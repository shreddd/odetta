margin = {
    top: 20,
    right: 50,
    bottom: 20,
    left: 50
};

width = 1000 - margin.left - margin.right;
height = 500 - margin.top - margin.bottom;

var x = d3.scale.linear()
.domain([0,24000])
            .range([0, width]); //X-Scale
            var y = d3.scale.linear()
            .domain([0,8e+39])
            .range([height, 0]); //y-Scale

            var line = d3.svg.line()
            .x(function (d) {
                return x(d.wavelength);
            })
            .y(function (d) {
                return y(d.lum);
            });

            var zoom = d3.behavior.zoom()
            .x(x)
            .y(y)
            .on("zoom", function(){
                if(d3.event.sourceEvent.which!=3){
                    refresh();
                }
            });
            var zoomRect = true;
            svg = d3.select('.graph')
            .append("svg:svg")
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append("svg:g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
            .call(zoom)
            .append("g")
            .on("mouseup", function(){
                d3.select('body').style("cursor", null);
            })
            .on("mousedown", function() {
                d3.select('body').style("cursor", "move");
                if (d3.event.which != 3) return;
                var e = this,
                origin = d3.mouse(e),
                rect = svg.append("rect").attr("class", "zoom");
                d3.select("body").classed("noselect", true);
                origin[0] = Math.max(0, Math.min(width, origin[0]));
                origin[1] = Math.max(0, Math.min(height, origin[1]));
                d3.select(window)
                .on("mousemove.zoomRect", function() {
                    var m = d3.mouse(e);
                    m[0] = Math.max(0, Math.min(width, m[0]));
                    m[1] = Math.max(0, Math.min(height, m[1]));
                    rect.attr("x", Math.min(origin[0], m[0]))
                    .attr("y", Math.min(origin[1], m[1]))
                    .attr("width", Math.abs(m[0] - origin[0]))
                    .attr("height", Math.abs(m[1] - origin[1]));
                })
                .on("mouseup.zoomRect", function() {
                    d3.select(window).on("mousemove.zoomRect", null).on("mouseup.zoomRect", null);
                    d3.select("body").classed("noselect", false);
                    var m = d3.mouse(e);
                    m[0] = Math.max(0, Math.min(width, m[0]));
                    m[1] = Math.max(0, Math.min(height, m[1]));
                    if (m[0] !== origin[0] && m[1] !== origin[1]) {
                        zoom.x(x.domain([origin[0], m[0]].map(x.invert).sort(function(a,b){return a > b;})))
                        .y(y.domain([origin[1], m[1]].map(y.invert).sort(function(a,b){return a > b;})));
                    }
                    rect.remove();
                    refresh();
                }, true);
                d3.event.stopPropagation();
            });

svg.append("svg:rect")
.attr("width", width)
.attr("height", height)
.attr("class", "plot");

var make_x_axis = function () {
    return d3.svg.axis()
    .scale(x)
    .orient("bottom");
};

var make_y_axis = function () {
    return d3.svg.axis()
    .scale(y)
    .orient("left");
};

var xAxis = d3.svg.axis()
.scale(x)
.orient("bottom");

svg.append("svg:g")
.attr("class", "x axis")
.attr("transform", "translate(0, " + height + ")")
.call(xAxis);

var yAxis = d3.svg.axis()
.scale(y)
.orient("left")
.tickFormat(function(d){
    return d.toExponential(1);
});

svg.append("g")
.attr("class", "y axis")
.call(yAxis);

svg.append("g")
.attr("class", "x grid")
.attr("transform", "translate(0," + height + ")")
.call(make_x_axis()
    .tickSize(-height, 0, 0)
    .tickFormat(""));

svg.append("g")
.attr("class", "y grid")
.call(make_y_axis()
    .tickSize(-width, 0, 0)
    .tickFormat(""));

var clip = svg.append("svg:clipPath")
.attr("id", "clip")
.append("svg:rect")
.attr("x", 0)
.attr("y", 0)
.attr("width", width)
.attr("height", height);

var chartBody = svg.append("g")
.attr("clip-path", "url(#clip)");


var circlesLayer = chartBody.append("g")
.attr("id","circles")

function graphData(data){
    if(clearData){
        chartBody.selectAll(".line").remove();         
    }
    chartBody.append("svg:path")
    .datum(data)
    .attr("class", "line")
    .attr("d", line);   
    refresh();         
}

function refresh() {
    svg.select(".x.axis").call(xAxis);
    svg.select(".y.axis").call(yAxis);
    svg.select(".x.grid")
    .call(make_x_axis()
        .tickSize(-height, 0, 0)
        .tickFormat(""));
    svg.select(".y.grid")
    .call(make_y_axis()
        .tickSize(-width, 0, 0)
        .tickFormat(""));
    svg.selectAll(".line")
    .attr("class", "line")
    .attr("d", line);
}

function restoreScale(){
    zoom.x(x.domain(d3.extent(frameData[currFrame], function (d) {
        return d.wavelength;
    }))
    .range([0, width]))
    .y(y.domain(d3.extent(frameData[currFrame], function (d) {
        return d.lum;
    }))
    .range([height, 0]));
    refresh();
}

function showCircles(){
    var circles = circlesLayer.selectAll("circle")
    .data(flux_data);

    circles.enter()
    .append("circle")
    .attr("r",3)
    .attr("stroke","black")
    .attr("stroke-width","1px")
    .attr("fill","teal")
    .attr("cx",function(d){
        return x(d.wavelength);
    })
    .attr("cy",function(d){
        return y(d.lum);
    });

    circles.attr("cx",function(d){
        return x(d.wavelength);
    })
    .attr("cy",function(d){
        return y(d.lum);
    });
}

var currFrame = 0;
var frameData = [];
var clearData = true;
var animation;
var rescale = false;

function runAnimation(start, end, speed){
    if(animation){
        animation = clearInterval(animation);
    }
    currFrame = start;
    animation = setInterval(getNextFrame, speed)
}

function getNextFrame(){
    getData(++currFrame);
}

function preloadData(start,end){
    for(var x=start; x<end; x++){
        d3.json("/ajax/plot/"+m_id+"/"+x+"/", function(error, data){
            if (error){
                console.log(error);
            }else{
                frameData[data.frame] = data.flux_data;
            }
        });
    }
}

function moveFrame(frames){
    currFrame+=frames;
    getData(currFrame);
    $("#frame-slider").slider("option", "value", currFrame);
}

function getData(frame){            
    if(frameData[frame]){
        graphData(frameData[frame]);
        currFrame = frame;
        if(rescale){
            restoreScale();
        }              
    }else{
        d3.json("/ajax/plot/"+m_id+"/"+frame+"/", function(error, data){
            if (error){
                alert(error);
                if(animation){
                    animation = clearInterval(animation);
                }
            }else{
                frameData[data.frame] = data.flux_data;
                graphData(data.flux_data);
                currFrame = frame;
                if(rescale){
                    restoreScale();
                }  
            }
        });
    }
}