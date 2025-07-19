const MAX_BUF = 200;
let buffer = [];
let plotData = {
  Office: [],
  Kitchen: [],
  Closet: [],
  Bedroom: [],
  time: []
};

Plotly.newPlot('temp-plot', [
  {
    x: plotData.time,
    y: plotData.Office,
    mode: 'lines+markers',
    name: 'Office',
    line: { color: 'rgb(31, 119, 180)' }
  },
  {
    x: plotData.time,
    y: plotData.Kitchen,
    mode: 'lines+markers',
    name: 'Kitchen',
    line: { color: 'rgb(255, 127, 14)' }
  },
  {
    x: plotData.time,
    y: plotData.Closet,
    mode: 'lines+markers',
    name: 'Closet',
    line: { color: 'rgb(44, 160, 44)' }
  },
  {
    x: plotData.time,
    y: plotData.Bedroom,
    mode: 'lines+markers',
    name: 'Bedroom',
    line: { color: 'rgb(214, 39, 40)' }
  }
], {
  margin: { t: 30, r: 20, l: 60, b: 60 },
  legend: { orientation: 'h', y: 1.18 },
  xaxis: { title: 'Time', tickformat: "%H:%M:%S<br>%b %d" },
  yaxis: { title: 'Temperature (°F)' },
  hovermode: 'closest',
  plot_bgcolor: '#fff',
  paper_bgcolor: '#fff',
  font: { family: "Source Sans, sans-serif", size: 14, color: "#808495" }
}, {responsive: true});

// --- WebSocket Stuff ---
const ws = new WebSocket('wss://data.kevingrazel.com:6789');

ws.onopen = () => {
  document.getElementById('slider-min').textContent = 'Connected, waiting...';
};

ws.onerror = () => {
  document.getElementById('slider-min').textContent = 'WebSocket error';
};

ws.onclose = () => {
  document.getElementById('slider-min').textContent = 'WebSocket closed';
};

ws.onmessage = event => {
  let data = JSON.parse(event.data);

  // Defensive: If any field is missing, skip (optional)
  if (!data.timestamp || !data.sensor_data) return;

  buffer.push({
    timestamp: data.timestamp,
    Office: data.sensor_data.office_temp,
    Kitchen: data.sensor_data.kitchen_temp,
    Closet: data.sensor_data.closet_temp,
    Bedroom: data.sensor_data.bedroom_temp
  });
  if (buffer.length > MAX_BUF) buffer.shift();

  // For plotting, build arrays from buffer:
  plotData.time    = buffer.map(d => d.timestamp);
  plotData.Office  = buffer.map(d => d.Office);
  plotData.Kitchen = buffer.map(d => d.Kitchen);
  plotData.Closet  = buffer.map(d => d.Closet);
  plotData.Bedroom = buffer.map(d => d.Bedroom);

  Plotly.react('temp-plot', [
    { x: plotData.time, y: plotData.Office, mode: 'lines+markers', name: 'Office', line: { color: 'rgb(31, 119, 180)' } },
    { x: plotData.time, y: plotData.Kitchen, mode: 'lines+markers', name: 'Kitchen', line: { color: 'rgb(255, 127, 14)' } },
    { x: plotData.time, y: plotData.Closet, mode: 'lines+markers', name: 'Closet', line: { color: 'rgb(44, 160, 44)' } },
    { x: plotData.time, y: plotData.Bedroom, mode: 'lines+markers', name: 'Bedroom', line: { color: 'rgb(214, 39, 40)' } }
  ], {
    margin: { t: 30, r: 20, l: 60, b: 60 },
    legend: { orientation: 'h', y: 1.18 },
    xaxis: { title: 'Time', tickformat: "%H:%M:%S<br>%b %d" },
    yaxis: { title: 'Temperature (°F)' },
    hovermode: 'closest',
    plot_bgcolor: '#fff',
    paper_bgcolor: '#fff',
    font: { family: "Source Sans, sans-serif", size: 14, color: "#808495" }
  });

  updateOverlay(buffer.length - 1);
};

// Overlay update: expects index in buffer
function updateOverlay(idx) {
  idx = Number(idx);
  if (buffer.length === 0 || !buffer[idx]) {
    ['office-temp', 'kitchen-temp', 'closet-temp', 'bedroom-temp'].forEach(id => {
      document.getElementById(id).textContent = '--.-°F';
    });
    return;
  }
  const d = buffer[idx];
  document.getElementById("office-temp").textContent  = (d.Office !== undefined ? d.Office.toFixed(1) : "--.-") + "°F";
  document.getElementById("kitchen-temp").textContent = (d.Kitchen !== undefined ? d.Kitchen.toFixed(1) : "--.-") + "°F";
  document.getElementById("closet-temp").textContent  = (d.Closet !== undefined ? d.Closet.toFixed(1) : "--.-") + "°F";
  document.getElementById("bedroom-temp").textContent = (d.Bedroom !== undefined ? d.Bedroom.toFixed(1) : "--.-") + "°F";
}

// --- Plotly hover event to update overlay based on hovered point ---
const plotDiv = document.getElementById('temp-plot');
plotDiv.on('plotly_hover', function(eventData) {
  if (!eventData || !eventData.points || eventData.points.length === 0) return;
  const xVal = eventData.points[0].x;
  const idx = plotData.time.findIndex(t => t === xVal);
  if (idx !== -1) {
    updateOverlay(idx);
  }
});
plotDiv.on('plotly_unhover', function(eventData) {
  updateOverlay(buffer.length - 1);
});

function refreshData() {
  document.getElementById("slider-min").textContent = "Reconnect not implemented in static version.";
}
