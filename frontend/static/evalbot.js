// EvalBot Chart.js helpers

function createRadarChart(canvasId, labels, data) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  return new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Scores',
        data: data,
        backgroundColor: 'rgba(30, 58, 95, 0.2)',
        borderColor: '#f5a623',
        borderWidth: 2,
        pointBackgroundColor: '#f5a623',
        pointBorderColor: '#1e3a5f',
        pointRadius: 4,
      }]
    },
    options: {
      responsive: true,
      scales: {
        r: {
          beginAtZero: true,
          max: 10,
          ticks: { stepSize: 2, color: '#6b7280', font: { size: 10 } },
          grid: { color: 'rgba(107, 114, 128, 0.2)' },
          pointLabels: { color: '#1e3a5f', font: { size: 11, weight: 'bold' } }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function createDonutChart(canvasId, labels, data, colors) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: '#fff',
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { font: { size: 11 }, padding: 12 }
        }
      }
    }
  });
}

function createBarChart(canvasId, labels, data) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Score',
        data: data,
        backgroundColor: 'rgba(30, 58, 95, 0.8)',
        borderColor: '#1e3a5f',
        borderWidth: 1,
        borderRadius: 4,
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          grid: { color: 'rgba(107, 114, 128, 0.15)' },
          ticks: { color: '#6b7280' }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#374151', maxRotation: 45, font: { size: 10 } }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}
