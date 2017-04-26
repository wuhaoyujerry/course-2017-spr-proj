<!DOCTYPE html>

<style>

.point {
  fill: #000;
  fill-opacity: 0.4;
}

.point--scanned {
  fill: orange;
  fill-opacity: 1;
  stroke: orange;
  stroke-width: 3px;
}

.point--selected {
  fill: red;
  fill-opacity: 1;
  stroke: red;
  stroke-width: 5px;
}

.node {
  fill: none;
  stroke: #ccc;
  shape-rendering: crispEdges;
}

</style>
<svg width="960" height="500"></svg>
<script src="https://d3js.org/d3.v4.min.js"></script>
<script>

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height"),
    selected;

/*
$.ajax({
  type: "POST",
  url: "./transformation_one_bus.py",
  data: {param: text}
}).done(function(o) {
   
});
*/

var random = Math.random,
    //data = d3.range(2500).map(function() { return [random() * width, random() * height]; });
    data = d3.map([]) //points already in array, figure out scale and how to get data here. 

var quadtree = d3.quadtree() //find a way to make this the rtree we already have
    .extent([[-1, -1], [width + 1, height + 1]])
    .addAll(data);

var brush = d3.brush()
    .on("brush", brushed);

//need to format data for these functions
svg.selectAll(".node")
  .data(nodes(quadtree))
  .enter().append("rect")
    .attr("class", "node")
    .attr("x", function(d) { return d.x0; })
    .attr("y", function(d) { return d.y0; })
    .attr("width", function(d) { return d.y1 - d.y0; })
    .attr("height", function(d) { return d.x1 - d.x0; });

var point = svg.selectAll(".point")
  .data(data)
  .enter().append("circle")
    .attr("class", "point")
    .attr("cx", function(d) { return d[0]; })
    .attr("cy", function(d) { return d[1]; })
    .attr("r", 2);

svg.append("g")
    .attr("class", "brush")
    .call(brush)
    .call(brush.move, [[100, 100], [200, 200]]);

function brushed() {
  var extent = d3.event.selection;
  point.each(function(d) { d.scanned = d.selected = false; });
  search(quadtree, extent[0][0], extent[0][1], extent[1][0], extent[1][1]);
  point.classed("point--scanned", function(d) { return d.scanned; });
  point.classed("point--selected", function(d) { return d.selected; });
}

// Find the nodes within the specified rectangle.
function search(quadtree, x0, y0, x3, y3) {
  quadtree.visit(function(node, x1, y1, x2, y2) {
    if (!node.length) {
      do {
        var d = node.data;
        d.scanned = true;
        d.selected = (d[0] >= x0) && (d[0] < x3) && (d[1] >= y0) && (d[1] < y3);
      } while (node = node.next);
    }
    return x1 >= x3 || y1 >= y3 || x2 < x0 || y2 < y0;
  });
}

// Collapse the quadtree into an array of rectangles.
function nodes(quadtree) {
  var nodes = [];
  quadtree.visit(function(node, x0, y0, x1, y1) {
    node.x0 = x0, node.y0 = y0;
    node.x1 = x1, node.y1 = y1;
    nodes.push(node);
  });
  return nodes;
}

</script>

