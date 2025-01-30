// script.js

// Teachers table

async function fetchParticipants(roomName) {
  try {
      const response = await fetch(`/api/participants/${roomName}/`);
      // Verifica si la respuesta es válida
      // if (!response.ok) {
      //   throw new Error(`HTTP error! status: ${response.status}`);
      // }

      const data = await response.json();
      // console.log('Participants:', data.participants);
      return data.participants;
  } catch (error) {
      console.error('Error fetching participants:', error);
      return [];
  }
}

async function initParticipantsTable(roomName) {
  const participants = await fetchParticipants(roomName);
  const participantsTableBody = document.querySelector('#teachersTable tbody');

  // Limpiar la tabla antes de agregar nuevos datos (evita duplicados)
  participantsTableBody.innerHTML = '';

  // Añadir filas dinámicamente a la tabla
  participants.forEach(item => {
      const row = document.createElement('tr');
      row.innerHTML = `
          <td>${item.username}</td>
          <td>${item.first_name}</td>
          <td>${item.last_name}</td>
          <td>${item.email}</td>
      `;
      participantsTableBody.appendChild(row);
  });

  // Inicializar DataTables (asegurarse de que se inicializa después de agregar los datos)
  $('#participantsTable').DataTable({
      destroy: true,  // Para reinicializar si la tabla ya estaba activa
      columnDefs: [
          { targets: '_all', className: 'dt-center' },
      ],
  });
}


// Participants Table
document.addEventListener('DOMContentLoaded', () => {
  // Ejemplo de datos
  const participantsData = [
    {
      user: 'User1',
      name: 'Alberto',
      lastName: 'Lopez',
      email: 'alberto@um.es',
      date: 'Jul 1, 2024',
    },
    {
      user: 'User2',
      name: 'Juan',
      apellido: 'Perez',
      email: 'juan@um.es',
      date: 'Jul 8, 2024',
    },
    // ... más proyectos
  ];

  // Seleccionar el cuerpo de la tabla Profesores
  const participantsTableBody = document.querySelector(
    '#participantsTable tbody'
  );
  // Rellenar tabla
  // Añadir filas dinámicamente a la tabla Profesores
  participantsData.forEach((item) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${item.user}</td>
      <td>${item.name}</td>
      <td>${item.lastName}</td>
      <td>${item.email}</td>
    `;
    participantsTableBody.appendChild(row);
  });

  $(document).ready(function () {
    // Inicializar DataTables para Participantes
    $('#participantsTable').DataTable({
      columnDefs: [
        {
          targets: '_all',
          className: 'dt-center',
        },
      ],
    });
  });
});


// Cargar datos elementos/logs por participante
async function fetchElements(roomName) {
  try {
      const response = await fetch(`/api/elements/${roomName}/`);
      // Verifica si la respuesta es válida
      // if (!response.ok) {
      //   throw new Error(`HTTP error! status: ${response.status}`);
      // }

      const data = await response.json();
      console.log('Elements:', data.elements);
      return data.elements;
  } catch (error) {
      console.error('Error fetching participants:', error);
      return [];
  }
}

// Grafica de barras de movimientos por participante
async function initMovementsChart(roomName) {
  const elements = await fetchElements(roomName);

  const usernames = elements.map((item) => item.username);
  const movements = elements.map((item) => item.movement);
 
  // Selecciona el contenedor de la gráfica
  const movementsChart = document.getElementById('movementsChart');

  // Inicializa la gráfica con ECharts
  const chart = echarts.init(movementsChart);

  // Configuración de la gráfica
  const option = {
    xAxis: {
      type: 'category',
      data: usernames, // Eje X con nombres de usuario
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        data: movements, // Eje Y con valores de movement
        type: 'bar',
        showBackground: true,
        backgroundStyle: {
          color: 'rgba(180, 180, 180, 0.2)',
        },
      },
    ],
  };

  // Establece la opción y renderiza la gráfica
  chart.setOption(option);

  // Asegura que el gráfico sea responsivo
  window.addEventListener('resize', () => {
    chart.resize();
  });
  
}


// DIAGRAMA CIRCULAR % DE INTERACCIONES
async function initInteractionsChart(roomName) {
  const elements = await fetchElements(roomName);

  // Calcular el total de interacciones para obtener los porcentajes
  const totalInteractions = elements.reduce(
    (sum, element) => sum + element.interactions,
    0
  );

  // Construir los datos para la gráfica
  const chartData = elements.map((element) => ({
    value: ((element.interactions / totalInteractions) * 100).toFixed(2), // Porcentaje
    name: element.username, // Nombre del usuario
  }));

  // Selecciona el contenedor del gráfico
  const diagrama_interacciones = document.getElementById('diagrama_interacciones');

  // Inicializa el gráfico con ECharts
  const myChart = echarts.init(diagrama_interacciones);

  // Configuración del gráfico
  const option = {
    legend: {
      top: 'bottom',
    },
    toolbox: {
      show: true,
      feature: {
        mark: { show: true },
        dataView: { show: true, readOnly: false },
        restore: { show: true },
        saveAsImage: { show: true },
      },
    },
    series: [
      {
        name: 'Interactions diagram (%)',
        type: 'pie',
        radius: [30, 120],
        center: ['50%', '50%'],
        roseType: 'area',
        itemStyle: {
          borderRadius: 8,
        },
        data: chartData, // Datos dinámicos calculados
      },
    ],
  };

  // Renderiza el gráfico
  myChart.setOption(option);

  // Asegura que el gráfico sea responsivo
  window.addEventListener('resize', () => {
    myChart.resize();
  });
}



async function fetchTimelineData(roomName) {
  try {
    const response = await fetch(`/api/timeline/${roomName}/`);
    const data = await response.json();

    if (!data.dataTime || !data.delta_minutes) {
      console.error('Datos no válidos o incompletos desde la API');
      return { dataTime: {}, deltaMinutes: 0 };
    }

    return {
      dataTime: data.dataTime,
      deltaMinutes: data.delta_minutes,
      start_time: data.start_time,
    };
  } catch (error) {
    console.error('Error fetching timeline data:', error);
    return { dataTime: {}, deltaMinutes: 0 };
  }
}

async function initTimelineChart(roomName) {
  const { dataTime, deltaMinutes, start_time } = await fetchTimelineData(roomName);

  if (deltaMinutes === 0) {
    console.error('No se pudo generar la gráfica debido a datos insuficientes.');
    return;
  }

  // Contenedor de la gráfica
  const chartDom = document.getElementById('lineRaceChart');
  const myChart = echarts.init(chartDom);

  // Generar etiquetas de tiempo
  //const times = Array.from({ length: deltaMinutes }, (_, i) => `${i + 1} min`);
  const [startHour, startMinute] = start_time.split(':').map((v) => parseInt(v, 10));
  const times = Array.from({ length: deltaMinutes }, (_, i) => {
    const totalMinutes = startHour * 60 + startMinute + i;
    const currentHour = Math.floor(totalMinutes / 60);
    const currentMinute = totalMinutes % 60;
    return `${String(currentHour).padStart(2, '0')}:${String(currentMinute).padStart(2, '0')}`;
  });


  // Construir las series para la gráfica
  const users = Object.keys(dataTime);
  const seriesList = users.map((username) => {
    const userData = dataTime[username];
    const formattedData = times.map((time) => [time, userData[time] || 0]); // 0 si no hay datos

    return {
      type: 'line',
      name: username,
      showSymbol: false,
      smooth: true,
      emphasis: {
        focus: 'series',
      },
      data: formattedData,
    };
  });

  // Configuración de la gráfica
  const option = {
    animationDuration: 10000,
    title: {
      text: 'Rhythm of interaction by time',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      name: 'Time (min)',
      data: times, // Tiempo (minutos)
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      name: 'Nº interactions',
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
    },
    series: seriesList,
  };

  // Renderizar la gráfica
  myChart.setOption(option);

  // Asegurar que sea responsiva
  window.addEventListener('resize', () => {
    myChart.resize();
  });

  // Mostrar el delta en la consola
  console.log(`Duración total (delta): ${deltaMinutes} minutos`);
}

document.addEventListener('DOMContentLoaded', async () => {
  const roomName = document.getElementById('roomName').value; // ID del input oculto con el nombre de la sala
  await initParticipantsTable(roomName); // Inicializar la tabla
  await initMovementsChart(roomName);    // Inicializar la gráfica de movimientos
  await initInteractionsChart(roomName); // Inicializar la gráfica interacciones
  await initTimelineChart(roomName);     // Inicializar la gráfica de tiempo
});

//HEATMAP
document.addEventListener('DOMContentLoaded', () => {
  const chartDom = document.getElementById('heatmapChart');
  const myChart = echarts.init(chartDom);

  // Perlin Noise Helper
  function getNoiseHelper() {
    class Grad {
      constructor(x, y, z) {
        this.x = x;
        this.y = y;
        this.z = z;
      }
      dot2(x, y) {
        return this.x * x + this.y * y;
      }
    }
    const grad3 = [
      new Grad(1, 1, 0),
      new Grad(-1, 1, 0),
      new Grad(1, -1, 0),
      new Grad(-1, -1, 0),
      new Grad(1, 0, 1),
      new Grad(-1, 0, 1),
      new Grad(1, 0, -1),
      new Grad(-1, 0, -1),
    ];
    const p = [...Array(256)].map((_, i) => i).sort(() => Math.random() - 0.5);
    const perm = [...p, ...p];
    const gradP = perm.map((v) => grad3[v % 8]);

    function fade(t) {
      return t * t * t * (t * (t * 6 - 15) + 10);
    }
    function lerp(a, b, t) {
      return (1 - t) * a + t * b;
    }
    function perlin2(x, y) {
      const X = Math.floor(x) & 255;
      const Y = Math.floor(y) & 255;
      x -= Math.floor(x);
      y -= Math.floor(y);
      const u = fade(x);
      const v = fade(y);
      const n00 = gradP[X + perm[Y]].dot2(x, y);
      const n01 = gradP[X + perm[Y + 1]].dot2(x, y - 1);
      const n10 = gradP[X + 1 + perm[Y]].dot2(x - 1, y);
      const n11 = gradP[X + 1 + perm[Y + 1]].dot2(x - 1, y - 1);
      return lerp(lerp(n00, n10, u), lerp(n01, n11, u), v);
    }
    return { perlin2 };
  }

  const noise = getNoiseHelper();

  // Generar datos de Perlin Noise
  function generateData() {
    const data = [];
    for (let x = 0; x <= 200; x++) {
      for (let y = 0; y <= 100; y++) {
        data.push([x, y, noise.perlin2(x / 40, y / 20) + 0.5]);
      }
    }
    return data;
  }

  const data = generateData();

  // Configuración del Heatmap
  const option = {
    tooltip: {
      position: 'top',
      formatter: (params) => `Value: ${params.value[2].toFixed(2)}`,
    },
    xAxis: {
      type: 'value',
      splitLine: { show: false },
      axisLabel: { show: false },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      splitLine: { show: false },
      axisLabel: { show: false },
      axisTick: { show: false },
    },
    visualMap: {
      min: 0,
      max: 1,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 20,
      inRange: {
        color: [
          '#313695',
          '#4575b4',
          '#74add1',
          '#abd9e9',
          '#e0f3f8',
          '#ffffbf',
          '#fee090',
          '#fdae61',
          '#f46d43',
          '#d73027',
          '#a50026',
        ],
      },
    },
    series: [
      {
        name: 'Heatmap',
        type: 'heatmap',
        data: data,
        emphasis: {
          itemStyle: {
            borderColor: '#000',
            borderWidth: 1,
          },
        },
        progressive: 1000,
        animation: false,
      },
    ],
  };

  // Renderizar el Heatmap
  myChart.setOption(option);

  // Responsividad
  window.addEventListener('resize', () => {
    myChart.resize();
  });
});

// Tabla de elementos creados
document.addEventListener('DOMContentLoaded', () => {
  // Datos de ejemplo para la tabla
  const tableData = [
    {
      name: 'John',
      lastName: 'Doe',
      figures: 20,
      connectors: 15,
      draws: 5,
      text: 8,
      modifiedElements: 12,
    },
    {
      name: 'Jane',
      lastName: 'Smith',
      figures: 25,
      connectors: 10,
      draws: 7,
      text: 14,
      modifiedElements: 20,
    },
    {
      name: 'Michael',
      lastName: 'Johnson',
      figures: 30,
      connectors: 20,
      draws: 12,
      text: 10,
      modifiedElements: 25,
    },
    // Agrega más datos aquí
  ];

  // Seleccionar el cuerpo de la tabla
  const tableBody = document.querySelector('#elements-table tbody');

  // Añadir filas dinámicamente
  tableData.forEach((item) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${item.name}</td>
      <td>${item.lastName}</td>
      <td>${item.figures}</td>
      <td>${item.connectors}</td>
      <td>${item.draws}</td>
      <td>${item.text}</td>
      <td>${item.modifiedElements}</td>
    `;
    tableBody.appendChild(row);
  });

  // Inicializar DataTables
  $(document).ready(function () {
    $('#elements-table').DataTable({
      order: [], // Habilita la ordenación en todas las columnas
      columnDefs: [
        {
          targets: '_all', // Aplica el centrado a todas las columnas
          className: 'dt-center',
        },
        { orderable: true, targets: '_all' },
        { searchable: true, targets: '_all' },
      ],
    });
  });
});
