from django import template
from ..models import Pseudonym

register = template.Library()

@register.filter
def pseudonyms_por_sala(room_id_):
    return Pseudonym.objects.filter(room_id=room_id_).count()