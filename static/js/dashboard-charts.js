// Dashboard Charts with Chart.js
// Fetches data from /api/dashboard-data/ and renders 2 charts

document.addEventListener('DOMContentLoaded', function () {
    // Elementos del DOM
    const ingresosCanvas = document.getElementById('ingresosChart');
    const citasCanvas = document.getElementById('citasChart');

    // Verificar que los canvas existen
    if (!ingresosCanvas || !citasCanvas) {
        console.log('Canvas elements not found - dashboard charts disabled');
        return;
    }

    // Detectar tema actual
    function getCurrentTheme() {
        return document.documentElement.getAttribute('data-bs-theme') || 'light';
    }

    // Colores según tema
    function getColors() {
        const theme = getCurrentTheme();
        const isDark = theme === 'dark';

        return {
            gridColor: isDark ? '#444' : '#e0e0e0',
            textColor: isDark ? '#ccc' : '#666',
            backgroundColor: isDark ? 'transparent' : 'white'
        };
    }

    // Fetch data from API
    fetch('/api/dashboard-data/')
        .then(response => response.json())
        .then(data => {
            const colors = getColors();

            // Gráfico 1: Ingresos Mensuales (Line Chart)
            const ingresosChart = new Chart(ingresosCanvas, {
                type: 'line',
                data: {
                    labels: data.ingresos_mensuales.labels,
                    datasets: [{
                        label: 'Ingresos (CLP)',
                        data: data.ingresos_mensuales.data,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.3,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: true,
                            labels: {
                                color: colors.textColor
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    let label = context.dataset.label || '';
                                    if (label) {
                                        label += ': ';
                                    }
                                    label += '$' + context.parsed.y.toLocaleString('es-CL');
                                    return label;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: colors.textColor,
                                callback: function (value) {
                                    return '$' + value.toLocaleString('es-CL');
                                }
                            },
                            grid: {
                                color: colors.gridColor
                            }
                        },
                        x: {
                            ticks: {
                                color: colors.textColor
                            },
                            grid: {
                                color: colors.gridColor
                            }
                        }
                    }
                }
            });

            // Gráfico 2: Citas por Mes (Bar Chart Agrupado)
            const citasChart = new Chart(citasCanvas, {
                type: 'bar',
                data: {
                    labels: data.citas_por_mes.labels,
                    datasets: [
                        {
                            label: 'Agendadas',
                            data: data.citas_por_mes.agendadas,
                            backgroundColor: 'rgba(54, 162, 235, 0.7)',
                            borderColor: 'rgb(54, 162, 235)',
                            borderWidth: 1
                        },
                        {
                            label: 'Realizadas',
                            data: data.citas_por_mes.realizadas,
                            backgroundColor: 'rgba(75, 192, 192, 0.7)',
                            borderColor: 'rgb(75, 192, 192)',
                            borderWidth: 1
                        },
                        {
                            label: 'Canceladas',
                            data: data.citas_por_mes.canceladas,
                            backgroundColor: 'rgba(255, 99, 132, 0.7)',
                            borderColor: 'rgb(255, 99, 132)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: true,
                            labels: {
                                color: colors.textColor
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: colors.textColor,
                                stepSize: 1
                            },
                            grid: {
                                color: colors.gridColor
                            }
                        },
                        x: {
                            ticks: {
                                color: colors.textColor
                            },
                            grid: {
                                color: colors.gridColor
                            }
                        }
                    }
                }
            });

            // Actualizar colores cuando cambie el tema
            const themeToggle = document.getElementById('theme-toggle');
            if (themeToggle) {
                themeToggle.addEventListener('click', function () {
                    setTimeout(() => {
                        const newColors = getColors();

                        // Actualizar gráfico de ingresos
                        ingresosChart.options.plugins.legend.labels.color = newColors.textColor;
                        ingresosChart.options.scales.y.ticks.color = newColors.textColor;
                        ingresosChart.options.scales.y.grid.color = newColors.gridColor;
                        ingresosChart.options.scales.x.ticks.color = newColors.textColor;
                        ingresosChart.options.scales.x.grid.color = newColors.gridColor;
                        ingresosChart.update();

                        // Actualizar gráfico de citas
                        citasChart.options.plugins.legend.labels.color = newColors.textColor;
                        citasChart.options.scales.y.ticks.color = newColors.textColor;
                        citasChart.options.scales.y.grid.color = newColors.gridColor;
                        citasChart.options.scales.x.ticks.color = newColors.textColor;
                        citasChart.options.scales.x.grid.color = newColors.gridColor;
                        citasChart.update();
                    }, 50); // Pequeño delay para que el tema cambie primero
                });
            }
        })
        .catch(error => {
            console.error('Error loading dashboard data:', error);
        });
});
