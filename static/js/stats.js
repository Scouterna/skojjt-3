
/*
function addAxesAndLegend (svg, xAxis, yAxis, margin, chartWidth, chartHeight) {
    var legendWidth  = 200,
        legendHeight = 100;
  
    // clipping to make sure nothing appears behind legend
    svg.append('clipPath')
      .attr('id', 'axes-clip')
      .append('polygon')
        .attr('points', (-margin.left)                 + ',' + (-margin.top)                 + ' ' +
                        (chartWidth - legendWidth - 1) + ',' + (-margin.top)                 + ' ' +
                        (chartWidth - legendWidth - 1) + ',' + legendHeight                  + ' ' +
                        (chartWidth + margin.right)    + ',' + legendHeight                  + ' ' +
                        (chartWidth + margin.right)    + ',' + (chartHeight + margin.bottom) + ' ' +
                        (-margin.left)                 + ',' + (chartHeight + margin.bottom));
  
    var axes = svg.append('g')
      .attr('clip-path', 'url(#axes-clip)');
  
    axes.append('g')
      .attr('class', 'x axis')
      .attr('transform', 'translate(0,' + chartHeight + ')')
      .call(xAxis);
    }
  
  function drawPaths (svg, data, x, y) {
    var upperOuterArea = d3.svg.area()
      .interpolate('basis')
      .x (function (d) { return x(d.date); })
      .y0(function (d) { return y(d.delt); });
  
    svg.datum(data);
  
    svg.append('path')
      .attr('class', 'area upper outer')
      .attr('d', upperOuterArea)
      .attr('clip-path', 'url(#rect-clip)');
  }

  function makeChart (data) {
    var svgWidth  = 960,
        svgHeight = 500,
        margin = { top: 20, right: 20, bottom: 40, left: 40 },
        chartWidth  = svgWidth  - margin.left - margin.right,
        chartHeight = svgHeight - margin.top  - margin.bottom;
  
    var x = d3.time.scale().range([0, chartWidth])
              .domain(d3.extent(data, function (d) { return d.date; })),
        y = d3.scale.linear().range([chartHeight, 0])
              .domain([0, d3.max(data, function (d) { return d.delt; })]);
  
    var xAxis = d3.svg.axis().scale(x).orient('bottom')
                  .innerTickSize(-chartHeight).outerTickSize(0).tickPadding(10),
        yAxis = d3.svg.axis().scale(y).orient('left')
                  .innerTickSize(-chartWidth).outerTickSize(0).tickPadding(10);
  
    var svg = d3.select('body').append('svg')
      .attr('width',  svgWidth)
      .attr('height', svgHeight)
      .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
  
    // clipping to start chart hidden and slide it in later
    var rectClip = svg.append('clipPath')
      .attr('id', 'rect-clip')
      .append('rect')
        .attr('width', 0)
        .attr('height', chartHeight);
  
    addAxesAndLegend(svg, xAxis, yAxis, margin, chartWidth, chartHeight);
    drawPaths(svg, data, x, y);
  }
  
  var parseDate  = d3.time.format('%Y-%m-%d').parse;
  d3.json(
      '/data/meeting_date_count.json', function (error, rawData) 
      {
        if (error) {
            console.error(error);
            return;
        }

        var data = rawData.map(function (d) {
            return {
            date: parseDate(d.date),
            delt: d.delt
            };
        });
  
        makeChart(data);
      }
    );
*/
