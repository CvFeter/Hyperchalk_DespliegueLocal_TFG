import asyncio
import logging
import json
from typing import Literal
from urllib.parse import urlunsplit

from channels.db import database_sync_to_async
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import *

from draw.utils import absolute_reverse, async_get_object_or_404, make_room_name, reverse_with_query, validate_room_name
from draw.utils.auth import Unauthenticated, require_staff_user, user_is_authenticated, user_is_staff

from . import models as m
from .utils import get_or_create_room, room_access_check

#Importaciones adicionales
from django.http.response import JsonResponse
from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F, OuterRef, Count, Subquery

logger = logging.getLogger('draw.collab')


@database_sync_to_async
def get_username(user):
    return (user.first_name or user.username) if user.pk else _("Anonymous")


def reverse_ws_url(request: HttpRequest, route: Literal["replay", "collaborate"], room_name: str):
    return urlunsplit((
        'wss' if request.is_secure() else 'ws',
        request.get_host(),
        f'/ws/collab/{room_name}/{route}',
        None,
        None))


@database_sync_to_async
def get_file_dicts(room_obj: m.ExcalidrawRoom):
    return {f.element_file_id: f.to_excalidraw_file_schema().dict() for f in room_obj.files.all()}


@database_sync_to_async
def course_exists(room_obj: m.ExcalidrawRoom):
    return hasattr(room_obj, 'course')


def custom_messages():
    return {
        'NOT_LOGGED_IN': _("You need to be logged in."),
        'FILE_TOO_LARGE': _("The file you've added is too large."),
    }


async def index(request: HttpRequest, *args, **kwargs):
    if settings.SHOW_CREATE_ROOM_PAGE:
        # show the room creation page on GET
        if request.method == 'GET':
            return render(request, 'collab/index.html', {
                'imprint_url': settings.IMPRINT_URL,
            })

        # on POST, redirect to the room, after checking that it doesn't exist yet
        if (room_name := request.POST.get('roomname')):
            try:
                validate_room_name(room_name)
            except ValidationError:
                return render(request, 'collab/index.html', {
                    'imprint_url': settings.IMPRINT_URL,
                    'error_message': _(
                        '“%s” is not a valid room name. The room name must have between 10 and 24 characters. '
                        'The following characters are allowed: a-z, A-Z, 0-9, -, _'
                    ) % room_name })

            __, created = await get_or_create_room(room_name=room_name)
            if created:
                return redirect(absolute_reverse(request, 'collab:room', kwargs={'room_name': room_name}))
            else:
                return render(request, 'collab/index.html', {
                    'imprint_url': settings.IMPRINT_URL,
                    'error_message': _('The room name “%(room_name)s” is already taken.') % {'room_name': room_name}})

    # create a random room name if none is given
    if settings.ALLOW_AUTOMATIC_ROOM_CREATION:
        if settings.ALLOW_ANONYMOUS_VISITS or await user_is_authenticated(request.user):
            room_name = make_room_name(24)
            __, created = await get_or_create_room(room_name=room_name)
            if not created:
                # retry in the unlikely case that the room name is already taken
                return redirect(absolute_reverse(request, 'collab:index'))
            room_uri = reverse('collab:room', kwargs={'room_name': room_name})
            return redirect(request.build_absolute_uri(room_uri), permanent=False)
        else:
            return redirect(
                reverse_with_query('admin:login', query_kwargs={'next': f'/{make_room_name(24)}/'}))

    else:
        return HttpResponseBadRequest(_('Automatic room creation is disabled here. CODIGO MODIFICADO, Y RENOVADO HOT RELOAD'))


async def room(request: HttpRequest, room_name: str):
    validate_room_name(room_name)
    room_obj, username = await asyncio.gather(
        async_get_object_or_404(m.ExcalidrawRoom, room_name=room_name),
        get_username(request.user))

    try:
        await room_access_check(request, room_obj)
    except Unauthenticated:
        return redirect(reverse_with_query('admin:login', query_kwargs={'next': request.path}))

    is_lti_room, is_staff, file_dicts = await asyncio.gather(
        course_exists(room_obj),
        user_is_staff(request.user),
        get_file_dicts(room_obj))

    return render(request, 'collab/room.html', {
        'excalidraw_config': {
            'FILE_URL_TEMPLATE': absolute_reverse(request, 'api-1:put_file', kwargs={
                'room_name': room_name, 'file_id': 'FILE_ID'}),
            'BROADCAST_RESOLUTION_THROTTLE_MSEC': settings.BROADCAST_RESOLUTION_THROTTLE_MSEC,
            'ELEMENT_UPDATES_BEFORE_FULL_RESYNC': 100,
            'LANGUAGE_CODE': settings.LANGUAGE_CODE,
            'LIBRARY_RETURN_URL': absolute_reverse(request, 'collab:add-library'),
            'ROOM_NAME': room_name,
            'SAVE_ROOM_MAX_WAIT_MSEC': settings.SAVE_ROOM_MAX_WAIT_MSEC,
            'SHOW_QR_CODE': not is_lti_room,
            'SOCKET_URL': reverse_ws_url(request, "collaborate", room_name),
            'USER_NAME': username,
            'USER_IS_STAFF': is_staff,
        },
        'custom_messages': custom_messages(),
        'initial_elements': room_obj.elements,
        'files': file_dicts,
        'room': room_obj,
        'show_privacy_notice': not is_lti_room and room_obj.tracking_enabled
    })


@require_staff_user()
async def replay(request: HttpRequest, room_name: str, **kwargs):
    room_obj = await async_get_object_or_404(m.ExcalidrawRoom, room_name=room_name)
    return render(request, 'collab/room.html', {
        'excalidraw_config': {
            'FILE_URL_TEMPLATE': absolute_reverse(request, 'api-1:put_file', kwargs={
                'room_name': room_name, 'file_id': '{file_id}'}),
            'IS_REPLAY_MODE': True,
            'LANGUAGE_CODE': settings.LANGUAGE_CODE,
            'LIBRARY_RETURN_URL': absolute_reverse(request, 'collab:add-library'),
            'ROOM_NAME': room_name,
            'SOCKET_URL': reverse_ws_url(request, "replay", room_name),
        },
        'custom_messages': custom_messages(),
        'initial_elements': [],
        'files': await get_file_dicts(room_obj)
    })

def get_distinct_user_count():
    return Pseudonym.objects.values('user_id').distinct().count()


async def collab_stats(request: HttpRequest):
    nRooms = await database_sync_to_async(ExcalidrawRoom.objects.count)()
    nUsers = await database_sync_to_async(get_distinct_user_count)()
    nLogs = await database_sync_to_async(ExcalidrawLogRecord.objects.count)()
    return render(request, 'collab/estadisticas.html', {'nRooms': nRooms, 'nUsers' : nUsers, 'nLogs' : nLogs}) #puede que sea /estadisticas dado que no está metido en templates/collab

async def rooms(request: HttpRequest):
    return render(request, 'collab/salas.html')


@database_sync_to_async
def get_rooms():
    return list(ExcalidrawRoom.objects.values('room_name', 'created_at', 'last_update'))

async def list_salas(request):
    rooms = await get_rooms()
    return JsonResponse({'rooms': rooms})

@database_sync_to_async
def fetch_pseudonyms_with_users(room_name: str):
    # Realizamos una consulta manual para unir Pseudonym y CustomUser
    pseudonyms = Pseudonym.objects.filter(room__room_name=room_name).annotate(
        username=F('user__username'),
        first_name=F('user__first_name'),
        last_name=F('user__last_name'),
        email=F('user__email'),
        is_staff=F('user__is_staff'),
        is_superuser=F('user__is_superuser'),
    ).values(
        'user_id',
        'user_pseudonym',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_superuser'
    ).filter(is_superuser=False)  # No mostrar superusuarios
    return list(pseudonyms)

async def get_users_pseudonym(request, room_name: str):
    # Obtenemos la lista de pseudónimos con la información de los usuarios
    pseudonym_list = await fetch_pseudonyms_with_users(room_name)
    
    # Construimos el resultado directamente desde la lista serializada
    participants = [
        {
            'user_id': str(p['user_id']),  # Convertir UUID a string
            'pseudonimo': p['user_pseudonym'],
            'username': p['username'],
            'first_name': p['first_name'],
            'last_name': p['last_name'],
            'email': p['email'],
            'is_staff': p['is_staff'],
        }
        for p in pseudonym_list
    ]

    return JsonResponse({'participants': participants}, safe=False)


@database_sync_to_async
def fetch_user_logs(room_name: str):
    logs = Pseudonym.objects.filter(room__room_name=room_name).annotate(
        movement=Subquery(
            ExcalidrawLogRecord.objects.filter(
                user_pseudonym=OuterRef('user_pseudonym'),  
                room_name=room_name,
                event_type='collaborator_change'
            )
            .values('user_pseudonym')  
            .annotate(movement_count=Count('id'))
            .values('movement_count')
        ),
        interactions=Subquery(
            ExcalidrawLogRecord.objects.filter(
                user_pseudonym=OuterRef('user_pseudonym'),
                room_name=room_name
            )
            .values('user_pseudonym')
            .annotate(interactions_count=Count('id'))
            .values('interactions_count')
        )
    ).values(
        'user__username',  
        'user__first_name',  
        'user__last_name',
        'user__is_superuser',  
        'movement',
        'interactions'
    ).filter(user__is_superuser=False)

    return list(logs)

async def get_elements(request, room_name: str):
        # Obtenemos la lista de usuarios con movimientos
        user_movements = await fetch_user_logs(room_name)
        
        # Construimos el JSON de respuesta
        response_data = [
            {
                'username': user['user__username'],
                'first_name': user['user__first_name'],
                'last_name': user['user__last_name'],
                'movement': user['movement'] if user['movement'] is not None else 0,
                'interactions': user['interactions'] if user['interactions'] is not None else 0
            }
            for user in user_movements
        ]

        return JsonResponse({'elements': response_data}, safe=False)


async def room_stats(request: HttpRequest, room_name: str):
    
    validate_room_name(room_name)
    room_obj, username = await asyncio.gather(
        async_get_object_or_404(m.ExcalidrawRoom, room_name=room_name),
        get_username(request.user))
    
    # logs = await get_logs(room_name) #logs de la sala
    
    #participants = await get_users_pseudonym(request, room_name) #usado para obtener los participantes de la sala
    # nParticipants = sum(1 for p in participants if p['is_staff'])
    nParticipants = await database_sync_to_async(Pseudonym.objects.filter(room_id=room_name).values('user_id').distinct().count)() 
    nLogs = await database_sync_to_async(ExcalidrawLogRecord.objects.filter(room_name=room_name).count)()

    #participants_serialized = json.dumps(participants, cls=DjangoJSONEncoder)
    # return render(request, 'collab/dashboard.html', {'room': room_obj, 'nParticipants': nParticipants, 'nLogs': nLogs})
    return render(request, 'collab/dashboard.html', 
        {
            'room': room_obj,
            'nParticipants': nParticipants,
            'nLogs': nLogs,
            #'participants': participants.content
            #'participants': participants_serialized
        }
    )

