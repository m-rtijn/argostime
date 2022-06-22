/*
graphs.js

Graph data retreival and rendering

Copyright (c) 2022 Kevin <kevin [at] 2sk.nl>

This file is part of Argostimè.

Argostimè is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Argostimè is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Argostimè. If not, see <https://www.gnu.org/licenses/>.
*/

function tooltipFormatter(object) {
    var date = new Date(object[0].data[0]).toISOString().split("T")[0];
    var price = object[0].data[1].toFixed(2);
    return `<center>${date}<br>€ ${price}</center>`;
}

function yFormatter(value) {
    var price = value.toFixed(2);
    return `€ ${price}`
}

var defaultOptions = {
    tooltip: {
        trigger: "axis",
        formatter: tooltipFormatter,
        textStyle: {
            color: "#000",
            fontSize: 18,
        },
    },
    toolbox: {
        iconStyle: {
            borderColor: "#000",
        },
        feature: {
            dataZoom: {
                yAxisIndex: "none",
            },
        },
    },
    dataZoom: [
        {
            type: "inside",
            filterMode: "none",
            start: 0,
            end: 100,
        },
        {
            start: 0,
            end: 100,
        },
    ],
    yAxis: {
        type: "value",
        min: "dataMin",
        max: "dataMax",
        axisLabel: {
            formatter: yFormatter,
            color: "#000",
            fontSize: 18,
        },
    },
    xAxis: {
        type: "time",
        axisLabel: {
            formatter: "{yyyy}-{MM}-{dd}",
            color: "#000",
            fontSize: 18,
        },
    },
};

var graphDivs = document.getElementsByClassName("graph");
var r = document.querySelector(':root');
r.style.setProperty('--vw', document.documentElement.clientWidth);
for (var i = 0; i < graphDivs.length; i++) {
    (function () {
        var offer = graphDivs[i].id.substring(6);
        var graph = echarts.init(graphDivs[i]);

        var xhr = new XMLHttpRequest();
        xhr.addEventListener("load", function() {
            graph.setOption(Object.assign({}, defaultOptions, JSON.parse(xhr.response)));
        });
        xhr.open("GET", `/productoffer/${offer}/price_step_graph_data.json`);
        xhr.send();

        window.addEventListener('resize', function(event) {
            r.style.setProperty('--vw', document.documentElement.clientWidth);
        }, true);
    }());
}
