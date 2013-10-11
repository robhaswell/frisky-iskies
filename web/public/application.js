jQuery(window).ready(function($) {
    var ctx = $("#chart").get(0).getContext("2d");
    var chart = new Chart(ctx);

    $("#select-item a[data-item-id]").click(function() {
        var $this = $(this);
        var id = $this.data("item-id");
        $.post('/', {
            action: "data",
            id: id,
        }, function(data) {
            var chartData = {
                labels: [],
                datasets: [
                    {
                        strokeColor : "rgba(0,0,255,1)",
                        data : [],
                    },
                    {
                        strokeColor : "rgba(0,128,255,1)",
                        data : [],
                    },
                    {
                        strokeColor : "rgba(255,0,0,1)",
                        data : [],
                    },
                    {
                        strokeColor : "rgba(255,128,0,1)",
                        data : [],
                    },
                ]
            };
            var options = {
                datasetFill: false,
                pointDot: false,
            };
            $(data).each(function(i, row) {
                chartData.labels.push(new Date(row.timestamp).
                    toString("dddd, MMMM"));
                chartData.datasets[0].data.push(row.jita_sell);
                chartData.datasets[1].data.push(row.jita_buy);
                chartData.datasets[2].data.push(row.amarr_sell);
                chartData.datasets[3].data.push(row.amarr_buy);
            });
            chart.Line(chartData, options);
        }, "json")
        /*
        TODO: Send JSON application headers and remove this format indicator.
        */
    });
});
