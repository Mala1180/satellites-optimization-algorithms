let chart;


window.onload = function () {
    const select = document.getElementById("select-instances");
    $.get('http://localhost:3000/instances', (data) => {
        console.log(data);
        data.forEach(instance => {
            $("#select-instances").append(`<option value="${instance}">${instance}</option>`);
        });
        getInstance(data[0]);
    });

    select.onchange = function () {
        const instanceName = select.value;
        getInstance(instanceName);
    };
}


function getInstance(name) {
    const ctx = document.getElementById('myChart').getContext('2d');
    let dtos = [];
    if (chart) {
        chart.destroy();
    }
    $.ajax({
        type: 'GET',
        url: `http://localhost:3000/instances/${name}/dtos`,
        dataType: 'json'
    }).done(function (result) {
        dtos = result;
        const dataset = [];
        const dtoLength = dtos.length;
        dtos = dtos.slice(0, dtoLength);

        dtos.forEach(function (dto) {
            // multiplied by 1000 so that the argument is in milliseconds, not seconds.
            const start = new Date(dto.start_time * 1000).getTime();
            const stop = new Date(dto.stop_time * 1000).getTime();
            dataset.push([start, stop]);
        });

        const colors = [];
        for (let i = 0; i < dtoLength; i++) {
            colors.push(getRandomColor());
        }

        // setup 
        const data = {
            labels: dtos.map((dto) => dto.id),
            datasets: [{
                data: dataset,
                backgroundColor: colors,
                borderColor: colors,
                // barPercentage: 0.7,
                barThickness: 3,
            }]
        };
        const startTime = dtos.map(dto => new Date(dto.start_time * 1000).getTime()).reduce((a, b) => Math.min(a, b))
        document.getElementById("start-date").textContent = `Start of the plan: ${new Date(startTime).toLocaleString()}`;
        // config 
        const config = {
            type: 'bar',
            data,
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: 'DTOs - Timeline'
                    },
                    legend: {
                        display: false
                    },
                },
                indexAxis: 'y',
                scales: {
                    x: {
                        min: startTime,
                        type: 'time'
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        };

        chart = new Chart(ctx, config);
    });

}

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}
