document.addEventListener("DOMContentLoaded", function () {
    // Formatear fechas
    document.querySelectorAll(".fecha-registro").forEach(function (element) {
        let fechaOriginal = element.textContent.trim();
        if (fechaOriginal) {
            let fecha = new Date(fechaOriginal);
            let fechaFormateada = fecha.toLocaleString("es-MX", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit"
            });
            element.textContent = fechaFormateada;
        }
    });

    // Función para crear gráficas
    function crearGrafica(canvasId, label, color, dataKey) {
        let ctx = document.getElementById(canvasId).getContext("2d");

        let datos = {
            labels: [],
            datasets: [{
                label: label,
                backgroundColor: `rgba(${color}, 0.5)`,
                borderColor: `rgba(${color}, 1)`,
                borderWidth: 2,
                data: []
            }]
        };

        let config = {
            type: "line",
            data: datos,
            options: {
                responsive: true,
                scales: {
                    x: { title: { display: true, text: "Hora" } },
                    y: { title: { display: true, text: label }, min: 0, max: 100 }
                }
            }
        };

        let grafica = new Chart(ctx, config);

        function cargarDatosHistoricos() {
            fetch("/api/table")
                .then(response => response.json())
                .then(data => {
                    data.reverse();
                    datos.labels = data.map(d => new Date(d.fecha).toLocaleTimeString("es-MX", {
                        hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: true
                    }));
                    datos.datasets[0].data = data.map(d => d[dataKey]);
                    grafica.update();
                })
                .catch(error => console.error("Error obteniendo datos históricos:", error));
        }

        function actualizarGrafica() {
            fetch("/api/table")
                .then(response => response.json())
                .then(data => {
                    data.reverse();
                    let nuevoDato = data[data.length - 1];

                    if (!nuevoDato.fecha || nuevoDato[dataKey] === undefined) {
                        console.error("Dato incorrecto:", nuevoDato);
                        return;
                    }

                    if (datos.labels.length >= 6) {
                        datos.labels.shift();
                        datos.datasets[0].data.shift();
                    }

                    datos.labels.push(new Date(nuevoDato.fecha).toLocaleTimeString("es-MX", {
                        hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: true
                    }));
                    datos.datasets[0].data.push(nuevoDato[dataKey]);

                    grafica.update();
                })
                .catch(error => console.error("Error obteniendo datos:", error));
        }

        cargarDatosHistoricos();
        setInterval(actualizarGrafica, 4000);
    }

    crearGrafica("miGrafica", "Nivel de Agua (%)", "54, 162, 235", "nivel_agua");
    crearGrafica("miGrafica2", "Nivel de Lluvia (%)", "255, 99, 132", "nivel_lluvia");

    // Variables para el caché
    let cacheDatosActuales = null;
    let cacheHistoricos = null;
    let lastUpdate = 0;
    const CACHE_TIME = 5000; // 5 segundos

    function actualizarTarjetasYTabla() {
        const now = Date.now();

        // Solo actualizar si ha pasado el tiempo de caché
        if (now - lastUpdate >= CACHE_TIME) {
            console.log('Actualizando datos...');

            // Actualizar tarjetas
            fetch("/api/datos-actuales")
                .then(response => response.json())
                .then(datos => {
                    cacheDatosActuales = datos;
                    actualizarTarjetas(datos);
                })
                .catch(error => console.error("Error actualizando tarjetas:", error));

            // Actualizar tabla
            fetch("/api/table")
                .then(response => response.json())
                .then(datos => {
                    cacheHistoricos = datos;
                    actualizarTabla(datos);
                })
                .catch(error => console.error("Error actualizando tabla:", error));

            lastUpdate = now;
        } else {
            // Usar datos en caché
            if (cacheDatosActuales) actualizarTarjetas(cacheDatosActuales);
            if (cacheHistoricos) actualizarTabla(cacheHistoricos);
        }
    }

    function actualizarTarjetas(datos) {
        // Actualizar tarjeta de Posibilidades de Desbordamiento
        const desbordamientoNumber = document.querySelector('.stats-card:nth-child(1) .stats-number');
        const desbordamientoText = document.querySelector('.stats-card:nth-child(1) .stats-text');

        if (desbordamientoNumber && desbordamientoText) {
            desbordamientoNumber.textContent = datos.waterlevel ? `${datos.waterlevel}%` : 'N/A';
            desbordamientoText.textContent = datos.waterprobability || 'N/A';
        }

        // Actualizar tarjeta de Intensidad de Lluvia
        const lluviaNumber = document.querySelector('.stats-card:nth-child(2) .stats-number');
        const lluviaText = document.querySelector('.stats-card:nth-child(2) .stats-text');

        if (lluviaNumber && lluviaText) {
            lluviaNumber.textContent = datos.rainlevel ? `${datos.rainlevel}%` : 'N/A';
            lluviaText.textContent = datos.rainintensity || 'N/A';
        }
    }

    function actualizarTabla(datos) {
        const tbody = document.querySelector('.table tbody');
        if (tbody && Array.isArray(datos) && datos.length > 0) {
            tbody.innerHTML = '';
            datos.forEach(registro => {
                const tr = document.createElement('tr');
                const fecha = new Date(registro.fecha);
                const fechaFormateada = fecha.toLocaleString("es-MX", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit"
                });

                tr.innerHTML = `
                    <td class="fecha-registro">${fechaFormateada}</td>
                    <td>${registro.nivel_agua || 'N/A'}%</td>
                    <td>${registro.nivel_lluvia || 'N/A'}%</td>
                `;
                tbody.appendChild(tr);
            });
        }
    }

    // Iniciar actualización
    actualizarTarjetasYTabla();
    setInterval(actualizarTarjetasYTabla, 5000);


    // Función grafica combinada
    const botonFiltrar = document.getElementById("boton-filtrar");
    const ctx = document.getElementById("miGrafica3").getContext("2d");
    let grafica;

    // Función para formato yyyy-mm-dd
    const toInputFormat = (fecha) => fecha.toISOString().split("T")[0];

    // Fechas predeterminadas
    const hoy = new Date();
    const hace7dias = new Date();
    hace7dias.setDate(hoy.getDate() - 7);

    const inicioInput = document.getElementById("fecha-inicio");
    const finInput = document.getElementById("fecha-fin");

    // Asignar valores predeterminados
    inicioInput.value = toInputFormat(hace7dias);
    finInput.value = toInputFormat(hoy);

    // Limitar selección al día actual como máximo
    const hoyStr = toInputFormat(hoy);
    inicioInput.max = hoyStr;
    finInput.max = hoyStr;

    // (máximo 28 días)
    inicioInput.addEventListener("change", () => {
        const inicio = new Date(inicioInput.value);
        const maxFin = new Date(inicio);
        maxFin.setDate(inicio.getDate() + 28);
        finInput.max = toInputFormat(maxFin);

        // evitar fechas futuras
        if (finInput.max > hoyStr) {
            finInput.max = hoyStr;
        }
    });

    finInput.addEventListener("change", () => {
        const fin = new Date(finInput.value);
        const minInicio = new Date(fin);
        minInicio.setDate(fin.getDate() - 28);
        inicioInput.min = toInputFormat(minInicio);
    });

    // Ejecutar filtrado al cargar
    botonFiltrar.click();

    botonFiltrar.addEventListener("click", async () => {
        const inicio = new Date(inicioInput.value);
        const fin = new Date(finInput.value);

        if (!inicio || !fin || (fin - inicio > 28 * 24 * 60 * 60 * 1000)) {
            alert("Selecciona fechas válidas (máx. 28 días).");
            return;
        }

        try {
            const res = await fetch("/api/tablee");
            const data = await res.json();

            const filtrados = data.filter((registro) => {
                const fecha = new Date(registro.fecha);
                return fecha >= inicio && fecha <= fin;
            });

            const fechas = filtrados.map((r) => new Date(r.fecha).toLocaleDateString());
            const agua = filtrados.map((r) => r.nivel_agua);
            const lluvia = filtrados.map((r) => r.nivel_lluvia);

            if (grafica) {
                grafica.destroy();
            }

            grafica = new Chart(ctx, {
                type: "line",
                data: {
                    labels: fechas,
                    datasets: [
                        {
                            label: "Nivel de Agua (%)",
                            data: agua,
                            borderColor: "rgba(54, 162, 235, 1)",
                            backgroundColor: "rgba(54, 162, 235, 0.2)",
                            fill: false,
                            tension: 0.1
                        },
                        {
                            label: "Nivel de Lluvia (%)",
                            data: lluvia,
                            borderColor: "rgba(255, 99, 132, 1)",
                            backgroundColor: "rgba(255, 99, 132, 0.2)",
                            fill: false,
                            tension: 0.1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: "Fecha"
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Nivel (%)"
                            },
                            ticks: {
                                callback: function (value) {
                                    return value + "%";
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error al obtener o graficar los datos:", error);
        }
    });



});
