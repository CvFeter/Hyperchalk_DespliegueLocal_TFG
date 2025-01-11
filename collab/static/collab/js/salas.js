let dataTable;

async function fetchRooms() {
    try {
        const response = await fetch('/list_salas/');
        const data = await response.json();
        return data.rooms;
    } catch (error) {
        console.error('Error fetching rooms:', error);
        return [];
    }
}

async function initDataTable() {
    const rooms = await fetchRooms();

    // Inicializa DataTable
    dataTable = $('#datatable-rooms').DataTable({
        data: rooms,
        columnDefs: [
            { className: "centered", targets: '_all'},
            { orderable: false, targets: [3] },
            { searchable: true, targets: '_all' }
        ],
        columns: [
            { data: 'room_name' },
            { 
                data: 'created_at',
                render: (data) => new Date(data).toLocaleString() // Formatea fecha
            },
            { 
                data: 'last_update',
                render: (data) => new Date(data).toLocaleString() // Formatea fecha
            },
            {
                data: null,
                render: () => '<button class="btn btn-primary">Ingresar</button>',
                className: 'text-center'

            }
        ],
        language: {
            url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/es-ES.json' // Traducción al español
        },
    });
}

window.addEventListener('load', async () => {
    await initDataTable();
});