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
        setInterval(actualizarGrafica, 3000);
    }
    
    crearGrafica("miGrafica", "Nivel de Agua (%)", "54, 162, 235", "nivel_agua");
    crearGrafica("miGrafica2", "Nivel de Lluvia (%)", "255, 99, 132", "nivel_lluvia");

    // Actualizar datos en tiempo real
    function actualizarDatos() {
        fetch('/api/datos-actuales')
            .then(response => response.json())
            .then(data => {
                document.getElementById("water-level").innerHTML = data.waterlevel + "%";
                document.getElementById("water-probability").innerHTML = data.waterprobability;
                document.getElementById("rain-level").innerHTML = data.rainlevel + "%";
                document.getElementById("rain-intensity").innerHTML = data.rainintensity;
            })
            .catch(error => console.error("Error obteniendo datos:", error));
    }
    
    actualizarDatos();
    setInterval(actualizarDatos, 3000);

    // Actualizar tabla de registros históricos
    function actualizarTabla() {
        fetch('/api/table')
            .then(response => response.json())
            .then(data => {
                let tbody = document.getElementById("tabla-registros");
                tbody.innerHTML = ""; 
    
                data.forEach(registro => {
                    let fecha = new Date(registro.fecha).toLocaleString("es-MX", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit"
                    });
    
                    let fila = `
                        <tr>
                            <td>${fecha}</td>
                            <td>${registro.nivel_agua}%</td>
                            <td>${registro.nivel_lluvia}%</td>
                        </tr>
                    `;
                    tbody.innerHTML += fila; 
                });
            })
            .catch(error => console.error("Error actualizando la tabla:", error));
    }

    actualizarTabla();
    setInterval(actualizarTabla, 3000);
});