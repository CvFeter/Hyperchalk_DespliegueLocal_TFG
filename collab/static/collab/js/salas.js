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
    dataTable = $('#salas-table').DataTable({
        data: rooms,
        columns: [
            { data: 'room_name' },
            { 
                data: 'created_at',
                render: (data) => new Date(data).toLocaleString() // Formatea fecha
            },
            { 
                data: 'last_update',
                render: (data) => new Date(data).toLocaleString() // Formatea fecha
            }
        ],
        language: {
            url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/es-ES.json' // Traducción al español
        }
    });
}

window.addEventListener('load', async () => {
    await initDataTable();
});


// const data initDataTable = async () => {
//     if(dataTableInitialized){
//         dataTable.destroy();
//     }

//     await 
// }

// const list_salas = async () => {
//     try{
//         const response = await fetch("/list_salas/");
//         const data = await response.json();

//         let content = ``;
//         data.rooms.forEach(())
//     }
// }


// const data = {
//     "rooms": [
//         {
//             "room_name": "salaDePrueba1",
//             "created_at": "2025-01-10T00:39:00.177Z",
//             "last_update": "2025-01-10T00:39:00.177Z"
//         },
//         {
//             "room_name": "salaDePrueba2",
//             "created_at": "2025-01-10T00:39:13.778Z",
//             "last_update": "2025-01-10T01:42:20.104Z"
//         }
//     ]
// };

// // Función para generar la tabla
// function populateTable(data) {
//     const table = document.getElementById("salas-table").getElementsByTagName('tbody')[0];

//     // Recorre cada habitación del JSON
//     data.rooms.forEach(room => {
//         const row = table.insertRow();

//         const cell1 = row.insertCell(0);
//         const cell2 = row.insertCell(1);
//         const cell3 = row.insertCell(2);

//         cell1.textContent = room.room_name;
//         cell2.textContent = new Date(room.created_at).toLocaleString();
//         cell3.textContent = new Date(room.last_update).toLocaleString();
//     });
// }

// window.addEventListener('load', async () => {
//     populateTable(data);
// });
