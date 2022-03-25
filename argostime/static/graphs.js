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

var graphDivs = document.getElementsByClassName("graph");
for (var i = 0; i < graphDivs.length; i++) {
    var offer = graphDivs[i].id.substring(6);
    var graph = echarts.init(graphDivs[i]);

    var xhr = new XMLHttpRequest();
    xhr.addEventListener("load", function() {
        graph.setOption(JSON.parse(xhr.response));
    });
    xhr.open("GET", `/productoffer/${offer}/price_step_graph_data.json`);
    xhr.send();
}
