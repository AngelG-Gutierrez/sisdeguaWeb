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
});