#!/usr/bin/env python3
"""The Du Bois D3 Gallery — 178 D3 visualizations (charts, interactions, animations,
and generative-art simulations) in a SINGLE Databricks AI/BI **Custom Page**, themed
with the Du Bois design-system palette. Core-d3 only (sandbox allowlist = d3@7).

Unlike the Vega-Lite gallery in this repo (grid of native/custom-viz widgets), this is
ONE custom-page widget rendering author-written React + D3 — real interactivity and
animation inside a governed AI/BI dashboard.

Requires the workspace preview **"Custom pages in AI/BI dashboards"** to be enabled.

Usage:
  python3 build_custom_page.py --profile <cli-profile> --warehouse <id> [--parent-path /Users/you] [--name "..."]
Re-running is idempotent: it adopts and updates the same-named dashboard in place.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deploy_custom_page import custom_page_widget, deploy

# Du Bois palette as an AI/BI dashboard theme (so the page chrome matches; the tiles
# carry their own tokens inside CODE). Pinned across light/dark so it's stable.
_both = lambda c: {"light": c, "dark": c}
DUBOIS_THEME = {
    "canvasBackgroundColor": _both("#F5F7FA"),
    "widgetBackgroundColor": _both("#FFFFFF"),
    "fontColor": _both("#11171C"),
    "selectionColor": _both("#DD2C4D"),
    "visualizationColors": ["#2463EB", "#2EB88A", "#AB47BD", "#F69E23", "#DD2C4D",
                            "#1BA3BB", "#9B61D1", "#34B262", "#92A4B3", "#5F7281"],
    "widgetHeaderAlignment": "LEFT",
}

CODE = r"""/** @custom-page-source jsx */
var R=require('react'); var d3=require('d3');
// ---- Du Bois design-system tokens ----
var PAL=['#2463EB','#2EB88A','#AB47BD','#F69E23','#DD2C4D','#1BA3BB','#9B61D1','#34B262','#92A4B3'];
var ACCENT='#2272B4', INK='#11171C', INK2='#5F7281', HILITE='#DD2C4D', GRIDC='#E8ECF0', CARD='#FFFFFF', CANVAS='#F5F7FA';
var SEQ=['#E5ECFA','#8CABEE','#2562E4','#0F3995'];
var FONT='DM Sans, Inter, system-ui, sans-serif';
function newSvg(host){return d3.select(host).append('svg').attr('width','100%').attr('height',230).attr('viewBox','0 0 360 230').style('overflow','visible');}
function rnorm(){var s=0;for(var i=0;i<6;i++)s+=Math.random();return s-3;}
function rnormM(m,sd){return m+rnorm()*sd;}
function kde(k,X){return function(V){return X.map(function(x){return [x,d3.mean(V,function(v){return k(x-v);})||0];});};}
function epan(bw){return function(v){v=v/bw;return Math.abs(v)<=1?0.75*(1-v*v)/bw:0;};}
function axc(g){g.selectAll('text').attr('fill',INK2);g.selectAll('line,path').attr('stroke',GRIDC);return g;}
function mpToPath(mp){var s='';(mp.coordinates||[]).forEach(function(poly){poly.forEach(function(ring){s+='M'+ring.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1);}).join('L')+'Z';});});return s;}

/* ===== Distribution ===== */
function drawHistogram(host){var svg=newSvg(host);var data=d3.range(300).map(rnorm);var x=d3.scaleLinear().domain([-3,3]).range([35,348]);
  var bins=d3.bin().domain(x.domain()).thresholds(22)(data);var y=d3.scaleLinear().domain([0,d3.max(bins,function(b){return b.length;})]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(6)));
  svg.selectAll('rect').data(bins).join('rect').attr('x',function(b){return x(b.x0)+1;}).attr('width',function(b){return Math.max(0,x(b.x1)-x(b.x0)-1);}).attr('fill',PAL[2])
    .attr('y',205).attr('height',0).transition().duration(800).attr('y',function(b){return y(b.length);}).attr('height',function(b){return 205-y(b.length);});}
function drawDensity(host){var svg=newSvg(host);var data=d3.range(300).map(rnorm);var x=d3.scaleLinear().domain([-3.5,3.5]).range([35,348]);
  var dens=kde(epan(0.5),x.ticks(60))(data);var y=d3.scaleLinear().domain([0,d3.max(dens,function(d){return d[1];})]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(6)));
  svg.append('path').datum(dens).attr('fill',PAL[1]).attr('opacity',0.5).attr('d',d3.area().x(function(d){return x(d[0]);}).y0(205).y1(function(d){return y(d[1]);}).curve(d3.curveBasis));
  svg.append('path').datum(dens).attr('fill','none').attr('stroke',PAL[1]).attr('stroke-width',1.5).attr('d',d3.line().x(function(d){return x(d[0]);}).y(function(d){return y(d[1]);}).curve(d3.curveBasis));}
function drawBox(host){var svg=newSvg(host);var groups=['A','B','C','D'];var x=d3.scaleBand().domain(groups).range([42,345]).padding(0.4);var y=d3.scaleLinear().domain([-3.5,3.5]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(42,0)').call(d3.axisLeft(y).ticks(5)));
  groups.forEach(function(gn,gi){var data=d3.range(80).map(function(){return rnormM(gi*0.4-0.6,0.8);}).sort(d3.ascending);var q1=d3.quantile(data,0.25),med=d3.quantile(data,0.5),q3=d3.quantile(data,0.75),iqr=q3-q1;
    var lo=Math.max(d3.min(data),q1-1.5*iqr),hi=Math.min(d3.max(data),q3+1.5*iqr),cx=x(gn)+x.bandwidth()/2;
    svg.append('line').attr('x1',cx).attr('x2',cx).attr('y1',y(lo)).attr('y2',y(hi)).attr('stroke',INK2);
    svg.append('rect').attr('x',x(gn)).attr('width',x.bandwidth()).attr('y',y(q3)).attr('height',y(q1)-y(q3)).attr('fill',PAL[gi%PAL.length]).attr('opacity',0.75).attr('stroke',INK2);
    svg.append('line').attr('x1',x(gn)).attr('x2',x(gn)+x.bandwidth()).attr('y1',y(med)).attr('y2',y(med)).attr('stroke',INK).attr('stroke-width',2);});}
function drawViolin(host){var svg=newSvg(host);var groups=['A','B','C'];var y=d3.scaleLinear().domain([-3.5,3.5]).range([205,12]);var x=d3.scaleBand().domain(groups).range([30,350]).padding(0.1);
  axc(svg.append('g').attr('transform','translate(30,0)').call(d3.axisLeft(y).ticks(5)));
  groups.forEach(function(gn,gi){var data=d3.range(120).map(function(){return rnormM(gi-1,0.7);});var dens=kde(epan(0.4),y.ticks(40))(data);var maxd=d3.max(dens,function(d){return d[1];})||1;
    var w=d3.scaleLinear().domain([0,maxd]).range([0,x.bandwidth()/2]);var cx=x(gn)+x.bandwidth()/2;
    svg.append('path').datum(dens).attr('fill',PAL[gi%PAL.length]).attr('opacity',0.7).attr('d',d3.area().x0(function(d){return cx-w(d[1]);}).x1(function(d){return cx+w(d[1]);}).y(function(d){return y(d[0]);}).curve(d3.curveCatmullRom));});}
function drawRidgeline(host){var svg=newSvg(host);var groups=d3.range(5);var x=d3.scaleLinear().domain([-4,4]).range([30,350]);var step=33;
  axc(svg.append('g').attr('transform','translate(0,212)').call(d3.axisBottom(x).ticks(6)));
  groups.forEach(function(gi){var data=d3.range(130).map(function(){return rnormM((gi-2)*0.6,0.8);});var dens=kde(epan(0.4),x.ticks(50))(data);var maxd=d3.max(dens,function(d){return d[1];})||1;var base=195-gi*step;var yh=d3.scaleLinear().domain([0,maxd]).range([0,52]);
    svg.append('path').datum(dens).attr('fill',PAL[gi%PAL.length]).attr('opacity',0.78).attr('stroke',CARD).attr('stroke-width',0.6).attr('d',d3.area().x(function(d){return x(d[0]);}).y0(base).y1(function(d){return base-yh(d[1]);}).curve(d3.curveBasis));});}
function drawBeeswarm(host){var svg=newSvg(host);var data=d3.range(90).map(function(){return rnorm();});var x=d3.scaleLinear().domain([-3,3]).range([20,345]);var nodes=data.map(function(v){return {v:v};});
  var sim=d3.forceSimulation(nodes).force('x',d3.forceX(function(d){return x(d.v);}).strength(1)).force('y',d3.forceY(130).strength(0.05)).force('collide',d3.forceCollide(4.5)).stop();
  for(var i=0;i<160;i++)sim.tick();axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(6)));
  svg.append('g').selectAll('circle').data(nodes).join('circle').attr('cx',function(d){return d.x;}).attr('cy',function(d){return d.y;}).attr('r',4).attr('fill',PAL[1]).attr('opacity',0.8).attr('stroke',CARD).attr('stroke-width',0.5);}

/* ===== Correlation ===== */
function drawScatter(host){var svg=newSvg(host);var data=d3.range(45).map(function(){return [Math.random(),Math.random(),Math.random()];});var x=d3.scaleLinear().domain([0,1]).range([15,350]);var y=d3.scaleLinear().domain([0,1]).range([215,10]);
  svg.selectAll('circle').data(data).join('circle').attr('cx',function(d){return x(d[0]);}).attr('cy',function(d){return y(d[1]);}).attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('opacity',0.72).attr('r',0).transition().duration(800).delay(function(_,i){return i*14;}).attr('r',function(d){return 3+d[2]*8;});}
function drawBubble(host){var svg=newSvg(host);var data=d3.range(28).map(function(){return [Math.random(),Math.random(),Math.random()];});var x=d3.scaleLinear().domain([0,1]).range([20,345]);var y=d3.scaleLinear().domain([0,1]).range([210,12]);var r=d3.scaleSqrt().domain([0,1]).range([4,22]);
  svg.selectAll('circle').data(data).join('circle').attr('cx',function(d){return x(d[0]);}).attr('cy',function(d){return y(d[1]);}).attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('opacity',0.5).attr('stroke',function(_,i){return PAL[i%PAL.length];}).attr('r',function(d){return r(d[2]);});}
function drawConnScatter(host){var svg=newSvg(host);var data=d3.range(14).map(function(i){return [i,50+20*Math.sin(i/2)+Math.random()*8];});var x=d3.scaleLinear().domain([0,13]).range([30,345]);var y=d3.scaleLinear().domain([0,90]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(6)));
  svg.append('path').datum(data).attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',1.5).attr('d',d3.line().x(function(d){return x(d[0]);}).y(function(d){return y(d[1]);}));
  svg.selectAll('circle').data(data).join('circle').attr('cx',function(d){return x(d[0]);}).attr('cy',function(d){return y(d[1]);}).attr('r',4).attr('fill',PAL[0]);}
function drawHeatmap(host){var svg=newSvg(host);var xs=d3.range(11),ys=d3.range(7);var x=d3.scaleBand().domain(xs).range([25,352]).padding(0.06);var y=d3.scaleBand().domain(ys).range([8,210]).padding(0.06);
  var c=d3.scaleLinear().domain([0,0.5,1]).range(SEQ.slice(0,3));var cells=[];xs.forEach(function(xi){ys.forEach(function(yi){cells.push([xi,yi,Math.random()]);});});
  svg.selectAll('rect').data(cells).join('rect').attr('x',function(d){return x(d[0]);}).attr('y',function(d){return y(d[1]);}).attr('width',x.bandwidth()).attr('height',y.bandwidth()).attr('rx',2).attr('fill',function(d){return c(d[2]);});}
function drawViridis(host){var svg=newSvg(host);var xs=d3.range(14),ys=d3.range(8);var x=d3.scaleBand().domain(xs).range([20,352]).padding(0.04);var y=d3.scaleBand().domain(ys).range([8,212]).padding(0.04);
  var c=d3.scaleSequential(d3.interpolateViridis).domain([0,1]);var cells=[];xs.forEach(function(xi){ys.forEach(function(yi){cells.push([xi,yi,(xi/14+yi/8)/2+Math.random()*0.25]);});});
  svg.selectAll('rect').data(cells).join('rect').attr('x',function(d){return x(d[0]);}).attr('y',function(d){return y(d[1]);}).attr('width',x.bandwidth()).attr('height',y.bandwidth()).attr('fill',function(d){return c(Math.min(1,d[2]));});}
function drawContour(host){var svg=newSvg(host);var pts=d3.range(400).map(function(){var k=Math.random()<0.5;return [180+(k?-55:55)+rnorm()*34,115+(k?-25:30)+rnorm()*26];});
  var cs=d3.contourDensity().x(function(d){return d[0];}).y(function(d){return d[1];}).size([360,230]).bandwidth(16)(pts);var color=d3.scaleSequential(d3.interpolateViridis).domain(d3.extent(cs,function(c){return c.value;}));
  svg.append('g').selectAll('path').data(cs).join('path').attr('d',function(c){return mpToPath(c);}).attr('fill',function(c){return color(c.value);});
  svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx',function(d){return d[0];}).attr('cy',function(d){return d[1];}).attr('r',1).attr('fill','#fff').attr('opacity',0.25);}
function drawVoronoi(host){var svg=newSvg(host);var pts=d3.range(42).map(function(){return [15+Math.random()*330,12+Math.random()*206];});var del=d3.Delaunay.from(pts);var voro=del.voronoi([0,0,360,230]);
  svg.append('g').attr('stroke','#fff').attr('stroke-width',0.6).selectAll('path').data(pts).join('path').attr('d',function(_,i){return voro.renderCell(i);}).attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('fill-opacity',0.4);
  svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx',function(d){return d[0];}).attr('cy',function(d){return d[1];}).attr('r',2).attr('fill',INK);}

/* ===== Ranking ===== */
function drawBars(host){var svg=newSvg(host);var data=[['Mon',30],['Tue',55],['Wed',43],['Thu',78],['Fri',62]];var x=d3.scaleBand().domain(data.map(function(d){return d[0];})).range([35,348]).padding(0.2);var y=d3.scaleLinear().domain([0,90]).range([200,12]);
  axc(svg.append('g').attr('transform','translate(0,200)').call(d3.axisBottom(x)));axc(svg.append('g').attr('transform','translate(35,0)').call(d3.axisLeft(y).ticks(4)));
  svg.selectAll('rect.b').data(data).join('rect').attr('class','b').attr('x',function(d){return x(d[0]);}).attr('width',x.bandwidth()).attr('rx',2).attr('fill',PAL[1]).attr('y',y(0)).attr('height',0).transition().duration(900).delay(function(_,i){return i*90;}).attr('y',function(d){return y(d[1]);}).attr('height',function(d){return y(0)-y(d[1]);});}
function drawHBar(host){var svg=newSvg(host);var data=[['Alpha',62],['Bravo',48],['Charlie',78],['Delta',35],['Echo',55],['Foxtrot',70]];data.sort(function(a,b){return b[1]-a[1];});var y=d3.scaleBand().domain(data.map(function(d){return d[0];})).range([12,215]).padding(0.2);var x=d3.scaleLinear().domain([0,90]).range([78,350]);
  axc(svg.append('g').attr('transform','translate(78,0)').call(d3.axisLeft(y)));
  svg.selectAll('rect').data(data).join('rect').attr('x',78).attr('y',function(d){return y(d[0]);}).attr('height',y.bandwidth()).attr('rx',2).attr('fill',PAL[0]).attr('width',0).transition().duration(800).delay(function(_,i){return i*70;}).attr('width',function(d){return x(d[1])-78;});}
function drawLollipop(host){var svg=newSvg(host);var data=[['A',62],['B',48],['C',78],['D',35],['E',55],['F',70],['G',40]];var y=d3.scaleBand().domain(data.map(function(d){return d[0];})).range([12,215]).padding(0.4);var x=d3.scaleLinear().domain([0,90]).range([40,350]);
  axc(svg.append('g').attr('transform','translate(40,0)').call(d3.axisLeft(y)));var g=svg.selectAll('g.l').data(data).join('g').attr('class','l');
  g.append('line').attr('x1',40).attr('x2',40).attr('y1',function(d){return y(d[0])+y.bandwidth()/2;}).attr('y2',function(d){return y(d[0])+y.bandwidth()/2;}).attr('stroke',INK2).transition().duration(800).attr('x2',function(d){return x(d[1]);});
  g.append('circle').attr('cx',40).attr('cy',function(d){return y(d[0])+y.bandwidth()/2;}).attr('r',5).attr('fill',PAL[1]).transition().duration(800).attr('cx',function(d){return x(d[1]);});}
function drawCircBar(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,118)');var data=d3.range(16).map(function(i){return {i:i,v:20+Math.random()*80};});var x=d3.scaleBand().domain(data.map(function(d){return d.i;})).range([0,2*Math.PI]).padding(0.05);
  var y=(d3.scaleRadial?d3.scaleRadial():d3.scaleLinear()).domain([0,100]).range([28,105]);var arc=d3.arc().innerRadius(28).outerRadius(function(d){return y(d.v);}).startAngle(function(d){return x(d.i);}).endAngle(function(d){return x(d.i)+x.bandwidth();}).padAngle(0.02).padRadius(28);
  g.selectAll('path').data(data).join('path').attr('fill',function(d){return PAL[d.i%PAL.length];}).attr('d',arc);}
function drawRadar(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,118)');var axes=['Speed','Power','Range','Cost','Agility','Tech'],N=axes.length,Rr=88;var ang=function(i){return i/N*2*Math.PI-Math.PI/2;};var rs=d3.scaleLinear().domain([0,100]).range([0,Rr]);
  [0.25,0.5,0.75,1].forEach(function(f){g.append('circle').attr('r',Rr*f).attr('fill','none').attr('stroke',GRIDC);});
  axes.forEach(function(a,i){g.append('line').attr('x2',Math.cos(ang(i))*Rr).attr('y2',Math.sin(ang(i))*Rr).attr('stroke',GRIDC);g.append('text').attr('x',Math.cos(ang(i))*(Rr+12)).attr('y',Math.sin(ang(i))*(Rr+12)).attr('text-anchor','middle').attr('dy',3).attr('font-size',9).attr('font-family',FONT).attr('fill',INK2).text(a);});
  [[70,60,80,40,65,90],[45,80,55,70,50,60]].forEach(function(vals,si){var pts=vals.map(function(v,i){return [Math.cos(ang(i))*rs(v),Math.sin(ang(i))*rs(v)];});g.append('path').attr('d',d3.line()(pts)+'Z').attr('fill',PAL[si]).attr('fill-opacity',0.3).attr('stroke',PAL[si]).attr('stroke-width',2);});}
function drawParallel(host){var svg=newSvg(host);var dims=['m1','m2','m3','m4'];var data=d3.range(24).map(function(){return {m1:Math.random(),m2:Math.random(),m3:Math.random(),m4:Math.random()};});var x=d3.scalePoint().domain(dims).range([40,340]);var ys={};dims.forEach(function(d){ys[d]=d3.scaleLinear().domain([0,1]).range([205,18]);});
  dims.forEach(function(d){svg.append('line').attr('x1',x(d)).attr('x2',x(d)).attr('y1',18).attr('y2',205).attr('stroke',GRIDC);svg.append('text').attr('x',x(d)).attr('y',12).attr('text-anchor','middle').attr('font-size',9).attr('font-family',FONT).attr('fill',INK2).text(d);});
  var line=d3.line();data.forEach(function(row,i){var pts=dims.map(function(d){return [x(d),ys[d](row[d])];});svg.append('path').attr('d',line(pts)).attr('fill','none').attr('stroke',PAL[i%PAL.length]).attr('stroke-width',1).attr('opacity',0.5);});}
function drawCandle(host){var svg=newSvg(host);var n=22;var pr=100;var data=d3.range(n).map(function(i){var o=pr;var c=o+(Math.random()-0.48)*9;var h=Math.max(o,c)+Math.random()*3;var l=Math.min(o,c)-Math.random()*3;pr=c;return {i:i,o:o,c:c,h:h,l:l};});
  var x=d3.scaleBand().domain(d3.range(n)).range([35,352]).padding(0.3);var ext=d3.extent(data.flatMap(function(d){return [d.h,d.l];}));var y=d3.scaleLinear().domain(ext).nice().range([205,12]);
  axc(svg.append('g').attr('transform','translate(35,0)').call(d3.axisLeft(y).ticks(4)));var g=svg.selectAll('g.c').data(data).join('g').attr('class','c').attr('transform',function(d){return 'translate('+(x(d.i)+x.bandwidth()/2)+',0)';});
  g.append('line').attr('y1',function(d){return y(d.h);}).attr('y2',function(d){return y(d.l);}).attr('stroke',INK2);
  g.append('rect').attr('x',-x.bandwidth()/2).attr('width',x.bandwidth()).attr('y',function(d){return y(Math.max(d.o,d.c));}).attr('height',function(d){return Math.max(1,Math.abs(y(d.o)-y(d.c)));}).attr('fill',function(d){return d.c>=d.o?PAL[1]:HILITE;});}
function drawMarimekko(host){var svg=newSvg(host);var cols=[['A',40],['B',28],['C',20],['D',14]];var total=d3.sum(cols,function(d){return d[1];});var xacc=30,Wd=322;
  cols.forEach(function(col){var cw=Wd*col[1]/total;var segs=d3.range(3).map(function(){return 0.5+Math.random();});var st=d3.sum(segs);var yacc=15;
    segs.forEach(function(s,si){var sh=(205-15)*s/st;svg.append('rect').attr('x',xacc).attr('width',cw-2).attr('y',yacc).attr('height',sh-1).attr('fill',PAL[si%PAL.length]).attr('opacity',0.85);yacc+=sh;});
    svg.append('text').attr('x',xacc+cw/2).attr('y',222).attr('text-anchor','middle').attr('font-size',10).attr('font-family',FONT).attr('fill',INK2).text(col[0]);xacc+=cw;});}

/* ===== Part of a whole ===== */
function drawPie(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var pie=d3.pie().sort(null);var arc=d3.arc().innerRadius(0).outerRadius(95);
  g.selectAll('path').data(pie([35,25,20,12,8])).join('path').attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('stroke','#fff').attr('d',arc);}
function drawDonut(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var pie=d3.pie().sort(null);var arc=d3.arc().innerRadius(45).outerRadius(95).cornerRadius(3).padAngle(0.02);
  g.selectAll('path').data(pie([30,22,18,14,10,6])).join('path').attr('fill',function(_,i){return PAL[i%PAL.length];}).each(function(d){this._c={startAngle:0,endAngle:0};}).transition().duration(900).attrTween('d',function(d){var i=d3.interpolate(this._c,d);this._c=i(1);return function(t){return arc(i(t));};});}
function drawTreemap(host){var svg=newSvg(host);var vals=[28,55,43,78,34,19,62,25,40];var root=d3.hierarchy({children:vals.map(function(v,i){return {name:'N'+i,value:v};})}).sum(function(d){return d.value;}).sort(function(a,b){return b.value-a.value;});
  d3.treemap().size([360,230]).padding(3)(root);var n=svg.selectAll('g').data(root.leaves()).join('g').attr('transform',function(d){return 'translate('+d.x0+','+d.y0+')';});
  n.append('rect').attr('width',function(d){return d.x1-d.x0;}).attr('height',function(d){return d.y1-d.y0;}).attr('rx',3).attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('opacity',0).transition().duration(700).delay(function(_,i){return i*60;}).attr('opacity',0.9);}
function drawPack(host){var svg=newSvg(host);var root=d3.hierarchy({children:d3.range(14).map(function(i){return {name:'n'+i,value:5+Math.random()*40};})}).sum(function(d){return d.value;});
  d3.pack().size([345,220]).padding(3)(root);var g=svg.append('g').attr('transform','translate(8,5)');
  g.selectAll('circle').data(root.leaves()).join('circle').attr('cx',function(d){return d.x;}).attr('cy',function(d){return d.y;}).attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('opacity',0.8).attr('r',0).transition().duration(800).delay(function(_,i){return i*40;}).attr('r',function(d){return d.r;});}
function drawDendro(host){var svg=newSvg(host);var data={name:'root',children:[{name:'A',children:[{name:'a1'},{name:'a2'}]},{name:'B',children:[{name:'b1'},{name:'b2'},{name:'b3'}]},{name:'C',children:[{name:'c1'}]}]};
  var root=d3.hierarchy(data);d3.cluster().size([210,245])(root);var g=svg.append('g').attr('transform','translate(45,10)');
  g.selectAll('path').data(root.links()).join('path').attr('fill','none').attr('stroke',ACCENT).attr('stroke-opacity',0.5).attr('d',d3.linkHorizontal().x(function(d){return d.y;}).y(function(d){return d.x;}));
  var n=g.selectAll('g').data(root.descendants()).join('g').attr('transform',function(d){return 'translate('+d.y+','+d.x+')';});
  n.append('circle').attr('r',3).attr('fill',function(d){return d.children?INK:ACCENT;});
  n.append('text').attr('dy',3).attr('x',function(d){return d.children?-6:6;}).attr('text-anchor',function(d){return d.children?'end':'start';}).attr('font-size',9).attr('font-family',FONT).attr('fill',INK2).text(function(d){return d.data.name;});}
function drawRadialTree(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var data={name:'r',children:d3.range(4).map(function(i){return {name:'G'+i,children:d3.range(3).map(function(){return {name:'n'};})};})};
  var root=d3.hierarchy(data);d3.tree().size([2*Math.PI,98]).separation(function(a,b){return (a.parent===b.parent?1:2)/Math.max(1,a.depth);})(root);
  g.append('g').attr('fill','none').attr('stroke',ACCENT).attr('stroke-opacity',0.5).selectAll('path').data(root.links()).join('path').attr('d',d3.linkRadial().angle(function(d){return d.x;}).radius(function(d){return d.y;}));
  g.append('g').selectAll('circle').data(root.descendants()).join('circle').attr('transform',function(d){return 'rotate('+(d.x*180/Math.PI-90)+') translate('+d.y+',0)';}).attr('r',3).attr('fill',function(d){return d.children?INK:ACCENT;});}
function drawStackBar(host){var svg=newSvg(host);var cats=['Q1','Q2','Q3','Q4'],keys=['a','b','c'];var data=cats.map(function(c){return {cat:c,a:20+Math.random()*30,b:15+Math.random()*25,c:10+Math.random()*20};});var st=d3.stack().keys(keys)(data);
  var x=d3.scaleBand().domain(cats).range([40,345]).padding(0.3);var y=d3.scaleLinear().domain([0,d3.max(data,function(d){return d.a+d.b+d.c;})]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x)));
  svg.append('g').selectAll('g').data(st).join('g').attr('fill',function(_,i){return PAL[i%PAL.length];}).selectAll('rect').data(function(d){return d;}).join('rect').attr('x',function(d){return x(d.data.cat);}).attr('width',x.bandwidth()).attr('y',function(d){return y(d[1]);}).attr('height',function(d){return y(d[0])-y(d[1]);});}
function drawSunburst(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var data={name:'r',children:d3.range(4).map(function(i){return {name:'A'+i,children:d3.range(3).map(function(){return {name:'L',value:5+Math.random()*20};})};})};
  var root=d3.hierarchy(data).sum(function(d){return d.value;});d3.partition().size([2*Math.PI,105])(root);var arc=d3.arc().startAngle(function(d){return d.x0;}).endAngle(function(d){return d.x1;}).innerRadius(function(d){return d.y0;}).outerRadius(function(d){return d.y1;}).padAngle(0.005);
  g.selectAll('path').data(root.descendants().filter(function(d){return d.depth;})).join('path').attr('fill',function(d,i){return PAL[i%PAL.length];}).attr('d',arc).attr('opacity',0).transition().duration(800).delay(function(_,i){return i*40;}).attr('opacity',0.9);}

/* ===== Evolution ===== */
function drawLine(host){var svg=newSvg(host);var data=d3.range(24).map(function(i){return [i,50+30*Math.sin(i/3)+Math.random()*8];});var x=d3.scaleLinear().domain([0,23]).range([35,348]);var y=d3.scaleLinear().domain([0,100]).range([200,12]);
  axc(svg.append('g').attr('transform','translate(0,200)').call(d3.axisBottom(x).ticks(6)));axc(svg.append('g').attr('transform','translate(35,0)').call(d3.axisLeft(y).ticks(4)));
  var p=svg.append('path').datum(data).attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',2).attr('d',d3.line().x(function(d){return x(d[0]);}).y(function(d){return y(d[1]);}).curve(d3.curveMonotoneX));
  var L=p.node().getTotalLength();p.attr('stroke-dasharray',L+' '+L).attr('stroke-dashoffset',L).transition().duration(1500).attr('stroke-dashoffset',0);}
function drawMultiLine(host){var svg=newSvg(host);var x=d3.scaleLinear().domain([0,20]).range([35,345]);var y=d3.scaleLinear().domain([0,100]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(5)));
  [0,1,2].forEach(function(s){var data=d3.range(21).map(function(i){return [i,40+25*Math.sin(i/3+s)+s*8+Math.random()*5];});svg.append('path').datum(data).attr('fill','none').attr('stroke',PAL[s]).attr('stroke-width',2).attr('d',d3.line().x(function(d){return x(d[0]);}).y(function(d){return y(d[1]);}).curve(d3.curveMonotoneX));});}
function drawArea(host){var svg=newSvg(host);var data=d3.range(30).map(function(i){return [i,45+25*Math.sin(i/4)+Math.random()*10];});var x=d3.scaleLinear().domain([0,29]).range([10,350]);var y=d3.scaleLinear().domain([0,100]).range([215,10]);
  svg.append('path').datum(data).attr('fill',PAL[0]).attr('opacity',0).attr('d',d3.area().x(function(d){return x(d[0]);}).y0(y(0)).y1(function(d){return y(d[1]);}).curve(d3.curveCatmullRom)).transition().duration(1200).attr('opacity',0.85);}
function drawStackArea(host){var svg=newSvg(host);var keys=['a','b','c','d'];var data=d3.range(20).map(function(i){var o={i:i};keys.forEach(function(k,ki){o[k]=10+10*Math.sin(i/4+ki)+Math.random()*5+5;});return o;});var st=d3.stack().keys(keys)(data);
  var x=d3.scaleLinear().domain([0,19]).range([10,350]);var y=d3.scaleLinear().domain([0,d3.max(st[st.length-1],function(d){return d[1];})]).range([215,10]);
  svg.selectAll('path').data(st).join('path').attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('opacity',0.85).attr('d',d3.area().x(function(d){return x(d.data.i);}).y0(function(d){return y(d[0]);}).y1(function(d){return y(d[1]);}).curve(d3.curveBasis));}
function drawStream(host){var svg=newSvg(host);var keys=['a','b','c','d','e'];var data=d3.range(24).map(function(i){var o={i:i};keys.forEach(function(k,ki){o[k]=Math.max(0,10+8*Math.sin(i/3+ki*1.3)+Math.random()*4);});return o;});var st=d3.stack().keys(keys).offset(d3.stackOffsetWiggle)(data);
  var x=d3.scaleLinear().domain([0,23]).range([0,360]);var y=d3.scaleLinear().domain([d3.min(st,function(l){return d3.min(l,function(d){return d[0];});}),d3.max(st,function(l){return d3.max(l,function(d){return d[1];});})]).range([225,5]);
  svg.selectAll('path').data(st).join('path').attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('d',d3.area().x(function(d){return x(d.data.i);}).y0(function(d){return y(d[0]);}).y1(function(d){return y(d[1]);}).curve(d3.curveBasis));}

/* ===== Flow & network ===== */
function drawChord(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var m=[[0,5,6,4,3],[5,0,8,3,2],[6,8,0,5,4],[4,3,5,0,6],[3,2,4,6,0]];var ch=d3.chord().padAngle(0.05).sortSubgroups(d3.descending)(m);
  var arc=d3.arc().innerRadius(88).outerRadius(98),rib=d3.ribbon().radius(88);
  g.append('g').selectAll('path').data(ch.groups).join('path').attr('d',arc).attr('fill',function(d){return PAL[d.index%PAL.length];});
  g.append('g').attr('fill-opacity',0.6).selectAll('path').data(ch).join('path').attr('d',rib).attr('fill',function(d){return PAL[d.source.index%PAL.length];}).attr('stroke','#fff').attr('stroke-width',0.3);}
function drawArc(host){var svg=newSvg(host);var N=10,nodes=d3.range(N);var x=d3.scalePoint().domain(nodes).range([25,345]);var baseY=185;var links=d3.range(16).map(function(){return [Math.floor(Math.random()*N),Math.floor(Math.random()*N)];}).filter(function(l){return l[0]!==l[1];});
  svg.append('g').selectAll('path').data(links).join('path').attr('fill','none').attr('stroke',ACCENT).attr('stroke-opacity',0.4).attr('d',function(l){var x1=x(l[0]),x2=x(l[1]),r=Math.abs(x2-x1)/2;return 'M'+x1+','+baseY+' A'+r+','+r+' 0 0,'+(x1<x2?1:0)+' '+x2+','+baseY;});
  svg.append('g').selectAll('circle').data(nodes).join('circle').attr('cx',function(d){return x(d);}).attr('cy',baseY).attr('r',5).attr('fill',function(d){return PAL[d%PAL.length];});}
function drawDragForce(host){var svg=newSvg(host);var N=16;var nodes=d3.range(N).map(function(i){return {id:i};});var links=d3.range(N-1).map(function(i){return {source:i+1,target:Math.floor(Math.random()*(i+1))};});
  var link=svg.append('g').attr('stroke','#bbb').attr('stroke-opacity',0.6).selectAll('line').data(links).join('line');var node=svg.append('g').selectAll('circle').data(nodes).join('circle').attr('r',7).attr('fill',function(d){return PAL[d.id%PAL.length];}).style('cursor','grab');
  var sim=d3.forceSimulation(nodes).force('charge',d3.forceManyBody().strength(-60)).force('link',d3.forceLink(links).distance(30)).force('center',d3.forceCenter(180,115)).on('tick',function(){link.attr('x1',function(d){return d.source.x;}).attr('y1',function(d){return d.source.y;}).attr('x2',function(d){return d.target.x;}).attr('y2',function(d){return d.target.y;});node.attr('cx',function(d){return d.x;}).attr('cy',function(d){return d.y;});});
  node.call(d3.drag().on('start',function(e,d){if(!e.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;}).on('drag',function(e,d){d.fx=e.x;d.fy=e.y;}).on('end',function(e,d){if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}));return function(){sim.stop();};}
function drawBundle(host){var W=360,Rad=W/2-45;var groups=d3.range(5).map(function(i){return {name:'G'+i,children:d3.range(5).map(function(j){return {name:'G'+i+'.'+j,group:i};})};});var root=d3.hierarchy({name:'',children:groups});d3.cluster().size([2*Math.PI,Rad])(root);var leaves=root.leaves();var links=[];
  leaves.forEach(function(l){var m=1+Math.floor(Math.random()*3);for(var k=0;k<m;k++){var t=leaves[Math.floor(Math.random()*leaves.length)];if(t!==l)links.push([l,t]);}});
  var line=d3.lineRadial().curve(d3.curveBundle.beta(0.85)).radius(function(d){return d.y;}).angle(function(d){return d.x;});
  var svg=d3.select(host).append('svg').attr('width','100%').attr('height',320).attr('viewBox',[-W/2,-W/2,W,W]).style('font','9px '+FONT);var g=svg.append('g');
  var link=g.append('g').attr('fill','none').attr('stroke',ACCENT).attr('stroke-opacity',0.35).selectAll('path').data(links).join('path').attr('d',function(d){return line(d[0].path(d[1]));});
  var node=g.append('g').selectAll('g').data(leaves).join('g').attr('transform',function(d){return 'rotate('+(d.x*180/Math.PI-90)+') translate('+d.y+',0)';});
  node.append('circle').attr('r',3.5).attr('fill',function(d){return PAL[d.data.group%PAL.length];}).style('cursor','pointer').on('mouseover',function(e,d){link.attr('stroke-opacity',0.04);link.filter(function(l){return l[0]===d||l[1]===d;}).attr('stroke',HILITE).attr('stroke-opacity',0.95).raise();}).on('mouseout',function(){link.attr('stroke',ACCENT).attr('stroke-opacity',0.35);});}

/* ===== Interactive & animated ===== */
function drawZoomSun(host){var width=360,radius=width/6;var data={name:'root',children:d3.range(5).map(function(i){return {name:'G'+i,children:d3.range(3+i%3).map(function(j){return {name:'c',children:d3.range(2+j%3).map(function(){return {name:'',value:1+Math.random()*8};})};})};})};
  var root=d3.hierarchy(data).sum(function(d){return d.value;}).sort(function(a,b){return b.value-a.value;});d3.partition().size([2*Math.PI,root.height+1])(root);root.each(function(d){d.current=d;});
  var arc=d3.arc().startAngle(function(d){return d.x0;}).endAngle(function(d){return d.x1;}).padAngle(function(d){return Math.min((d.x1-d.x0)/2,0.005);}).padRadius(radius*1.5).innerRadius(function(d){return d.y0*radius;}).outerRadius(function(d){return Math.max(d.y0*radius,d.y1*radius-1);});
  var svg=d3.select(host).append('svg').attr('viewBox',[-width/2,-width/2,width,width]).attr('width','100%').attr('height',300).style('font','10px '+FONT);var g=svg.append('g');
  function vis(d){return d.y1<=3&&d.y0>=1&&d.x1>d.x0;}
  var path=g.append('g').selectAll('path').data(root.descendants().slice(1)).join('path').attr('fill',function(d){var n=d;while(n.depth>1)n=n.parent;return PAL[root.children.indexOf(n)%PAL.length];}).attr('fill-opacity',function(d){return vis(d.current)?(d.children?0.85:0.55):0;}).attr('pointer-events',function(d){return vis(d.current)?'auto':'none';}).attr('d',function(d){return arc(d.current);});
  path.filter(function(d){return d.children;}).style('cursor','pointer').on('click',clicked);var parent=g.append('circle').datum(root).attr('r',radius).attr('fill','none').attr('pointer-events','all').style('cursor','pointer').on('click',clicked);
  function clicked(event,p){parent.datum(p.parent||root);root.each(function(d){d.target={x0:Math.max(0,Math.min(1,(d.x0-p.x0)/(p.x1-p.x0)))*2*Math.PI,x1:Math.max(0,Math.min(1,(d.x1-p.x0)/(p.x1-p.x0)))*2*Math.PI,y0:Math.max(0,d.y0-p.depth),y1:Math.max(0,d.y1-p.depth)};});var t=g.transition().duration(680);
    path.transition(t).tween('data',function(d){var i=d3.interpolate(d.current,d.target);return function(tt){d.current=i(tt);};}).attr('fill-opacity',function(d){return vis(d.target)?(d.children?0.85:0.55):0;}).attr('pointer-events',function(d){return vis(d.target)?'auto':'none';}).attrTween('d',function(d){return function(){return arc(d.current);};});}}
function drawIcicle(host){var W=352,H=200;var svg=newSvg(host);var data={name:'root',children:d3.range(4).map(function(i){return {name:'G'+i,children:d3.range(3+i%2).map(function(j){return {name:'',value:5+Math.random()*25};})};})};
  var root=d3.hierarchy(data).sum(function(d){return d.value;}).sort(function(a,b){return b.value-a.value;});d3.partition().size([H,W])(root);
  var xs=d3.scaleLinear().domain([0,H]).range([12,212]);var ys=d3.scaleLinear().domain([0,W]).range([4,356]);var cell=svg.append('g').selectAll('g').data(root.descendants()).join('g');
  var rect=cell.append('rect').attr('fill',function(d){var n=d;while(n.depth>1)n=n.parent;return d.depth===0?'#C7D2DE':PAL[root.children.indexOf(n)%PAL.length];}).attr('opacity',0.88).style('cursor','pointer');
  function render(){cell.attr('transform',function(d){return 'translate('+ys(d.y0)+','+xs(d.x0)+')';});rect.attr('width',function(d){return Math.max(0,ys(d.y1)-ys(d.y0)-1);}).attr('height',function(d){return Math.max(0,xs(d.x1)-xs(d.x0)-1);});}
  render();rect.on('click',function(event,p){xs.domain([p.x0,p.x1]);ys.domain([p.y0,W]);var t=svg.transition().duration(600);cell.transition(t).attr('transform',function(d){return 'translate('+ys(d.y0)+','+xs(d.x0)+')';});rect.transition(t).attr('width',function(d){return Math.max(0,ys(d.y1)-ys(d.y0)-1);}).attr('height',function(d){return Math.max(0,xs(d.x1)-xs(d.x0)-1);});});}
function drawTree(host){var data={name:'Root',children:[{name:'Japan',children:[{name:'Chiba'},{name:'Osaka'},{name:'Tokyo'}]},{name:'US',children:[{name:'West'},{name:'East'},{name:'South'}]},{name:'Europe',children:[{name:'Italy'},{name:'Sweden'}]}]};
  var width=350,mT=10,mB=10,mL=52;var root=d3.hierarchy(data);var dx=16;var dy=(width-10-mL)/(1+root.height);var tree=d3.tree().nodeSize([dx,dy]);var diagonal=d3.linkHorizontal().x(function(d){return d.y;}).y(function(d){return d.x;});
  var svg=d3.select(host).append('svg').attr('width','100%').attr('height',dx).attr('viewBox',[-mL,-mT,width,dx]).attr('style','max-width:100%;height:auto;font:11px '+FONT+';user-select:none;');
  var gLink=svg.append('g').attr('fill','none').attr('stroke',ACCENT).attr('stroke-opacity',0.5).attr('stroke-width',1.5);var gNode=svg.append('g').attr('cursor','pointer').attr('pointer-events','all');
  function update(event,source){var nodes=root.descendants().reverse(),links=root.links();tree(root);var left=root,right=root;root.eachBefore(function(n){if(n.x<left.x)left=n;if(n.x>right.x)right=n;});var height=right.x-left.x+mT+mB;
    var tr=svg.transition().duration(250).attr('height',height).attr('viewBox',[-mL,left.x-mT,width,height]);var node=gNode.selectAll('g').data(nodes,function(d){return d.id;});
    var en=node.enter().append('g').attr('transform',function(){return 'translate('+source.y0+','+source.x0+')';}).attr('fill-opacity',0).attr('stroke-opacity',0).on('click',function(event,d){d.children=d.children?null:d._children;update(event,d);});
    en.append('circle').attr('r',3).attr('fill',function(d){return d._children?INK:ACCENT;}).attr('stroke-width',10);
    en.append('text').attr('dy','0.31em').attr('x',function(d){return d._children?-7:7;}).attr('text-anchor',function(d){return d._children?'end':'start';}).text(function(d){return d.data.name;}).attr('stroke-linejoin','round').attr('stroke-width',3).attr('stroke','#fff').attr('paint-order','stroke').attr('fill',INK);
    node.merge(en).transition(tr).attr('transform',function(d){return 'translate('+d.y+','+d.x+')';}).attr('fill-opacity',1).attr('stroke-opacity',1);
    node.exit().transition(tr).remove().attr('transform',function(){return 'translate('+source.y+','+source.x+')';}).attr('fill-opacity',0).attr('stroke-opacity',0);
    var link=gLink.selectAll('path').data(links,function(d){return d.target.id;});var le=link.enter().append('path').attr('d',function(){var o={x:source.x0,y:source.y0};return diagonal({source:o,target:o});});
    link.merge(le).transition(tr).attr('d',diagonal);link.exit().transition(tr).remove().attr('d',function(){var o={x:source.x,y:source.y};return diagonal({source:o,target:o});});root.eachBefore(function(d){d.x0=d.x;d.y0=d.y;});}
  root.x0=dy/2;root.y0=0;root.descendants().forEach(function(d,i){d.id=i;d._children=d.children;if(d.depth>=1)d.children=null;});update(null,root);}
function drawTooltip(host){var svg=newSvg(host);var data=[['A',40],['B',72],['C',55],['D',88],['E',63],['F',30],['G',50]];var x=d3.scaleBand().domain(data.map(function(d){return d[0];})).range([25,348]).padding(0.2);var y=d3.scaleLinear().domain([0,100]).range([205,15]);
  svg.selectAll('rect.b').data(data).join('rect').attr('class','b').attr('x',function(d){return x(d[0]);}).attr('width',x.bandwidth()).attr('y',function(d){return y(d[1]);}).attr('height',function(d){return 205-y(d[1]);}).attr('fill',PAL[2]).attr('rx',2)
    .on('mousemove',function(event,d){var p=d3.pointer(event,svg.node());tip.style('display',null).attr('transform','translate('+p[0]+','+(p[1]-16)+')');tt.text(d[0]+': '+d[1]);}).on('mouseout',function(){tip.style('display','none');});
  var tip=svg.append('g').style('display','none').style('pointer-events','none');tip.append('rect').attr('x',-26).attr('y',-15).attr('width',52).attr('height',22).attr('rx',4).attr('fill',INK);var tt=tip.append('text').attr('text-anchor','middle').attr('fill','#fff').attr('font-size',11).attr('font-family',FONT);}
function drawNearest(host){var svg=newSvg(host);var pts=d3.range(70).map(function(){return [20+Math.random()*320,15+Math.random()*185];});var del=d3.Delaunay.from(pts);
  svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx',function(d){return d[0];}).attr('cy',function(d){return d[1];}).attr('r',3.5).attr('fill',ACCENT).attr('opacity',0.55);
  var hl=svg.append('circle').attr('r',8).attr('fill','none').attr('stroke',HILITE).attr('stroke-width',2).style('display','none');var lbl=svg.append('text').attr('font-size',11).attr('font-family',FONT).attr('fill',INK).style('display','none');
  svg.append('rect').attr('width',360).attr('height',215).attr('fill','transparent').on('mousemove',function(event){var p=d3.pointer(event);var i=del.find(p[0],p[1]);hl.style('display',null).attr('cx',pts[i][0]).attr('cy',pts[i][1]);lbl.style('display',null).attr('x',pts[i][0]+10).attr('y',pts[i][1]+3).text('#'+i);}).on('mouseout',function(){hl.style('display','none');lbl.style('display','none');});}
function drawZoomScatter(host){var svg=newSvg(host).style('cursor','move');var data=d3.range(140).map(function(){return [rnorm(),rnorm()];});var x=d3.scaleLinear().domain([-3,3]).range([40,410]);var y=d3.scaleLinear().domain([-3,3]).range([205,14]);
  var gx=svg.append('g').attr('transform','translate(0,205)');var gy=svg.append('g').attr('transform','translate(40,0)');axc(gx.call(d3.axisBottom(x)));axc(gy.call(d3.axisLeft(y)));
  svg.append('clipPath').attr('id','clp_db').append('rect').attr('x',40).attr('y',14).attr('width',320).attr('height',191);
  var dots=svg.append('g').attr('clip-path','url(#clp_db)').selectAll('circle').data(data).join('circle').attr('cx',function(d){return x(d[0]);}).attr('cy',function(d){return y(d[1]);}).attr('r',3.5).attr('fill',ACCENT).attr('opacity',0.7);
  var zoom=d3.zoom().scaleExtent([1,10]).on('zoom',function(event){var tr=event.transform;var zx=tr.rescaleX(x),zy=tr.rescaleY(y);axc(gx.call(d3.axisBottom(zx)));axc(gy.call(d3.axisLeft(zy)));dots.attr('cx',function(d){return zx(d[0]);}).attr('cy',function(d){return zy(d[1]);});});svg.call(zoom);}
function drawBarRace(host){var names=['Alpha','Bravo','Charlie','Delta','Echo','Foxtrot','Golf','Hotel'];var vals=names.map(function(){return 20+Math.random()*40;});var n=names.length,rowH=28,mTop=12;
  var svg=d3.select(host).append('svg').attr('width','100%').attr('height',270).attr('viewBox','0 0 420 270');var x=d3.scaleLinear().range([120,410]);var y=d3.scaleBand().domain(d3.range(n)).range([mTop,mTop+n*rowH]).padding(0.18);var tick=0;
  function frame(){tick++;vals=vals.map(function(v){return Math.max(5,v+(Math.random()-0.45)*14);});var order=d3.range(n).sort(function(a,b){return vals[b]-vals[a];});var rank={};order.forEach(function(idx,r){rank[idx]=r;});x.domain([0,d3.max(vals)]);var t=svg.transition().duration(1400);
    var g=svg.selectAll('g.bar').data(d3.range(n),function(d){return d;});var ge=g.enter().append('g').attr('class','bar').attr('transform',function(d){return 'translate(0,'+y(rank[d])+')';});
    ge.append('rect').attr('x',120).attr('height',y.bandwidth()).attr('rx',3).attr('fill',function(d){return PAL[d%PAL.length];});ge.append('text').attr('x',114).attr('text-anchor','end').attr('dy',y.bandwidth()/2).attr('font-size',12).attr('font-family',FONT).attr('fill',INK2).text(function(d){return names[d];});
    var gm=ge.merge(g);gm.transition(t).attr('transform',function(d){return 'translate(0,'+y(rank[d])+')';});gm.select('rect').transition(t).attr('width',function(d){return x(vals[d])-120;});}
  frame();var iv=setInterval(frame,1600);return function(){clearInterval(iv);};}
function drawElastic(host){var svg=newSvg(host);var data=[40,95,150,120,70,110];var x=d3.scaleBand().domain(d3.range(data.length)).range([25,345]).padding(0.28);var y=d3.scaleLinear().domain([0,170]).range([210,12]);
  svg.selectAll('rect').data(data).join('rect').attr('x',function(_,i){return x(i);}).attr('width',x.bandwidth()).attr('rx',3).attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('y',y(0)).attr('height',0).transition().duration(1400).delay(function(_,i){return i*110;}).attr('y',function(d){return y(d);}).attr('height',function(d){return y(0)-y(d);});}
function drawGauges(host){var svg=newSvg(host);var vals=[0.72,0.45,0.88],cx=[80,180,280],r=55;var bg=d3.arc().innerRadius(r-11).outerRadius(r).startAngle(-Math.PI/2).endAngle(Math.PI/2);
  vals.forEach(function(v,i){var g=svg.append('g').attr('transform','translate('+cx[i]+',140)');g.append('path').attr('d',bg).attr('fill',GRIDC);var fg=d3.arc().innerRadius(r-11).outerRadius(r).startAngle(-Math.PI/2).cornerRadius(5);
    g.append('path').attr('fill',PAL[i%PAL.length]).transition().duration(1200).attrTween('d',function(){var ip=d3.interpolate(-Math.PI/2,-Math.PI/2+v*Math.PI);return function(t){return fg.endAngle(ip(t))();};});
    g.append('text').attr('text-anchor','middle').attr('dy',4).attr('font-weight',700).attr('font-family',FONT).attr('font-size',16).attr('fill',INK).text(Math.round(v*100)+'%');});}
function drawGUP(host){var svg=newSvg(host);var alpha='ABCDEFGHIJKLMNOP'.split('');var baseY=120;var x=d3.scaleBand().range([20,350]).padding(0.15);
  function frame(){var letters=alpha.filter(function(){return Math.random()>0.5;});x.domain(letters);var t=svg.transition().duration(750);var g=svg.selectAll('text.l').data(letters,function(d){return d;});
    g.exit().transition(t).attr('y',baseY+30).style('fill',HILITE).style('fill-opacity',0).remove();g.transition(t).attr('x',function(d){return x(d)+x.bandwidth()/2;}).style('fill',INK).style('fill-opacity',1);
    g.enter().append('text').attr('class','l').attr('text-anchor','middle').attr('font-family',FONT).attr('font-size',20).attr('y',baseY-30).attr('x',function(d){return x(d)+x.bandwidth()/2;}).style('fill',PAL[1]).style('fill-opacity',0).text(function(d){return d;}).transition(t).attr('y',baseY).style('fill-opacity',1).style('fill',INK);}
  frame();var iv=setInterval(frame,1700);return function(){clearInterval(iv);};}

// ===== More forms =====
function matrix(host){var svg=newSvg(host);var n=14;var names=d3.range(n);var m=names.map(function(){return names.map(function(){return 0;});});
  for(var k=0;k<42;k++){var a=Math.floor(Math.random()*n),b=Math.floor(Math.random()*n);if(a!==b){var w=1+Math.floor(Math.random()*4);m[a][b]=w;m[b][a]=w;}}
  var size=196;var x=d3.scaleBand().domain(names).range([0,size]).padding(0.05);var g=svg.append('g').attr('transform','translate('+((360-size)/2)+',16)');
  var c=d3.scaleSequential(d3.interpolateBlues||d3.interpolateViridis).domain([0,4]);var cells=[];names.forEach(function(i){names.forEach(function(j){cells.push({i:i,j:j,v:m[i][j]});});});
  var rects=g.selectAll('rect').data(cells).join('rect').attr('x',function(d){return x(d.j);}).attr('y',function(d){return x(d.i);}).attr('width',x.bandwidth()).attr('height',x.bandwidth()).attr('fill',function(d){return d.v?c(d.v):'#eef2f7';}).attr('stroke','#fff').attr('stroke-width',0.5)
    .on('mouseover',function(event,d){rects.attr('opacity',function(e){return (e.i===d.i||e.j===d.j)?1:0.25;});}).on('mouseout',function(){rects.attr('opacity',1);});}
function sankey(host){var svg=newSvg(host);var S=[{n:'A',v:45},{n:'B',v:30},{n:'C',v:25}];var Tt=[{n:'X',v:38},{n:'Y',v:34},{n:'Z',v:28}];
  var links=[{s:0,t:0,v:20},{s:0,t:1,v:15},{s:0,t:2,v:10},{s:1,t:0,v:12},{s:1,t:1,v:10},{s:1,t:2,v:8},{s:2,t:1,v:14},{s:2,t:2,v:11}];
  var H=185,top=18,gap=12,x1=50,x2=300,nw=14;function layout(nodes){var tot=d3.sum(nodes,function(d){return d.v;});var sc=(H-(nodes.length-1)*gap)/tot;var yy=top;nodes.forEach(function(d){d.y0=yy;d.h=d.v*sc;d.y1=yy+d.h;yy+=d.h+gap;});return sc;}
  var sc=layout(S);layout(Tt);links.forEach(function(l){l.w=l.v*sc;});
  S.forEach(function(nd,si){var o=0;links.filter(function(l){return l.s===si;}).forEach(function(l){l.sy=nd.y0+o+l.w/2;o+=l.w;});});
  Tt.forEach(function(nd,ti){var o=0;links.filter(function(l){return l.t===ti;}).forEach(function(l){l.ty=nd.y0+o+l.w/2;o+=l.w;});});
  svg.append('g').selectAll('path').data(links).join('path').attr('fill','none').attr('stroke',function(l){return PAL[l.s%PAL.length];}).attr('stroke-opacity',0.4).attr('stroke-width',function(l){return Math.max(1,l.w);}).attr('d',function(l){var xa=x1+nw,cx=(xa+x2)/2;return 'M'+xa+','+l.sy+'C'+cx+','+l.sy+' '+cx+','+l.ty+' '+x2+','+l.ty;});
  svg.append('g').selectAll('rect').data(S).join('rect').attr('x',x1).attr('y',function(d){return d.y0;}).attr('width',nw).attr('height',function(d){return d.h;}).attr('fill',function(_,i){return PAL[i%PAL.length];});
  svg.append('g').selectAll('rect').data(Tt).join('rect').attr('x',x2).attr('y',function(d){return d.y0;}).attr('width',nw).attr('height',function(d){return d.h;}).attr('fill',function(_,i){return PAL[(i+3)%PAL.length];});
  S.forEach(function(d){svg.append('text').attr('x',x1-4).attr('y',(d.y0+d.y1)/2+3).attr('text-anchor','end').attr('font-size',9).attr('font-family',FONT).attr('fill',INK).text(d.n);});
  Tt.forEach(function(d){svg.append('text').attr('x',x2+nw+4).attr('y',(d.y0+d.y1)/2+3).attr('font-size',9).attr('font-family',FONT).attr('fill',INK).text(d.n);});}
function horizon(host){var svg=newSvg(host);var N=60,data=d3.range(N).map(function(i){return Math.abs(55+40*Math.sin(i/7)+20*Math.sin(i/3)+(Math.random()-0.5)*15);});
  var bands=4,max=d3.max(data),step=max/bands,h=120;var x=d3.scaleLinear().domain([0,N-1]).range([0,360]);var yb=d3.scaleLinear().domain([0,step]).range([h,0]);var seq=d3.interpolateBlues||d3.interpolateViridis;
  for(var b=0;b<bands;b++){(function(b){svg.append('path').datum(data).attr('transform','translate(0,'+(205-h)+')').attr('fill',seq(0.3+0.6*b/bands)).attr('d',d3.area().x(function(d,i){return x(i);}).y0(h).y1(function(d){return yb(Math.max(0,Math.min(step,d-b*step)));}).curve(d3.curveBasis));})(b);}}
function bump(host){var svg=newSvg(host);var items=6,T=7;var cols=d3.range(T).map(function(){var a=d3.range(items);for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var tmp=a[i];a[i]=a[j];a[j]=tmp;}return a;});
  var rankOf=cols.map(function(c){var r=[];c.forEach(function(item,rank){r[item]=rank;});return r;});var x=d3.scalePoint().domain(d3.range(T)).range([30,345]);var y=d3.scalePoint().domain(d3.range(items)).range([18,205]);var curve=d3.curveBumpX||d3.curveMonotoneX;
  d3.range(items).forEach(function(s){var r=d3.range(T).map(function(t){return rankOf[t][s];});svg.append('path').datum(r).attr('fill','none').attr('stroke',PAL[s%PAL.length]).attr('stroke-width',3).attr('opacity',0.8).attr('d',d3.line().x(function(d,i){return x(i);}).y(function(d){return y(d);}).curve(curve));
    svg.selectAll('c'+s).data(r).enter().append('circle').attr('cx',function(d,i){return x(i);}).attr('cy',function(d){return y(d);}).attr('r',4).attr('fill',PAL[s%PAL.length]);});}
function slope(host){var svg=newSvg(host);var items=['Alpha','Bravo','Charlie','Delta','Echo'];var data=items.map(function(n,i){return {n:n,a:20+Math.random()*70,b:20+Math.random()*70,c:PAL[i%PAL.length]};});
  var y=d3.scaleLinear().domain([0,100]).range([205,22]);var xA=130,xB=250;svg.append('text').attr('x',xA).attr('y',14).attr('text-anchor','middle').attr('font-size',10).attr('font-family',FONT).attr('fill',INK2).text('Before');svg.append('text').attr('x',xB).attr('y',14).attr('text-anchor','middle').attr('font-size',10).attr('font-family',FONT).attr('fill',INK2).text('After');
  data.forEach(function(d){svg.append('line').attr('x1',xA).attr('y1',y(d.a)).attr('x2',xB).attr('y2',y(d.b)).attr('stroke',d.c).attr('stroke-width',2);svg.append('circle').attr('cx',xA).attr('cy',y(d.a)).attr('r',3).attr('fill',d.c);svg.append('circle').attr('cx',xB).attr('cy',y(d.b)).attr('r',3).attr('fill',d.c);
    svg.append('text').attr('x',xA-6).attr('y',y(d.a)+3).attr('text-anchor','end').attr('font-size',9).attr('font-family',FONT).attr('fill',INK).text(d.n);svg.append('text').attr('x',xB+6).attr('y',y(d.b)+3).attr('font-size',9).attr('font-family',FONT).attr('fill',INK).text(Math.round(d.b));});}
function waffle(host){var svg=newSvg(host);var cats=[['A',38,PAL[0]],['B',27,PAL[1]],['C',21,PAL[2]],['D',14,PAL[3]]];var cells=[];cats.forEach(function(c){for(var k=0;k<c[1];k++)cells.push(c[2]);});var cs=18,cols=10;
  cells.forEach(function(col,i){var r=Math.floor(i/cols),cc=i%cols;svg.append('rect').attr('x',120+cc*cs).attr('y',18+r*cs).attr('width',cs-3).attr('height',cs-3).attr('rx',2).attr('fill',col).attr('opacity',0).transition().duration(500).delay(i*6).attr('opacity',0.9);});
  cats.forEach(function(c,i){svg.append('rect').attr('x',10).attr('y',24+i*22).attr('width',12).attr('height',12).attr('rx',2).attr('fill',c[2]);svg.append('text').attr('x',28).attr('y',34+i*22).attr('font-size',10).attr('font-family',FONT).attr('fill',INK).text(c[0]+' — '+c[1]+'%');});}

// ===== Even more forms =====
function hexbin(host){var svg=newSvg(host);var r=13;var pts=d3.range(420).map(function(){var k=Math.random()<0.5;return [180+(k?-52:52)+rnorm()*42,115+(k?-18:26)+rnorm()*28];});
  var dx=1.5*r,dy=Math.sqrt(3)*r,centers=[];for(var cx=12;cx<356;cx+=dx){var col=Math.round((cx-12)/dx);for(var cy=12+(col%2?dy/2:0);cy<224;cy+=dy){centers.push({x:cx,y:cy,n:0});}}
  pts.forEach(function(p){var best=1e9,bc=null;centers.forEach(function(c){var a=c.x-p[0],b=c.y-p[1],d2=a*a+b*b;if(d2<best){best=d2;bc=c;}});if(bc)bc.n++;});
  var mx=d3.max(centers,function(c){return c.n;})||1;var color=d3.scaleSequential(d3.interpolateViridis).domain([0,mx]);
  function hex(cx,cy){var s='';for(var i=0;i<6;i++){var a=Math.PI/3*i,x=cx+r*0.92*Math.cos(a),y=cy+r*0.92*Math.sin(a);s+=(i?'L':'M')+x.toFixed(1)+','+y.toFixed(1);}return s+'Z';}
  centers.filter(function(c){return c.n>0;}).forEach(function(c){svg.append('path').attr('d',hex(c.x,c.y)).attr('fill',color(c.n)).attr('stroke','#fff').attr('stroke-width',0.4);});}
function wordcloud(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');
  var words=[['data',40],['viz',34],['d3',30],['chart',26],['scale',22],['axis',20],['color',19],['svg',18],['node',16],['link',15],['arc',14],['pie',13],['bar',13],['line',12],['area',12],['force',11],['tree',11],['hover',10],['zoom',10],['hex',9]];
  var placed=[];function hit(b){return placed.some(function(p){return !(b.x+b.w<p.x||b.x>p.x+p.w||b.y+b.h<p.y||b.y>p.y+p.h);});}
  words.forEach(function(w,i){var s=w[1],wpx=w[0].length*s*0.58,hpx=s,ang=0,rad=0,cx,cy,box,tries=0;
    do{cx=Math.cos(ang)*rad;cy=Math.sin(ang)*rad;box={x:cx-wpx/2,y:cy-hpx/2,w:wpx,h:hpx};ang+=0.5;rad+=1.1;tries++;}while(hit(box)&&tries<500);
    placed.push(box);g.append('text').attr('x',cx).attr('y',cy).attr('text-anchor','middle').attr('dy',s*0.34).attr('font-size',s).attr('font-weight',600).attr('font-family',FONT).attr('fill',PAL[i%PAL.length]).text(w[0]);});}
function radialStack(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,120)');var cats=d3.range(12);
  var data=cats.map(function(c){return {c:c,a:5+Math.random()*14,b:5+Math.random()*14,c2:5+Math.random()*14};});var st=d3.stack().keys(['a','b','c2'])(data);
  var x=d3.scaleBand().domain(cats).range([0,2*Math.PI]).padding(0.08);var y=d3.scaleLinear().domain([0,d3.max(data,function(d){return d.a+d.b+d.c2;})]).range([28,102]);
  st.forEach(function(layer,li){var arc=d3.arc().innerRadius(function(d){return y(d[0]);}).outerRadius(function(d){return y(d[1]);}).startAngle(function(d){return x(d.data.c);}).endAngle(function(d){return x(d.data.c)+x.bandwidth();}).padAngle(0.02);
    g.selectAll('rs'+li).data(layer).enter().append('path').attr('fill',PAL[li]).attr('d',arc);});}
function chordDirected(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var m=[[0,8,3,5],[2,0,6,4],[5,3,0,7],[4,6,2,0]];
  var ch=(d3.chordDirected?d3.chordDirected():d3.chord()).padAngle(0.05).sortSubgroups(d3.descending)(m);var arc=d3.arc().innerRadius(88).outerRadius(98);var rib=(d3.ribbonArrow?d3.ribbonArrow():d3.ribbon()).radius(86);
  g.append('g').selectAll('path').data(ch.groups).join('path').attr('d',arc).attr('fill',function(d){return PAL[d.index%PAL.length];});
  g.append('g').attr('fill-opacity',0.6).selectAll('path').data(ch).join('path').attr('d',rib).attr('fill',function(d){return PAL[d.target.index%PAL.length];}).attr('stroke','#fff').attr('stroke-width',0.3);}
function dotplot(host){var svg=newSvg(host);var cats=['A','B','C','D'];var y=d3.scaleBand().domain(cats).range([18,205]).padding(0.3);var x=d3.scaleLinear().domain([0,100]).range([42,350]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(5)));axc(svg.append('g').attr('transform','translate(42,0)').call(d3.axisLeft(y)));
  cats.forEach(function(c,ci){d3.range(32).forEach(function(){var val=Math.max(2,Math.min(98,(ci*6+42)+rnorm()*17));svg.append('circle').attr('cx',x(val)).attr('cy',y(c)+y.bandwidth()/2+(Math.random()-0.5)*y.bandwidth()*0.65).attr('r',3).attr('fill',PAL[ci%PAL.length]).attr('opacity',0.55);});});}
function gantt(host){var svg=newSvg(host);var tasks=[['Plan',0,3],['Design',2,6],['Build',5,12],['Test',10,15],['Ship',14,17]];var y=d3.scaleBand().domain(tasks.map(function(t){return t[0];})).range([18,200]).padding(0.3);var x=d3.scaleLinear().domain([0,18]).range([72,350]);
  axc(svg.append('g').attr('transform','translate(0,200)').call(d3.axisBottom(x).ticks(6)));axc(svg.append('g').attr('transform','translate(72,0)').call(d3.axisLeft(y)));
  svg.selectAll('rect').data(tasks).join('rect').attr('x',function(t){return x(t[1]);}).attr('y',function(t){return y(t[0]);}).attr('height',y.bandwidth()).attr('rx',3).attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('width',0).transition().duration(700).delay(function(_,i){return i*90;}).attr('width',function(t){return x(t[2])-x(t[1]);});}
function streamHover(host){var svg=newSvg(host);var keys=['a','b','c','d','e'];var data=d3.range(24).map(function(i){var o={i:i};keys.forEach(function(k,ki){o[k]=Math.max(0,10+8*Math.sin(i/3+ki*1.3)+Math.random()*4);});return o;});var st=d3.stack().keys(keys).offset(d3.stackOffsetWiggle)(data);
  var x=d3.scaleLinear().domain([0,23]).range([0,360]);var y=d3.scaleLinear().domain([d3.min(st,function(l){return d3.min(l,function(d){return d[0];});}),d3.max(st,function(l){return d3.max(l,function(d){return d[1];});})]).range([205,22]);
  var lbl=svg.append('text').attr('x',8).attr('y',16).attr('font-size',11).attr('font-weight',700).attr('font-family',FONT).attr('fill',INK);
  var paths=svg.selectAll('path').data(st).join('path').attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('opacity',0.9).attr('d',d3.area().x(function(d){return x(d.data.i);}).y0(function(d){return y(d[0]);}).y1(function(d){return y(d[1]);}).curve(d3.curveBasis))
    .on('mouseover',function(event,d){paths.attr('opacity',0.22);d3.select(this).attr('opacity',1);lbl.text('series '+d.key);}).on('mouseout',function(){paths.attr('opacity',0.9);lbl.text('');});}
function sunburstBread(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,122)');var data={name:'root',children:d3.range(4).map(function(i){return {name:'G'+i,children:d3.range(3).map(function(j){return {name:'c'+i+j,value:5+Math.random()*20};})};})};
  var root=d3.hierarchy(data).sum(function(d){return d.value;});d3.partition().size([2*Math.PI,98])(root);var arc=d3.arc().startAngle(function(d){return d.x0;}).endAngle(function(d){return d.x1;}).innerRadius(function(d){return d.y0;}).outerRadius(function(d){return d.y1;}).padAngle(0.004);
  var bc=svg.append('text').attr('x',8).attr('y',14).attr('font-size',10).attr('font-family',FONT).attr('fill',INK2);
  var paths=g.selectAll('path').data(root.descendants().filter(function(d){return d.depth;})).join('path').attr('fill',function(d,i){return PAL[i%PAL.length];}).attr('d',arc).attr('opacity',0.85)
    .on('mouseover',function(event,d){var anc=d.ancestors();paths.attr('opacity',function(e){return anc.indexOf(e)>=0?1:0.2;});bc.text(d.ancestors().reverse().map(function(n){return n.data.name;}).join(' / '));}).on('mouseout',function(){paths.attr('opacity',0.85);bc.text('');});}

// ===== Yet more forms =====
function funnel(host){var svg=newSvg(host);var stages=[['Visits',100],['Signups',62],['Trials',38],['Paid',19],['Renew',11]];var w=d3.scaleLinear().domain([0,100]).range([0,300]);var h=40,cx=180;
  stages.forEach(function(s,i){var y=14+i*h;var w0=w(s[1]);var w1=w(i<stages.length-1?stages[i+1][1]:s[1]*0.8);svg.append('path').attr('d','M'+(cx-w0/2)+','+y+'L'+(cx+w0/2)+','+y+'L'+(cx+w1/2)+','+(y+h-6)+'L'+(cx-w1/2)+','+(y+h-6)+'Z').attr('fill',PAL[i%PAL.length]).attr('opacity',0.85);
    svg.append('text').attr('x',cx).attr('y',y+20).attr('text-anchor','middle').attr('font-size',10).attr('font-weight',600).attr('font-family',FONT).attr('fill','#fff').text(s[0]+' '+s[1]+'%');});}
function waterfall(host){var svg=newSvg(host);var steps=[['Start',60,'t'],['Q1',25,'+'],['Q2',-15,'-'],['Q3',30,'+'],['Q4',-12,'-'],['End',0,'e']];var run=0,bars=[];
  steps.forEach(function(d){if(d[2]==='t'){run=d[1];bars.push({name:d[0],y0:0,y1:run,c:ACCENT});}else if(d[2]==='e'){bars.push({name:d[0],y0:0,y1:run,c:ACCENT});}else{var n=run+d[1];bars.push({name:d[0],y0:run,y1:n,c:d[1]>=0?'#2EB88A':'#DD2C4D'});run=n;}});
  var x=d3.scaleBand().domain(bars.map(function(b){return b.name;})).range([35,350]).padding(0.3);var y=d3.scaleLinear().domain([0,110]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x)));axc(svg.append('g').attr('transform','translate(35,0)').call(d3.axisLeft(y).ticks(4)));
  bars.forEach(function(b){svg.append('rect').attr('x',x(b.name)).attr('width',x.bandwidth()).attr('y',y(Math.max(b.y0,b.y1))).attr('height',Math.max(1,Math.abs(y(b.y0)-y(b.y1)))).attr('fill',b.c).attr('rx',1);});}
function pyramid(host){var svg=newSvg(host);var ages=['0-14','15-29','30-44','45-59','60-74','75+'];var data=ages.map(function(a,i){return {a:a,m:20-i*2+Math.random()*5,f:19-i*1.8+Math.random()*5};});
  var y=d3.scaleBand().domain(ages).range([22,205]).padding(0.22);var cx=180;var xw=d3.scaleLinear().domain([0,25]).range([0,150]);
  data.forEach(function(d){svg.append('rect').attr('x',cx-xw(d.m)).attr('y',y(d.a)).attr('width',xw(d.m)).attr('height',y.bandwidth()).attr('fill',PAL[0]);svg.append('rect').attr('x',cx).attr('y',y(d.a)).attr('width',xw(d.f)).attr('height',y.bandwidth()).attr('fill',PAL[2]);
    svg.append('text').attr('x',cx).attr('y',y(d.a)+y.bandwidth()/2+3).attr('text-anchor','middle').attr('font-size',7).attr('font-family',FONT).attr('fill',INK).text(d.a);});
  svg.append('text').attr('x',cx-80).attr('y',14).attr('text-anchor','middle').attr('font-size',9).attr('fill',PAL[0]).attr('font-family',FONT).text('Male');svg.append('text').attr('x',cx+80).attr('y',14).attr('text-anchor','middle').attr('font-size',9).attr('fill',PAL[2]).attr('font-family',FONT).text('Female');}
function punchcard(host){var svg=newSvg(host);var days=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];var x=d3.scaleLinear().domain([0,23]).range([44,352]);var y=d3.scaleBand().domain(days).range([15,200]).padding(0.25);var r=d3.scaleSqrt().domain([0,10]).range([0,y.bandwidth()/2]);
  axc(svg.append('g').attr('transform','translate(0,200)').call(d3.axisBottom(x).ticks(8)));axc(svg.append('g').attr('transform','translate(44,0)').call(d3.axisLeft(y)));
  days.forEach(function(d,di){d3.range(24).forEach(function(h){var v=Math.max(0,(di<5?1:0.4)*(8*Math.exp(-Math.pow(h-14,2)/40))+Math.random()*2);if(v>0.3)svg.append('circle').attr('cx',x(h)).attr('cy',y(d)+y.bandwidth()/2).attr('r',r(v)).attr('fill',ACCENT).attr('opacity',0.7);});});}

// ===== Variants =====
function pct100(host){var svg=newSvg(host);var cats=['Q1','Q2','Q3','Q4'],keys=['a','b','c'];var data=cats.map(function(c){var o={cat:c};keys.forEach(function(k){o[k]=10+Math.random()*30;});return o;});var st=d3.stack().keys(keys).offset(d3.stackOffsetExpand)(data);var x=d3.scaleBand().domain(cats).range([35,350]).padding(0.3);var y=d3.scaleLinear().domain([0,1]).range([205,12]);axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x)));svg.append('g').selectAll('g').data(st).join('g').attr('fill',function(_,i){return PAL[i%PAL.length];}).selectAll('rect').data(function(d){return d;}).join('rect').attr('x',function(d){return x(d.data.cat);}).attr('width',x.bandwidth()).attr('y',function(d){return y(d[1]);}).attr('height',function(d){return y(d[0])-y(d[1]);});}
function hgroup(host){var svg=newSvg(host);var cats=['A','B','C','D'],keys=['x','y'];var data=cats.map(function(c){return {c:c,x:20+Math.random()*60,y:20+Math.random()*60};});var y0=d3.scaleBand().domain(cats).range([15,205]).padding(0.25);var y1=d3.scaleBand().domain(keys).range([0,y0.bandwidth()]).padding(0.1);var x=d3.scaleLinear().domain([0,90]).range([40,350]);axc(svg.append('g').attr('transform','translate(40,0)').call(d3.axisLeft(y0)));var g=svg.selectAll('g.gg').data(data).join('g').attr('class','gg').attr('transform',function(d){return 'translate(0,'+y0(d.c)+')';});keys.forEach(function(k,ki){g.append('rect').attr('x',40).attr('y',y1(k)).attr('height',y1.bandwidth()).attr('fill',PAL[ki]).attr('width',function(d){return x(d[k])-40;});});}
function gradArea(host){var svg=newSvg(host);var defs=svg.append('defs');var grad=defs.append('linearGradient').attr('id','agx').attr('x1','0').attr('y1','0').attr('x2','0').attr('y2','1');grad.append('stop').attr('offset','0%').attr('stop-color',ACCENT).attr('stop-opacity',0.8);grad.append('stop').attr('offset','100%').attr('stop-color',ACCENT).attr('stop-opacity',0.05);var data=d3.range(30).map(function(i){return [i,45+25*Math.sin(i/4)+Math.random()*8];});var x=d3.scaleLinear().domain([0,29]).range([8,352]);var y=d3.scaleLinear().domain([0,100]).range([210,10]);svg.append('path').datum(data).attr('fill','url(#agx)').attr('d',d3.area().x(function(d){return x(d[0]);}).y0(210).y1(function(d){return y(d[1]);}).curve(d3.curveCatmullRom));svg.append('path').datum(data).attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',2).attr('d',d3.line().x(function(d){return x(d[0]);}).y(function(d){return y(d[1]);}).curve(d3.curveCatmullRom));}
function stepline(host){var svg=newSvg(host);var data=d3.range(16).map(function(i){return [i,40+30*Math.sin(i/3)+Math.random()*8];});var x=d3.scaleLinear().domain([0,15]).range([30,350]);var y=d3.scaleLinear().domain([0,100]).range([205,12]);axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(6)));svg.append('path').datum(data).attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',2).attr('d',d3.line().x(function(d){return x(d[0]);}).y(function(d){return y(d[1]);}).curve(d3.curveStepAfter));}
function radialLine(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,118)');var N=24;var data=d3.range(N).map(function(i){return 40+25*Math.sin(i/3)+Math.random()*10;});var ang=d3.scaleLinear().domain([0,N]).range([0,2*Math.PI]);var r=d3.scaleLinear().domain([0,80]).range([20,100]);[20,40,60,80].forEach(function(t){g.append('circle').attr('r',r(t)).attr('fill','none').attr('stroke',GRIDC);});var line=d3.lineRadial().angle(function(d,i){return ang(i);}).radius(function(d){return r(d);}).curve(d3.curveCardinalClosed);g.append('path').datum(data).attr('fill',ACCENT).attr('opacity',0.25).attr('stroke',ACCENT).attr('stroke-width',2).attr('d',line);}
function nestedDonut(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var pie=d3.pie().sort(null);var outer=d3.arc().innerRadius(70).outerRadius(96).padAngle(0.01);var inner=d3.arc().innerRadius(40).outerRadius(68).padAngle(0.01);g.selectAll('po').data(pie([30,22,18,16,14])).enter().append('path').attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('d',outer);g.selectAll('pi').data(pie([25,25,20,18,12])).enter().append('path').attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('opacity',0.5).attr('d',inner);}

// ===== d3og extras =====
function liquidGauge(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,120)');var Rr=72;var level=0.3+Math.random()*0.5;
  svg.append('clipPath').attr('id','lg').append('circle').attr('r',Rr-3);g.append('circle').attr('r',Rr).attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',3);
  var wave=g.append('path').attr('clip-path','url(#lg)').attr('fill',ACCENT).attr('opacity',0.45);var W=2*Rr,pts=44,phase=0;
  function frame(){phase+=0.14;var yl=Rr-2*Rr*level;var d='M'+(-Rr)+','+Rr;for(var i=0;i<=pts;i++){var x=-Rr+W*i/pts;var y=yl+6*Math.sin(i/pts*4*Math.PI+phase);d+='L'+x.toFixed(1)+','+y.toFixed(1);}wave.attr('d',d+'L'+Rr+','+Rr+'Z');}
  frame();var iv=setInterval(frame,55);g.append('text').attr('text-anchor','middle').attr('dy',6).attr('font-size',22).attr('font-weight',700).attr('font-family',FONT).attr('fill',INK).text(Math.round(level*100)+'%');return function(){clearInterval(iv);};}
function phyllotaxis(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var n=500,c=4.4,ga=Math.PI*(3-Math.sqrt(5));var color=d3.scaleSequential(d3.interpolateViridis).domain([0,n]);
  g.selectAll('circle').data(d3.range(n)).join('circle').attr('r',3).attr('fill',function(i){return color(i);}).attr('cx',function(i){return Math.cos(i*ga)*c*Math.sqrt(i);}).attr('cy',function(i){return Math.sin(i*ga)*c*Math.sqrt(i);}).attr('opacity',0).transition().duration(1200).delay(function(i){return i*2;}).attr('opacity',0.85);}
function shapeTween(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var N=60,Rr=80;
  function circle(){return d3.range(N).map(function(i){var a=i/N*2*Math.PI;return [Math.cos(a)*Rr,Math.sin(a)*Rr];});}
  function star(){return d3.range(N).map(function(i){var a=i/N*2*Math.PI;var rr=(i%(N/5)<N/10)?Rr:Rr*0.45;return [Math.cos(a)*rr,Math.sin(a)*rr];});}
  function toP(p){return 'M'+p.map(function(q){return q[0].toFixed(1)+','+q[1].toFixed(1);}).join('L')+'Z';}
  var path=g.append('path').attr('fill',ACCENT).attr('opacity',0.6).attr('stroke',ACCENT).attr('stroke-width',2).attr('d',toP(circle()));var s=0;
  function frame(){s=1-s;var from=s?circle():star(),to=s?star():circle();var ip=d3.interpolate(from,to);path.transition().duration(1500).attrTween('d',function(){return function(t){return toP(ip(t));};});}
  frame();var iv=setInterval(frame,1900);return function(){clearInterval(iv);};}
function sortableBar(host){var svg=newSvg(host);var data=d3.range(10).map(function(i){return {k:'I'+i,v:10+Math.random()*80};});var y=d3.scaleLinear().domain([0,95]).range([205,15]);var x=d3.scaleBand().range([30,350]).padding(0.2);var asc=false;
  function draw(){var order=data.slice().sort(function(a,b){return asc?a.v-b.v:b.v-a.v;});x.domain(order.map(function(d){return d.k;}));var bars=svg.selectAll('rect').data(data,function(d){return d.k;});
    bars.enter().append('rect').attr('fill',ACCENT).attr('rx',2).attr('y',function(d){return y(d.v);}).attr('height',function(d){return 205-y(d.v);}).merge(bars).transition().duration(900).attr('x',function(d){return x(d.k);}).attr('width',x.bandwidth()).attr('y',function(d){return y(d.v);}).attr('height',function(d){return 205-y(d.v);});}
  draw();var iv=setInterval(function(){asc=!asc;draw();},2200);return function(){clearInterval(iv);};}
function splom(host){var svg=newSvg(host);var vars=['a','b','c'];var data=d3.range(60).map(function(){return {a:Math.random(),b:Math.random(),c:Math.random()*0.6+0.2};});var pad=8,size=(222-pad*2)/3;var sc=d3.scaleLinear().domain([0,1]).range([0,size]);
  vars.forEach(function(vx,i){vars.forEach(function(vy,j){var cell=svg.append('g').attr('transform','translate('+(12+i*(size+pad))+','+(6+j*(size+pad))+')');cell.append('rect').attr('width',size).attr('height',size).attr('fill','none').attr('stroke',GRIDC);
    if(i===j){cell.append('text').attr('x',size/2).attr('y',size/2+4).attr('text-anchor','middle').attr('font-size',12).attr('font-weight',700).attr('font-family',FONT).attr('fill',INK).text(vx.toUpperCase());}else{cell.selectAll('circle').data(data).join('circle').attr('cx',function(d){return sc(d[vx]);}).attr('cy',function(d){return size-sc(d[vy]);}).attr('r',2).attr('fill',PAL[(i+j)%PAL.length]).attr('opacity',0.5);}});});}
function divergingBar(host){var svg=newSvg(host);var items=['Q1','Q2','Q3','Q4','Q5'];var data=items.map(function(q){return {q:q,sd:5+Math.random()*12,d:8+Math.random()*14,a:8+Math.random()*16,sa:5+Math.random()*14};});var y=d3.scaleBand().domain(items).range([18,205]).padding(0.3);var x=d3.scaleLinear().domain([-50,50]).range([35,350]);var cx=x(0);
  svg.append('line').attr('x1',cx).attr('x2',cx).attr('y1',12).attr('y2',205).attr('stroke',INK2);
  data.forEach(function(d){svg.append('rect').attr('x',x(-(d.sd+d.d))).attr('width',x(-d.d)-x(-(d.sd+d.d))).attr('y',y(d.q)).attr('height',y.bandwidth()).attr('fill',PAL[4]).attr('opacity',0.5);
    svg.append('rect').attr('x',x(-d.d)).attr('width',cx-x(-d.d)).attr('y',y(d.q)).attr('height',y.bandwidth()).attr('fill',PAL[4]);
    svg.append('rect').attr('x',cx).attr('width',x(d.a)-cx).attr('y',y(d.q)).attr('height',y.bandwidth()).attr('fill',PAL[1]);
    svg.append('rect').attr('x',x(d.a)).attr('width',x(d.a+d.sa)-x(d.a)).attr('y',y(d.q)).attr('height',y.bandwidth()).attr('fill',PAL[1]).attr('opacity',0.5);
    svg.append('text').attr('x',6).attr('y',y(d.q)+y.bandwidth()/2+3).attr('font-size',9).attr('font-family',FONT).attr('fill',INK2).text(d.q);});}
function waveMotion(host){var svg=newSvg(host);var W=360,layers=4;var x=d3.scaleLinear().domain([0,100]).range([0,W]);var paths=d3.range(layers).map(function(l){return svg.append('path').attr('fill','none').attr('stroke',PAL[l%PAL.length]).attr('stroke-width',2).attr('opacity',0.7);});var phase=0;
  function frame(){phase+=0.1;paths.forEach(function(p,l){var d='';for(var i=0;i<=100;i++){var yy=115+(30-l*5)*Math.sin(i/8+phase+l*0.8);d+=(i?'L':'M')+x(i).toFixed(1)+','+yy.toFixed(1);}p.attr('d',d);});}
  frame();var iv=setInterval(frame,40);return function(){clearInterval(iv);};}
function gradientStroke(host){var svg=newSvg(host);var defs=svg.append('defs');var lg=defs.append('linearGradient').attr('id','gs').attr('x1','0').attr('x2','1');lg.append('stop').attr('offset','0%').attr('stop-color',PAL[0]);lg.append('stop').attr('offset','50%').attr('stop-color',PAL[2]);lg.append('stop').attr('offset','100%').attr('stop-color',PAL[4]);
  var data=d3.range(40).map(function(i){return [i,60+40*Math.sin(i/5)+Math.random()*6];});var x=d3.scaleLinear().domain([0,39]).range([15,350]);var y=d3.scaleLinear().domain([0,120]).range([205,12]);
  svg.append('path').datum(data).attr('fill','none').attr('stroke','url(#gs)').attr('stroke-width',3).attr('d',d3.line().x(function(d){return x(d[0]);}).y(function(d){return y(d[1]);}).curve(d3.curveBasis));}

// ===== Generative / algorithmic =====
function mazeGen(host){var svg=newSvg(host);var cs=16,cols=20,rows=13,ox=20,oy=6;
  var cells=[];for(var r=0;r<rows;r++)for(var c=0;c<cols;c++)cells.push({c:c,r:r,v:false,walls:[true,true,true,true]});
  function idx(c,r){return (c<0||r<0||c>=cols||r>=rows)?-1:r*cols+c;}
  var g=svg.append('g').attr('transform','translate('+ox+','+oy+')');
  var wallSel=g.append('g').attr('stroke',ACCENT).attr('stroke-width',1.3).attr('stroke-linecap','round');
  var hl=g.append('rect').attr('width',cs).attr('height',cs).attr('fill',PAL[3]).attr('opacity',0.6);
  var cur=cells[0];cur.v=true;var stack=[];
  function drawWalls(){wallSel.selectAll('line').remove();cells.forEach(function(cell){var x=cell.c*cs,y=cell.r*cs;if(cell.walls[0])wallSel.append('line').attr('x1',x).attr('y1',y).attr('x2',x+cs).attr('y2',y);if(cell.walls[1])wallSel.append('line').attr('x1',x+cs).attr('y1',y).attr('x2',x+cs).attr('y2',y+cs);if(cell.walls[2])wallSel.append('line').attr('x1',x).attr('y1',y+cs).attr('x2',x+cs).attr('y2',y+cs);if(cell.walls[3])wallSel.append('line').attr('x1',x).attr('y1',y).attr('x2',x).attr('y2',y+cs);});}
  function step(){var nb=[];var dirs=[[0,-1,0,2],[1,0,1,3],[0,1,2,0],[-1,0,3,1]];dirs.forEach(function(dd){var ni=idx(cur.c+dd[0],cur.r+dd[1]);if(ni>=0&&!cells[ni].v)nb.push({cell:cells[ni],w:dd[2],ow:dd[3]});});
    if(nb.length){var ch=nb[Math.floor(Math.random()*nb.length)];stack.push(cur);cur.walls[ch.w]=false;ch.cell.walls[ch.ow]=false;cur=ch.cell;cur.v=true;}else if(stack.length){cur=stack.pop();}
    hl.attr('x',cur.c*cs).attr('y',cur.r*cs);}
  drawWalls();var iv=setInterval(function(){for(var k=0;k<3;k++)step();drawWalls();if(stack.length===0&&cells.every(function(c){return c.v;})){clearInterval(iv);hl.remove();}},45);
  return function(){clearInterval(iv);};}
function quickSort(host){var svg=newSvg(host);var n=28;var data=d3.range(n).map(function(i){return i+1;});for(var q=n-1;q>0;q--){var j0=Math.floor(Math.random()*(q+1));var tt=data[q];data[q]=data[j0];data[j0]=tt;}
  var x=d3.scaleBand().domain(d3.range(n)).range([15,350]).padding(0.12);var y=d3.scaleLinear().domain([0,n]).range([210,12]);
  var frames=[];var arr=data.slice();
  function rec(lo,hi){if(lo>=hi)return;var pivot=arr[hi],i=lo;for(var j=lo;j<hi;j++){if(arr[j]<pivot){var t=arr[i];arr[i]=arr[j];arr[j]=t;frames.push({a:arr.slice(),hi:[i,j],piv:hi});i++;}}var t2=arr[i];arr[i]=arr[hi];arr[hi]=t2;frames.push({a:arr.slice(),hi:[i,hi],piv:i});rec(lo,i-1);rec(i+1,hi);}
  rec(0,n-1);frames.push({a:arr.slice(),hi:[],piv:-1});
  svg.selectAll('rect').data(d3.range(n)).join('rect').attr('x',function(i){return x(i);}).attr('width',x.bandwidth()).attr('rx',1);
  var fi=0;function render(){var f=frames[fi];svg.selectAll('rect').attr('y',function(i){return y(f.a[i]);}).attr('height',function(i){return 210-y(f.a[i]);}).attr('fill',function(i){return f.hi.indexOf(i)>=0?PAL[4]:(i===f.piv?PAL[3]:ACCENT);});}
  render();var iv=setInterval(function(){fi++;if(fi>=frames.length){clearInterval(iv);svg.selectAll('rect').attr('fill',PAL[1]);return;}render();},110);
  return function(){clearInterval(iv);};}
function poisson(host){var svg=newSvg(host);var W=340,H=210,r=14,k=18,cs=r/Math.SQRT2;var gw=Math.ceil(W/cs),gh=Math.ceil(H/cs);var grid=new Array(gw*gh).fill(-1);var pts=[],active=[];var g=svg.append('g').attr('transform','translate(10,10)');var color=d3.scaleSequential(d3.interpolateViridis).domain([0,320]);
  function far(x,y){var gx=Math.floor(x/cs),gy=Math.floor(y/cs);for(var i=Math.max(0,gx-2);i<=Math.min(gw-1,gx+2);i++)for(var j=Math.max(0,gy-2);j<=Math.min(gh-1,gy+2);j++){var id=grid[i+j*gw];if(id>=0){var p=pts[id];if((p[0]-x)*(p[0]-x)+(p[1]-y)*(p[1]-y)<r*r)return false;}}return true;}
  function add(x,y){var id=pts.length;pts.push([x,y]);active.push(id);grid[Math.floor(x/cs)+Math.floor(y/cs)*gw]=id;g.append('circle').attr('cx',x).attr('cy',y).attr('r',0).attr('fill',color(id)).attr('opacity',0.82).transition().duration(300).attr('r',3);}
  add(W/2,H/2);
  var iv=setInterval(function(){var tries=0;while(active.length&&tries<28){tries++;var ai=Math.floor(Math.random()*active.length);var p=pts[active[ai]];var found=false;for(var s=0;s<k;s++){var ang=Math.random()*2*Math.PI,rad=r*(1+Math.random());var nx=p[0]+Math.cos(ang)*rad,ny=p[1]+Math.sin(ang)*rad;if(nx>=0&&nx<W&&ny>=0&&ny<H&&far(nx,ny)){add(nx,ny);found=true;break;}}if(!found)active.splice(ai,1);}if(!active.length)clearInterval(iv);},45);
  return function(){clearInterval(iv);};}
function lorenz(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,122)');var sigma=10,rho=28,beta=8/3,dt=0.008;var x=0.1,y=0,z=0;var pts=[];var scale=4;var color=d3.scaleSequential(d3.interpolateViridis).domain([0,1500]);var i=0;var ln=d3.line();
  function frame(){var seg=[];if(pts.length)seg.push(pts[pts.length-1]);for(var s=0;s<7;s++){var dx=sigma*(y-x),dy=x*(rho-z)-y,dz=x*y-beta*z;x+=dx*dt;y+=dy*dt;z+=dz*dt;var pt=[x*scale,(z-27)*scale];pts.push(pt);seg.push(pt);}
    g.append('path').attr('d',ln(seg)).attr('fill','none').attr('stroke',color(i)).attr('stroke-width',1).attr('opacity',0.85);
    i+=7;if(i>1480)clearInterval(iv);}
  var iv=setInterval(frame,28);return function(){clearInterval(iv);};}
function particles(host){var svg=newSvg(host);var W=360,H=230,N=38;var nodes=d3.range(N).map(function(){return {x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-0.5)*1.2,vy:(Math.random()-0.5)*1.2};});
  var linkG=svg.append('g').attr('stroke',ACCENT);var dots=svg.append('g').selectAll('circle').data(nodes).join('circle').attr('r',2.5).attr('fill',ACCENT);
  function frame(){nodes.forEach(function(n){n.x+=n.vx;n.y+=n.vy;if(n.x<0||n.x>W)n.vx*=-1;if(n.y<0||n.y>H)n.vy*=-1;});
    dots.attr('cx',function(d){return d.x;}).attr('cy',function(d){return d.y;});
    var segs=[];for(var i=0;i<N;i++)for(var j=i+1;j<N;j++){var dx=nodes[i].x-nodes[j].x,dy=nodes[i].y-nodes[j].y,d2=dx*dx+dy*dy;if(d2<3600)segs.push({a:nodes[i],b:nodes[j],o:1-Math.sqrt(d2)/60});}
    var ls=linkG.selectAll('line').data(segs);ls.enter().append('line').merge(ls).attr('x1',function(s){return s.a.x;}).attr('y1',function(s){return s.a.y;}).attr('x2',function(s){return s.b.x;}).attr('y2',function(s){return s.b.y;}).attr('stroke-width',0.6).attr('opacity',function(s){return s.o*0.5;});ls.exit().remove();}
  var iv=setInterval(frame,33);return function(){clearInterval(iv);};}


/* ===== d3og.com classics (v3/v4 -> v7, ported) ===== */
function gen(depth,p){ if(depth===0) return {name:p, size:100+Math.floor(Math.random()*900)}; var n=2+Math.floor(Math.random()*3); var k=[]; for(var i=0;i<n;i++)k.push(gen(depth-1,p+'.'+i)); return {name:p, children:k}; }
var DATA={name:'flare', children:d3.range(4).map(function(i){return {name:'group'+i, children:d3.range(3).map(function(j){return gen(2,'g'+i+j);})};})};

// ===== Zoomable circle packing (v4 -> v7) =====
function circlePack(host){var diameter=330,margin=16;var svg=d3.select(host).append('svg').attr('width','100%').attr('height',330).attr('viewBox','0 0 '+diameter+' '+diameter).style('cursor','pointer');
  var g=svg.append('g').attr('transform','translate('+diameter/2+','+diameter/2+')');var color=d3.scaleLinear().domain([-1,5]).range(['hsl(152,80%,80%)','hsl(228,30%,40%)']).interpolate(d3.interpolateHcl||d3.interpolateRgb);
  var pack=d3.pack().size([diameter-margin,diameter-margin]).padding(2);var root=d3.hierarchy(DATA).sum(function(d){return d.size;}).sort(function(a,b){return b.value-a.value;});
  var focus=root,nodes=pack(root).descendants(),view;
  var circle=g.selectAll('circle').data(nodes).enter().append('circle').style('fill',function(d){return d.children?color(d.depth):'#fff';}).style('stroke','#fff').style('stroke-opacity',0.4).style('cursor','pointer').on('click',function(event,d){if(focus!==d){zoom(event,d);event.stopPropagation();}});
  var text=g.selectAll('text').data(nodes).enter().append('text').style('font','9px '+FONT).attr('text-anchor','middle').style('pointer-events','none').style('fill-opacity',function(d){return d.parent===root?1:0;}).style('display',function(d){return d.parent===root?'inline':'none';}).style('text-shadow','0 1px 0 #fff,1px 0 0 #fff,-1px 0 0 #fff,0 -1px 0 #fff').text(function(d){return d.data.name;});
  var node=g.selectAll('circle,text');svg.style('background',color(-1)).on('click',function(event){zoom(event,root);});zoomTo([root.x,root.y,root.r*2+margin]);
  function zoom(event,d){focus=d;var tr=d3.transition().duration(event&&event.altKey?2500:750).tween('zoom',function(){var i=d3.interpolateZoom(view,[focus.x,focus.y,focus.r*2+margin]);return function(t){zoomTo(i(t));};});
    text.filter(function(dd){return dd.parent===focus||this.style.display==='inline';}).transition(tr).style('fill-opacity',function(dd){return dd.parent===focus?1:0;}).on('start',function(dd){if(dd.parent===focus)this.style.display='inline';}).on('end',function(dd){if(dd.parent!==focus)this.style.display='none';});}
  function zoomTo(v){var k=diameter/v[2];view=v;node.attr('transform',function(d){return 'translate('+(d.x-v[0])*k+','+(d.y-v[1])*k+')';});circle.attr('r',function(d){return d.r*k;});}}
// ===== Collapsible indented tree (v4 -> v7) =====
function indentedTree(host){var margin={top:16,right:16,bottom:16,left:16},width=420,barHeight=20,barWidth=(width-32)*0.8;var i=0,duration=400,root;var diagonal=d3.linkHorizontal().x(function(d){return d.y;}).y(function(d){return d.x;});
  var svgEl=d3.select(host).append('svg').attr('width',width).attr('height',300).style('max-width','100%').style('height','auto');var svg=svgEl.append('g').attr('transform','translate(16,16)');
  root=d3.hierarchy(DATA);root.x0=0;root.y0=0;root.each(function(d){if(d.depth>=2&&d.children){d._children=d.children;d.children=null;}});update(root);
  function update(source){var nodes=root.descendants();var height=Math.max(120,nodes.length*barHeight+32);svgEl.transition().duration(duration).attr('height',height);var index=-1;root.eachBefore(function(n){n.x=++index*barHeight;n.y=n.depth*20;});
    var node=svg.selectAll('.node').data(nodes,function(d){return d.id||(d.id=++i);});var nodeEnter=node.enter().append('g').attr('class','node').attr('transform',function(){return 'translate('+source.y0+','+source.x0+')';}).style('opacity',0);
    nodeEnter.append('rect').attr('y',-barHeight/2).attr('height',barHeight).attr('width',barWidth).style('fill',color).style('fill-opacity',0.6).style('stroke',ACCENT).style('stroke-width','1.5px').style('cursor','pointer').on('click',click);
    nodeEnter.append('text').attr('dy',3.5).attr('dx',5.5).style('font','10px '+FONT).style('pointer-events','none').text(function(d){return d.data.name;});
    nodeEnter.transition().duration(duration).attr('transform',function(d){return 'translate('+d.y+','+d.x+')';}).style('opacity',1);
    node.transition().duration(duration).attr('transform',function(d){return 'translate('+d.y+','+d.x+')';}).style('opacity',1).select('rect').style('fill',color);
    node.exit().transition().duration(duration).attr('transform',function(){return 'translate('+source.y+','+source.x+')';}).style('opacity',0).remove();
    var link=svg.selectAll('.link').data(root.links(),function(d){return d.target.id;});
    link.enter().insert('path','g').attr('class','link').style('fill','none').style('stroke','#9ecae1').style('stroke-width','1.5px').attr('d',function(){var o={x:source.x0,y:source.y0};return diagonal({source:o,target:o});}).transition().duration(duration).attr('d',diagonal);
    link.transition().duration(duration).attr('d',diagonal);link.exit().transition().duration(duration).attr('d',function(){var o={x:source.x,y:source.y};return diagonal({source:o,target:o});}).remove();root.each(function(d){d.x0=d.x;d.y0=d.y;});}
  function click(event,d){if(d.children){d._children=d.children;d.children=null;}else{d.children=d._children;d._children=null;}update(d);}
  function color(d){return d._children?'#3182bd':d.children?'#c6dbef':'#fd8d3c';}}
// ===== Bullet charts (reimplemented core d3) =====
function bullet(host){var svg=newSvg(host);var rows=[['Revenue',[150,225,300],220,250],['Profit %',[20,40,60],48,55],['Orders',[200,400,600],510,560],['NPS',[20,50,80],62,70]];
  var rowH=50;rows.forEach(function(r,i){var y=14+i*rowH;var max=r[1][2];var x=d3.scaleLinear().domain([0,max]).range([80,352]);var rg=r[1];
    [[rg[2],'#eef2f7'],[rg[1],'#dde5ee'],[rg[0],'#c7d2de']].forEach(function(b){svg.append('rect').attr('x',80).attr('y',y).attr('width',x(b[0])-80).attr('height',22).attr('fill',b[1]);});
    svg.append('rect').attr('x',80).attr('y',y+6).attr('width',x(r[2])-80).attr('height',10).attr('fill',ACCENT);
    svg.append('line').attr('x1',x(r[3])).attr('x2',x(r[3])).attr('y1',y+1).attr('y2',y+21).attr('stroke',INK).attr('stroke-width',2.5);
    svg.append('text').attr('x',74).attr('y',y+15).attr('text-anchor','end').attr('font-size',10).attr('font-weight',600).attr('font-family',FONT).attr('fill',INK2).text(r[0]);});}
// ===== Calendar heatmap (manual dates) =====
function calendar(host){var svg=d3.select(host).append('svg').attr('width','100%').attr('height',130).attr('viewBox','0 0 360 130');var cs=9;var color=d3.scaleSequential(d3.interpolateGreens||d3.interpolateViridis).domain([0,1]);
  var start=new Date(2025,0,1);var day0=start.getDay();var mlab={};
  for(var dd=0;dd<245;dd++){var dt=new Date(2025,0,1+dd);var wk=Math.floor((dd+day0)/7);var wd=dt.getDay();var v=Math.max(0,Math.min(1,0.5+0.4*Math.sin(dd/9)+(Math.random()-0.5)*0.4));
    svg.append('rect').attr('x',22+wk*cs).attr('y',16+wd*cs).attr('width',cs-1.5).attr('height',cs-1.5).attr('rx',1.5).attr('fill',color(v));
    if(dt.getDate()===1){mlab[wk]=dt.toLocaleString('en',{month:'short'});}}
  Object.keys(mlab).forEach(function(wk){svg.append('text').attr('x',22+wk*cs).attr('y',10).attr('font-size',8).attr('font-family',FONT).attr('fill',INK2).text(mlab[wk]);});
  ['S','M','T','W','T','F','S'].forEach(function(d,i){svg.append('text').attr('x',16).attr('y',16+i*cs+7).attr('text-anchor','end').attr('font-size',7).attr('font-family',FONT).attr('fill',INK2).text(d);});}
// ===== Collision detection (interactive — mouse pushes nodes) =====
function collision(host){var svg=newSvg(host);var W=360,H=230,n=70;var nodes=d3.range(n).map(function(i){return {r:3+Math.random()*13,c:PAL[i%PAL.length]};});
  var sim=d3.forceSimulation(nodes).force('charge',d3.forceManyBody().strength(3)).force('center',d3.forceCenter(W/2,H/2)).force('collide',d3.forceCollide().radius(function(d){return d.r+1;}).iterations(2)).alphaDecay(0.015);
  var circle=svg.append('g').selectAll('circle').data(nodes).join('circle').attr('r',function(d){return d.r;}).attr('fill',function(d){return d.c;}).attr('opacity',0.85);
  sim.on('tick',function(){circle.attr('cx',function(d){return d.x;}).attr('cy',function(d){return d.y;});});
  svg.append('rect').attr('width',W).attr('height',H).attr('fill','transparent').on('mousemove',function(event){var p=d3.pointer(event);nodes[0].fx=p[0];nodes[0].fy=p[1];sim.alphaTarget(0.3).restart();}).on('mouseout',function(){nodes[0].fx=null;nodes[0].fy=null;sim.alphaTarget(0);});
  return function(){sim.stop();};}
// ===== Grouped bar chart =====
function groupedBar(host){var svg=newSvg(host);var cats=['Q1','Q2','Q3','Q4'];var keys=['a','b','c'];var data=cats.map(function(c){return {c:c,a:30+Math.random()*55,b:30+Math.random()*55,c2:30+Math.random()*55};});
  var x0=d3.scaleBand().domain(cats).range([35,352]).padding(0.22);var x1=d3.scaleBand().domain(keys).range([0,x0.bandwidth()]).padding(0.06);var y=d3.scaleLinear().domain([0,95]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x0)));axc(svg.append('g').attr('transform','translate(35,0)').call(d3.axisLeft(y).ticks(4)));
  var g=svg.selectAll('g.grp').data(data).join('g').attr('class','grp').attr('transform',function(d){return 'translate('+x0(d.c)+',0)';});
  keys.forEach(function(k,ki){var val=function(d){return k==='a'?d.a:(k==='b'?d.b:d.c2);};g.append('rect').attr('x',x1(k)).attr('width',x1.bandwidth()).attr('rx',1).attr('fill',PAL[ki]).attr('y',y(0)).attr('height',0).transition().duration(800).delay(ki*120).attr('y',function(d){return y(val(d));}).attr('height',function(d){return y(0)-y(val(d));});});}
// ===== Line transition (live updating) =====
function lineTransition(host){var svg=newSvg(host);var n=48;var data=d3.range(n).map(function(){return Math.random();});var x=d3.scaleLinear().domain([0,n-1]).range([5,355]);var y=d3.scaleLinear().domain([0,1]).range([205,15]);
  var line=d3.line().x(function(d,i){return x(i);}).y(function(d){return y(d);}).curve(d3.curveBasis);
  var path=svg.append('path').datum(data).attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',2).attr('d',line);
  var area=svg.insert('path','path').datum(data).attr('fill',ACCENT).attr('opacity',0.12).attr('d',d3.area().x(function(d,i){return x(i);}).y0(210).y1(function(d){return y(d);}).curve(d3.curveBasis));
  function frame(){data.push(Math.random());data.shift();path.datum(data).attr('d',line);area.datum(data).attr('d',d3.area().x(function(d,i){return x(i);}).y0(210).y1(function(d){return y(d);}).curve(d3.curveBasis));}
  var iv=setInterval(frame,950);return function(){clearInterval(iv);};}
// ===== Difference chart (clipped areas) =====
function differenceChart(host){var svg=newSvg(host);var N=44;var data=d3.range(N).map(function(i){return {i:i,a:55+22*Math.sin(i/6),b:55+18*Math.cos(i/7+1)};});
  var x=d3.scaleLinear().domain([0,N-1]).range([8,352]);var y=d3.scaleLinear().domain([0,100]).range([205,12]);
  svg.append('clipPath').attr('id','dc_above').append('path').datum(data).attr('d',d3.area().x(function(d){return x(d.i);}).y0(0).y1(function(d){return y(d.b);}));
  svg.append('clipPath').attr('id','dc_below').append('path').datum(data).attr('d',d3.area().x(function(d){return x(d.i);}).y0(210).y1(function(d){return y(d.b);}));
  var areaA=d3.area().x(function(d){return x(d.i);}).y0(210).y1(function(d){return y(d.a);});
  svg.append('path').datum(data).attr('clip-path','url(#dc_above)').attr('fill',ACCENT).attr('opacity',0.55).attr('d',areaA);
  svg.append('path').datum(data).attr('clip-path','url(#dc_below)').attr('fill',HILITE).attr('opacity',0.55).attr('d',areaA);
  svg.append('path').datum(data).attr('fill','none').attr('stroke',INK).attr('stroke-width',1.2).attr('d',d3.line().x(function(d){return x(d.i);}).y(function(d){return y(d.a);}));
  svg.append('path').datum(data).attr('fill','none').attr('stroke',INK2).attr('stroke-width',1).attr('stroke-dasharray','3,2').attr('d',d3.line().x(function(d){return x(d.i);}).y(function(d){return y(d.b);}));}
// ===== Stacked <-> grouped bars (animated toggle) =====
function stackGroup(host){var svg=newSvg(host);var m=4,keys=d3.range(m),cats=d3.range(10);var data=cats.map(function(c){var o={c:c};keys.forEach(function(k){o[k]=8+Math.random()*26;});return o;});
  var x=d3.scaleBand().domain(cats).range([18,352]).padding(0.12);var y=d3.scaleLinear().range([205,14]);var st=d3.stack().keys(keys)(data);
  var yStack=d3.max(st[st.length-1],function(d){return d[1];});var yGroup=d3.max(data,function(d){return d3.max(keys,function(k){return d[k];});});
  var xk=d3.scaleBand().domain(keys).range([0,x.bandwidth()]).padding(0.05);
  var layers=svg.selectAll('g.lyr').data(st).join('g').attr('class','lyr').attr('fill',function(_,i){return PAL[i];});
  var rects=layers.selectAll('rect').data(function(d){return d.map(function(seg,ci){return {seg:seg,ci:ci,key:d.key};});}).join('rect').attr('width',x.bandwidth()).attr('x',function(d){return x(d.ci);});
  function stacked(){y.domain([0,yStack]);rects.transition().duration(650).delay(function(d){return d.ci*8;}).attr('x',function(d){return x(d.ci);}).attr('width',x.bandwidth()).attr('y',function(d){return y(d.seg[1]);}).attr('height',function(d){return y(d.seg[0])-y(d.seg[1]);});}
  function grouped(){y.domain([0,yGroup]);rects.transition().duration(650).delay(function(d){return d.ci*8;}).attr('x',function(d){return x(d.ci)+xk(d.key);}).attr('width',xk.bandwidth()).attr('y',function(d){return y(d.seg[1]-d.seg[0]);}).attr('height',function(d){return 205-y(d.seg[1]-d.seg[0]);});}
  stacked();var g=false;var iv=setInterval(function(){g=!g;g?grouped():stacked();},2300);return function(){clearInterval(iv);};}
// ===== Epicyclic gearing (animated meshing gears) =====
function gears(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');
  function cog(teeth,r){var r0=r-6,r1=r+6,da=Math.PI/teeth,pts=[];for(var i=0;i<teeth;i++){var a=i*2*da;pts.push([Math.cos(a)*r0,Math.sin(a)*r0]);pts.push([Math.cos(a+da*0.3)*r1,Math.sin(a+da*0.3)*r1]);pts.push([Math.cos(a+da*0.7)*r1,Math.sin(a+da*0.7)*r1]);pts.push([Math.cos(a+da)*r0,Math.sin(a+da)*r0]);}return 'M'+pts.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1);}).join('L')+'Z';}
  var gA=g.append('g').attr('transform','translate(-34,0)');gA.append('path').attr('d',cog(24,64)).attr('fill',PAL[0]).attr('opacity',0.9);gA.append('circle').attr('r',14).attr('fill','#fff').attr('stroke',PAL[0]).attr('stroke-width',3);
  var gB=g.append('g').attr('transform','translate(70,0)');gB.append('path').attr('d',cog(12,32)).attr('fill',PAL[3]).attr('opacity',0.9);gB.append('circle').attr('r',9).attr('fill','#fff').attr('stroke',PAL[3]).attr('stroke-width',3);
  var ang=0;var iv=setInterval(function(){ang+=1.4;gA.attr('transform','translate(-34,0) rotate('+ang+')');gB.attr('transform','translate(70,0) rotate('+(-ang*2)+')');},40);return function(){clearInterval(iv);};}
// ===== Polar clock (live radial time arcs) =====
function polarClock(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var fields=[['Sec',60,PAL[0]],['Min',60,PAL[1]],['Hr',24,PAL[2]]];
  var layers=fields.map(function(f,i){var r=100-i*28;g.append('circle').attr('r',r-6).attr('fill','none').attr('stroke',GRIDC).attr('stroke-width',12);var p=g.append('path').attr('fill',f[2]);g.append('text').attr('x',0).attr('y',-(r-6)).attr('dy',4).attr('text-anchor','middle').attr('font-size',8).attr('font-family',FONT).attr('fill',INK2).text(f[0]);return {f:f,r:r,p:p};});
  function frame(){var now=new Date();var vals=[now.getSeconds()+now.getMilliseconds()/1000,now.getMinutes()+now.getSeconds()/60,(now.getHours()%24)+now.getMinutes()/60];
    layers.forEach(function(L,i){var frac=vals[i]/L.f[1];L.p.attr('d',d3.arc().innerRadius(L.r-12).outerRadius(L.r).startAngle(0).endAngle(frac*2*Math.PI).cornerRadius(6)());});}
  frame();var iv=setInterval(frame,200);return function(){clearInterval(iv);};}
// ===== Hierarchical (drill-down) bar chart =====
function hierBar(host){var svg=newSvg(host);var root=d3.hierarchy(DATA).sum(function(d){return d.size;}).sort(function(a,b){return b.value-a.value;});var cur=root;
  var y=d3.scaleBand().range([24,205]).padding(0.18);var x=d3.scaleLinear().range([90,352]);
  var title=svg.append('text').attr('x',6).attr('y',14).attr('font-size',10).attr('font-weight',700).attr('font-family',FONT).attr('fill',INK);
  function show(node){cur=node;var kids=node.children||[];y.domain(kids.map(function(d){return d.data.name;}));x.domain([0,d3.max(kids,function(d){return d.value;})||1]);
    title.text(node.ancestors().reverse().map(function(d){return d.data.name;}).join(' / ')+(node.children?'  — click a bar':'  (leaf)'));
    var bars=svg.selectAll('g.hb').data(kids,function(d){return d.data.name;});bars.exit().remove();var e=bars.enter().append('g').attr('class','hb');e.append('rect');e.append('text');var m=e.merge(bars);
    m.select('rect').attr('x',90).attr('y',function(d){return y(d.data.name);}).attr('height',y.bandwidth()).attr('rx',2).attr('fill',function(d){return d.children?ACCENT:'#9ecae1';}).style('cursor',function(d){return d.children?'pointer':'default';}).on('click',function(event,d){if(d.children){event.stopPropagation();show(d);}}).transition().duration(500).attr('width',function(d){return Math.max(0,x(d.value)-90);});
    m.select('text').attr('x',84).attr('y',function(d){return y(d.data.name)+y.bandwidth()/2+3;}).attr('text-anchor','end').attr('font-size',9).attr('font-family',FONT).attr('fill',INK2).text(function(d){return d.data.name;});}
  svg.on('click',function(event){if((event.target.tagName==='svg'||event.target.tagName==='text')&&cur.parent)show(cur.parent);});show(root);}
// ===== Multi-line + Voronoi (nearest-line hover) =====
function multiLineVoronoi(host){var svg=newSvg(host);var series=d3.range(4).map(function(s){return d3.range(20).map(function(i){return {s:s,i:i,v:45+20*Math.sin(i/3+s)+s*5};});});
  var x=d3.scaleLinear().domain([0,19]).range([30,352]);var y=d3.scaleLinear().domain([0,100]).range([205,12]);axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(5)));
  series.forEach(function(ser,s){svg.append('path').datum(ser).attr('class','ml'+s).attr('fill','none').attr('stroke',PAL[s]).attr('stroke-width',1.5).attr('opacity',0.55).attr('d',d3.line().x(function(d){return x(d.i);}).y(function(d){return y(d.v);}).curve(d3.curveMonotoneX));});
  var all=[].concat.apply([],series);var del=d3.Delaunay.from(all,function(d){return x(d.i);},function(d){return y(d.v);});
  var dot=svg.append('circle').attr('r',4).style('display','none');var lbl=svg.append('text').attr('font-size',10).attr('font-family',FONT).attr('fill',INK).style('display','none');
  svg.append('rect').attr('width',360).attr('height',215).attr('fill','transparent').on('mousemove',function(event){var p=d3.pointer(event);var d=all[del.find(p[0],p[1])];
    [0,1,2,3].forEach(function(s){svg.select('.ml'+s).attr('opacity',s===d.s?1:0.15).attr('stroke-width',s===d.s?2.5:1.5);});dot.style('display',null).attr('cx',x(d.i)).attr('cy',y(d.v)).attr('fill',PAL[d.s]);lbl.style('display',null).attr('x',x(d.i)+8).attr('y',y(d.v)-6).text('S'+d.s+': '+Math.round(d.v));
  }).on('mouseout',function(){[0,1,2,3].forEach(function(s){svg.select('.ml'+s).attr('opacity',0.55).attr('stroke-width',1.5);});dot.style('display','none');lbl.style('display','none');});}
// ===== Bubble chart (pack, labeled) =====
function bubbleChart(host){var svg=newSvg(host);var root=d3.hierarchy({children:d3.range(12).map(function(i){return {name:'B'+i,value:10+Math.random()*90};})}).sum(function(d){return d.value;});
  d3.pack().size([355,225]).padding(3)(root);var g=svg.selectAll('g').data(root.leaves()).join('g').attr('transform',function(d){return 'translate('+d.x+','+d.y+')';});
  g.append('circle').attr('r',0).attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('opacity',0.78).transition().duration(800).delay(function(_,i){return i*50;}).attr('r',function(d){return d.r;});
  g.append('text').attr('text-anchor','middle').attr('dy',3).attr('font-size',9).attr('font-family',FONT).attr('fill','#fff').style('pointer-events','none').text(function(d){return d.r>14?d.data.name:'';});}
// ===== Google-style needle gauges (tomerd, d3 v2 + external gauge.js -> reimplemented in v7) =====
function needleGauges(host){var svg=newSvg(host);var defs=[['Memory',0,100],['CPU',0,100],['Network',0,100]];var cx=[72,180,288],cy=120,r=46;var a0=-3*Math.PI/4,a1=3*Math.PI/4;var needles=[];
  defs.forEach(function(def,gi){var min=def[1],max=def[2];var g=svg.append('g').attr('transform','translate('+cx[gi]+','+cy+')');var sc=d3.scaleLinear().domain([min,max]).range([a0,a1]);
    function band(f0,f1,col){g.append('path').attr('fill',col).attr('d',d3.arc().innerRadius(r-9).outerRadius(r).startAngle(sc(min+(max-min)*f0)).endAngle(sc(min+(max-min)*f1))());}
    band(0,0.75,'#2EB88A');band(0.75,0.9,'#F69E23');band(0.9,1,'#DD2C4D');
    d3.range(0,6).forEach(function(i){var t=min+(max-min)*i/5;var ang=sc(t);g.append('line').attr('x1',Math.sin(ang)*(r-11)).attr('y1',-Math.cos(ang)*(r-11)).attr('x2',Math.sin(ang)*(r+1)).attr('y2',-Math.cos(ang)*(r+1)).attr('stroke',INK2);
      g.append('text').attr('x',Math.sin(ang)*(r+10)).attr('y',-Math.cos(ang)*(r+10)).attr('text-anchor','middle').attr('dy',3).attr('font-size',7).attr('font-family',FONT).attr('fill',INK2).text(Math.round(t));});
    g.append('text').attr('y',24).attr('text-anchor','middle').attr('font-size',10).attr('font-weight',700).attr('font-family',FONT).attr('fill',INK).text(def[0]);
    var val=g.append('text').attr('y',38).attr('text-anchor','middle').attr('font-size',10).attr('font-family',FONT).attr('fill',INK2);
    var needle=g.append('g');needle.append('path').attr('d','M -2.5,6 L 0,'+(-(r-14))+' L 2.5,6 Z').attr('fill',INK);needle.append('circle').attr('r',4).attr('fill',INK);
    needles.push({needle:needle,sc:sc,val:val,def:def});});
  function update(){needles.forEach(function(N){var v=N.def[1]+(N.def[2]-N.def[1])*Math.random();N.needle.transition().duration(1200).attr('transform','rotate('+(N.sc(v)*180/Math.PI)+')');N.val.text(Math.round(v));});}
  update();var iv=setInterval(update,3000);return function(){clearInterval(iv);};}
// ===== Interactive graph editor (cjrd graph-creator, d3 v3 + FileSaver -> reimplemented in v7; file save/load omitted — would persist to a UC dataset) =====
function graphEditor(host){var svg=newSvg(host).style('cursor','crosshair');
  var nodes=[{id:0,x:90,y:80,t:'A'},{id:1,x:250,y:70,t:'B'},{id:2,x:170,y:175,t:'C'}];var edges=[{s:0,t:1},{s:1,t:2}];var idc=3,selected=null;
  svg.append('text').attr('x',8).attr('y',12).attr('font-size',8.5).attr('font-family',FONT).attr('fill',INK2).text('click empty = add · drag = move · shift-drag node→node = edge · dbl-click = delete');
  var gE=svg.append('g'),gN=svg.append('g');var dragLine=svg.append('line').attr('stroke',INK).attr('stroke-dasharray','4,3').style('display','none');
  function byId(id){for(var i=0;i<nodes.length;i++)if(nodes[i].id===id)return nodes[i];}
  function render(){
    var e=gE.selectAll('line').data(edges,function(d){return d.s+'-'+d.t;});e.exit().remove();
    e.enter().append('line').attr('stroke',ACCENT).attr('stroke-width',2).merge(e).attr('x1',function(d){return byId(d.s).x;}).attr('y1',function(d){return byId(d.s).y;}).attr('x2',function(d){return byId(d.t).x;}).attr('y2',function(d){return byId(d.t).y;});
    var g=gN.selectAll('g.nd').data(nodes,function(d){return d.id;});g.exit().remove();
    var en=g.enter().append('g').attr('class','nd').style('cursor','move');en.append('circle').attr('r',16);en.append('text').attr('text-anchor','middle').attr('dy',4).attr('font-size',11).attr('font-family',FONT).attr('fill','#fff').style('pointer-events','none');
    var m=en.merge(g).attr('transform',function(d){return 'translate('+d.x+','+d.y+')';});
    m.select('circle').attr('fill',function(d){return d===selected?HILITE:ACCENT;});m.select('text').text(function(d){return d.t;});
    m.on('click',function(event,d){selected=d;event.stopPropagation();render();}).on('dblclick',function(event,d){edges=edges.filter(function(x){return x.s!==d.id&&x.t!==d.id;});nodes=nodes.filter(function(x){return x!==d;});if(selected===d)selected=null;event.stopPropagation();render();})
      .call(d3.drag().on('start',function(event,d){this.__e=event.sourceEvent.shiftKey;if(this.__e){dragLine.style('display',null).attr('x1',d.x).attr('y1',d.y).attr('x2',d.x).attr('y2',d.y);}})
        .on('drag',function(event,d){if(this.__e){dragLine.attr('x2',event.x).attr('y2',event.y);}else{d.x=event.x;d.y=event.y;render();}})
        .on('end',function(event,d){if(this.__e){dragLine.style('display','none');var tgt=null,best=24;nodes.forEach(function(nn){if(nn!==d){var dx=nn.x-event.x,dy=nn.y-event.y,ds=Math.sqrt(dx*dx+dy*dy);if(ds<best){best=ds;tgt=nn;}}});if(tgt){edges.push({s:d.id,t:tgt.id});render();}}}));}
  svg.on('click',function(event){if(event.target===svg.node()){var p=d3.pointer(event);nodes.push({id:idc,x:p[0],y:p[1],t:String.fromCharCode(65+idc)});idc++;render();}});
  render();}

/* ===== d3og.com -- more classics (fresh ports) ===== */
function colorBrewer(host){var svg=d3.select(host).append('svg').attr('width','100%').attr('height',230).attr('viewBox','0 0 360 230').style('overflow','visible');
  var schemes=[['Viridis',d3.interpolateViridis],['Blues',d3.interpolateBlues],['Greens',d3.interpolateGreens],['Spectral',d3.interpolateSpectral],['RdYlBu',d3.interpolateRdYlBu],['Cool',d3.interpolateCool],['Warm',d3.interpolateWarm],['Plasma',d3.interpolatePlasma]].filter(function(s){return typeof s[1]==='function';});
  var n=42,bh=(230-10)/schemes.length,bw=(360-80)/n;
  schemes.forEach(function(s,si){var y=5+si*bh;for(var i=0;i<n;i++){svg.append('rect').attr('x',72+i*bw).attr('y',y).attr('width',bw+0.6).attr('height',bh-5).attr('fill',s[1](i/(n-1)));}
    svg.append('text').attr('x',66).attr('y',y+(bh-5)/2+3).attr('text-anchor','end').attr('font-size',9).attr('font-family',FONT).attr('fill',INK2).text(s[0]);});}
function quadtreeViz(host){var svg=newSvg(host);var W=360,H=230;var pts=d3.range(80).map(function(){return [8+Math.random()*(W-16),8+Math.random()*(H-16)];});
  var cells=[];
  function build(x0,y0,x1,y1,ps,depth){cells.push([x0,y0,x1-x0,y1-y0]);if(ps.length<=1||depth>6)return;var mx=(x0+x1)/2,my=(y0+y1)/2;var q=[[],[],[],[]];
    ps.forEach(function(p){var qi=(p[0]<mx?0:1)+(p[1]<my?0:2);q[qi].push(p);});
    if(q[0].length)build(x0,y0,mx,my,q[0],depth+1);if(q[1].length)build(mx,y0,x1,my,q[1],depth+1);if(q[2].length)build(x0,my,mx,y1,q[2],depth+1);if(q[3].length)build(mx,my,x1,y1,q[3],depth+1);}
  build(0,0,W,H,pts,0);
  svg.append('g').selectAll('rect').data(cells).join('rect').attr('x',function(d){return d[0];}).attr('y',function(d){return d[1];}).attr('width',function(d){return d[2];}).attr('height',function(d){return d[3];}).attr('fill','none').attr('stroke',GRIDC).attr('stroke-width',0.5);
  svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx',function(d){return d[0];}).attr('cy',function(d){return d[1];}).attr('r',3).attr('fill',ACCENT).attr('opacity',0.6);
  var hl=svg.append('circle').attr('r',6).attr('fill','none').attr('stroke',HILITE).attr('stroke-width',2).style('display','none');
  svg.append('rect').attr('width',W).attr('height',H).attr('fill','transparent').on('mousemove',function(event){var p=d3.pointer(event);var best,bd=1e9;pts.forEach(function(pt){var dx=pt[0]-p[0],dy=pt[1]-p[1],d2=dx*dx+dy*dy;if(d2<bd){bd=d2;best=pt;}});if(best){hl.style('display',null).attr('cx',best[0]).attr('cy',best[1]);}}).on('mouseout',function(){hl.style('display','none');});}
function closestPoint(host){var svg=newSvg(host);var data=d3.range(20).map(function(i){return [20+i*17,120+70*Math.sin(i/2.2)];});
  var node=svg.append('path').datum(data).attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',2).attr('d',d3.line().x(function(d){return d[0];}).y(function(d){return d[1];}).curve(d3.curveCatmullRom)).node();
  var L=node.getTotalLength();var marker=svg.append('circle').attr('r',5).attr('fill',HILITE).style('display','none');
  var seg=svg.append('line').attr('stroke',INK2).attr('stroke-dasharray','3,3').style('display','none');var cur=svg.append('circle').attr('r',3).attr('fill',INK).style('display','none');
  svg.append('rect').attr('width',360).attr('height',230).attr('fill','transparent').on('mousemove',function(event){var m=d3.pointer(event);var best,bd=1e9;for(var s=0;s<=L;s+=4){var pt=node.getPointAtLength(s);var dx=pt.x-m[0],dy=pt.y-m[1],d2=dx*dx+dy*dy;if(d2<bd){bd=d2;best=pt;}}cur.style('display',null).attr('cx',m[0]).attr('cy',m[1]);marker.style('display',null).attr('cx',best.x).attr('cy',best.y);seg.style('display',null).attr('x1',m[0]).attr('y1',m[1]).attr('x2',best.x).attr('y2',best.y);}).on('mouseout',function(){marker.style('display','none');seg.style('display','none');cur.style('display','none');});}
function autoText(host){var svg=newSvg(host);var words=['D3','viz','data','W.E.B.','Du Bois','gallery','render'];var t=svg.append('text').attr('x',180).attr('y',125).attr('text-anchor','middle').attr('dominant-baseline','middle').attr('font-family',FONT).attr('font-weight',700).attr('fill',ACCENT).attr('font-size',10).text(words[0]);var i=0;
  function frame(){i++;var w=words[i%words.length];t.text(w).attr('font-size',10);var bb=t.node().getBBox();var scale=Math.min(300/bb.width,120/bb.height);t.transition().duration(850).attr('font-size',10*scale).attr('fill',PAL[i%PAL.length]);}
  frame();var iv=setInterval(frame,1500);return function(){clearInterval(iv);};}
function wrapLabels(host){var svg=newSvg(host);var data=[['Annual recurring revenue',70],['Customer acquisition cost',45],['Monthly active users',88],['Net promoter score',55]];
  var x=d3.scaleBand().domain(data.map(function(d){return d[0];})).range([12,352]).padding(0.3);var y=d3.scaleLinear().domain([0,100]).range([172,14]);
  svg.selectAll('rect').data(data).join('rect').attr('x',function(d){return x(d[0]);}).attr('width',x.bandwidth()).attr('y',function(d){return y(d[1]);}).attr('height',function(d){return 172-y(d[1]);}).attr('rx',2).attr('fill',PAL[2]).attr('opacity',0.85);
  svg.selectAll('text.lab').data(data).join('text').attr('class','lab').attr('x',function(d){return x(d[0])+x.bandwidth()/2;}).attr('text-anchor','middle').attr('font-size',9).attr('font-family',FONT).attr('fill',INK2).each(function(d){wrap(d3.select(this),d[0],x.bandwidth());});
  function wrap(text,str,width){var words=str.split(/\s+/);var line=[],lineNo=0,yy=180;text.text(null);var tsp=text.append('tspan').attr('x',text.attr('x')).attr('y',yy).attr('dy','0.9em');
    words.forEach(function(word){line.push(word);tsp.text(line.join(' '));if(tsp.node().getComputedTextLength()>width&&line.length>1){line.pop();tsp.text(line.join(' '));line=[word];tsp=text.append('tspan').attr('x',text.attr('x')).attr('y',yy).attr('dy',(++lineNo*1.05+0.9)+'em').text(word);}});}}
function multiFoci(host){var svg=newSvg(host);var groups=4;var foci=d3.range(groups).map(function(i){return {x:80+(i%2)*200,y:70+Math.floor(i/2)*95};});
  var nodes=d3.range(80).map(function(){return {g:Math.floor(Math.random()*groups)};});
  var sim=d3.forceSimulation(nodes).force('x',d3.forceX(function(d){return foci[d.g].x;}).strength(0.12)).force('y',d3.forceY(function(d){return foci[d.g].y;}).strength(0.12)).force('collide',d3.forceCollide(5.5)).force('charge',d3.forceManyBody().strength(-4));
  var c=svg.append('g').selectAll('circle').data(nodes).join('circle').attr('r',4.5).attr('fill',function(d){return PAL[d.g];}).attr('opacity',0.85).attr('stroke',CARD).attr('stroke-width',0.5);
  sim.on('tick',function(){c.attr('cx',function(d){return d.x;}).attr('cy',function(d){return d.y;});});return function(){sim.stop();};}
function stackedRadialArea(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,118)');var keys=['a','b','c'];var N=28;
  var data=d3.range(N).map(function(i){var o={i:i};keys.forEach(function(k,ki){o[k]=6+6*Math.sin(i/3+ki)+Math.random()*3+4;});return o;});
  var st=d3.stack().keys(keys)(data);var ang=d3.scaleLinear().domain([0,N]).range([0,2*Math.PI]);var r=d3.scaleLinear().domain([0,d3.max(st[st.length-1],function(d){return d[1];})]).range([24,104]);
  var area=d3.areaRadial().angle(function(d,i){return ang(i);}).innerRadius(function(d){return r(d[0]);}).outerRadius(function(d){return r(d[1]);}).curve(d3.curveCardinalClosed);
  g.selectAll('path').data(st).join('path').attr('fill',function(_,i){return PAL[i];}).attr('opacity',0.8).attr('d',area);}
function spiralCircle(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var n=180;var color=d3.scaleSequential(d3.interpolateViridis).domain([0,n]);
  var pts=d3.range(n).map(function(i){var a=i*0.5;var rad=3+i*0.6;return {x:Math.cos(a)*rad,y:Math.sin(a)*rad,i:i};});
  g.selectAll('circle').data(pts).join('circle').attr('cx',function(d){return d.x;}).attr('cy',function(d){return d.y;}).attr('r',0).attr('fill',function(d){return color(d.i);}).transition().duration(900).delay(function(d){return d.i*8;}).attr('r',3.4);}
function brushHandles(host){var svg=newSvg(host);var n=40;var data=d3.range(n).map(function(i){return 45+28*Math.sin(i/4)+Math.random()*8;});var x=d3.scaleLinear().domain([0,n-1]).range([20,340]);var y=d3.scaleLinear().domain([0,90]).range([150,24]);
  svg.append('path').datum(data).attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',1.5).attr('d',d3.line().x(function(d,i){return x(i);}).y(function(d){return y(d);}).curve(d3.curveMonotoneX));
  var lbl=svg.append('text').attr('x',20).attr('y',16).attr('font-size',10).attr('font-weight',700).attr('font-family',FONT).attr('fill',INK2);
  var sel=[x(10),x(24)];var yA=160,yB=192;
  var rectSel=svg.append('rect').attr('y',yA).attr('height',yB-yA).attr('fill',ACCENT).attr('opacity',0.15);
  svg.append('rect').attr('x',20).attr('y',yA).attr('width',320).attr('height',yB-yA).attr('fill','none').attr('stroke',GRIDC);
  function mk(side){return svg.append('rect').attr('width',6).attr('height',30).attr('rx',2).attr('y',(yA+yB)/2-15).attr('fill','#fff').attr('stroke',INK).attr('stroke-width',1.5).style('cursor','ew-resize').call(d3.drag().on('drag',function(event){sel[side]=Math.max(20,Math.min(340,event.x));if(sel[0]>sel[1]){var t=sel[0];sel[0]=sel[1];sel[1]=t;}upd();}));}
  function upd(){rectSel.attr('x',sel[0]).attr('width',sel[1]-sel[0]);h0.attr('x',sel[0]-3);h1.attr('x',sel[1]-3);var i0=Math.round(x.invert(sel[0])),i1=Math.round(x.invert(sel[1]));lbl.text('brush ['+i0+' - '+i1+']');}
  var h0=mk(0),h1=mk(1);upd();}
function pieUpdate(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,118)');var pie=d3.pie().sort(null);var arc=d3.arc().innerRadius(40).outerRadius(96);var k=5;
  function rnd(){return d3.range(k).map(function(){return 5+Math.random()*30;});}
  var path=g.selectAll('path').data(pie(rnd())).join('path').attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('stroke','#fff').attr('stroke-width',1).each(function(d){this._c=d;});
  function frame(){path=path.data(pie(rnd()));path.transition().duration(900).attrTween('d',function(d){var i=d3.interpolate(this._c,d);this._c=i(1);return function(t){return arc(i(t));};});}
  var iv=setInterval(frame,1700);return function(){clearInterval(iv);};}


/* ===== d3og.com -- even more (sandbox-safe core d3) ===== */
function mareyTrains(host){var svg=newSvg(host);var stations=['Gare A','B','C','D','Gare E'];var sy=d3.scalePoint().domain(stations).range([20,198]);var x=d3.scaleLinear().domain([0,24]).range([44,352]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(6)));
  stations.forEach(function(s){svg.append('line').attr('x1',44).attr('x2',352).attr('y1',sy(s)).attr('y2',sy(s)).attr('stroke',GRIDC);svg.append('text').attr('x',40).attr('y',sy(s)+3).attr('text-anchor','end').attr('font-size',8).attr('font-family',FONT).attr('fill',INK2).text(s);});
  d3.range(11).forEach(function(k){var start=k*2+Math.random();var dir=k%2===0;var stops=stations.map(function(_,i){var idx=dir?i:stations.length-1-i;return {t:start+idx*0.75+Math.random()*0.15,s:stations[idx]};});
    svg.append('path').datum(stops).attr('fill','none').attr('stroke',PAL[k%PAL.length]).attr('stroke-width',1.6).attr('opacity',0.85).attr('d',d3.line().x(function(d){return x(d.t);}).y(function(d){return sy(d.s);}));});}
function patentSuits(host){var svg=newSvg(host);var defs=svg.append('defs');defs.append('marker').attr('id','ps_arr').attr('viewBox','0 -5 10 10').attr('refX',17).attr('refY',0).attr('markerWidth',6).attr('markerHeight',6).attr('orient','auto').append('path').attr('d','M0,-5L10,0L0,5').attr('fill',INK2);
  var N=12;var nodes=d3.range(N).map(function(i){return {id:i,t:String.fromCharCode(65+i)};});var links=d3.range(16).map(function(){return {source:Math.floor(Math.random()*N),target:Math.floor(Math.random()*N)};}).filter(function(l){return l.source!==l.target;});
  var link=svg.append('g').selectAll('line').data(links).join('line').attr('stroke',INK2).attr('stroke-opacity',0.5).attr('marker-end','url(#ps_arr)');
  var node=svg.append('g').selectAll('g').data(nodes).join('g').style('cursor','grab');node.append('circle').attr('r',9).attr('fill',function(d){return PAL[d.id%PAL.length];});node.append('text').attr('text-anchor','middle').attr('dy',3).attr('font-size',9).attr('font-family',FONT).attr('fill','#fff').style('pointer-events','none').text(function(d){return d.t;});
  var sim=d3.forceSimulation(nodes).force('charge',d3.forceManyBody().strength(-95)).force('link',d3.forceLink(links).distance(46)).force('center',d3.forceCenter(180,115)).force('collide',d3.forceCollide(13)).on('tick',function(){link.attr('x1',function(d){return d.source.x;}).attr('y1',function(d){return d.source.y;}).attr('x2',function(d){return d.target.x;}).attr('y2',function(d){return d.target.y;});node.attr('transform',function(d){return 'translate('+d.x+','+d.y+')';});});
  node.call(d3.drag().on('start',function(e,d){if(!e.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;}).on('drag',function(e,d){d.fx=e.x;d.fy=e.y;}).on('end',function(e,d){if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}));return function(){sim.stop();};}
function omgParticles(host){var svg=newSvg(host);var W=360,H=230;var parts=[];var color=d3.scaleSequential(d3.interpolateViridis).domain([0,60]);var g=svg.append('g');
  function frame(){for(var i=0;i<6;i++)parts.push({x:W/2,y:H-8,vx:(Math.random()-0.5)*6,vy:-4-Math.random()*5,life:0,c:color(Math.random()*60)});
    parts=parts.filter(function(p){return p.life<60&&p.y<H+10;});parts.forEach(function(p){p.vy+=0.18;p.x+=p.vx;p.y+=p.vy;p.life++;});
    var c=g.selectAll('circle').data(parts);c.enter().append('circle').attr('r',2.5).merge(c).attr('cx',function(p){return p.x;}).attr('cy',function(p){return p.y;}).attr('fill',function(p){return p.c;}).attr('opacity',function(p){return 1-p.life/60;});c.exit().remove();}
  frame();var iv=setInterval(frame,45);return function(){clearInterval(iv);};}
function zoomableArea(host){var svg=newSvg(host).style('cursor','ew-resize');var n=120;var data=d3.range(n).map(function(i){return [i,50+30*Math.sin(i/9)+Math.random()*8];});var x=d3.scaleLinear().domain([0,n-1]).range([34,350]);var y=d3.scaleLinear().domain([0,100]).range([200,12]);
  var gx=svg.append('g').attr('transform','translate(0,200)');axc(gx.call(d3.axisBottom(x).ticks(6)));axc(svg.append('g').attr('transform','translate(34,0)').call(d3.axisLeft(y).ticks(4)));
  svg.append('clipPath').attr('id','za_clip').append('rect').attr('x',34).attr('y',12).attr('width',316).attr('height',188);
  var path=svg.append('path').datum(data).attr('clip-path','url(#za_clip)').attr('fill',ACCENT).attr('opacity',0.5).attr('d',d3.area().x(function(d){return x(d[0]);}).y0(200).y1(function(d){return y(d[1]);}).curve(d3.curveMonotoneX));
  var zoom=d3.zoom().scaleExtent([1,12]).translateExtent([[34,0],[350,230]]).extent([[34,0],[350,230]]).on('zoom',function(event){var zx=event.transform.rescaleX(x);axc(gx.call(d3.axisBottom(zx).ticks(6)));path.attr('d',d3.area().x(function(d){return zx(d[0]);}).y0(200).y1(function(d){return y(d[1]);}).curve(d3.curveMonotoneX));});svg.call(zoom);}


/* ===== Observable @d3/gallery -- iconic additions (core d3, sandbox-safe) ===== */
function wealthHealth(host){var svg=newSvg(host);
  var x=d3.scaleLog().domain([250,60000]).range([38,350]);var y=d3.scaleLinear().domain([20,85]).range([205,16]);var r=d3.scaleSqrt().domain([0,5e8]).range([2,19]);
  var N=30;var nations=d3.range(N).map(function(i){return {reg:i%5,pop:1e6+Math.random()*4.5e8,inc0:300+Math.random()*3500,life0:34+Math.random()*22,gi:0.025+Math.random()*0.05,gl:0.08+Math.random()*0.45};});
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(4,'~s')));axc(svg.append('g').attr('transform','translate(38,0)').call(d3.axisLeft(y).ticks(4)));
  var yr=svg.append('text').attr('x',345).attr('y',120).attr('text-anchor','end').attr('font-size',46).attr('font-weight',700).attr('fill',GRIDC).attr('font-family',FONT);
  var dots=svg.append('g').selectAll('circle').data(nations).join('circle').attr('fill',function(d){return PAL[d.reg];}).attr('opacity',0.72).attr('stroke',CARD).attr('stroke-width',0.5);
  var t=0;function frame(){t=(t+1)%82;yr.text(1960+t);dots.attr('cx',function(d){return x(Math.min(59000,d.inc0*Math.pow(1+d.gi,t)));}).attr('cy',function(d){return y(Math.min(84,d.life0+d.gl*t));}).attr('r',function(d){return r(d.pop);});}
  frame();var iv=setInterval(frame,110);return function(){clearInterval(iv);};}
function scatterTour(host){var svg=newSvg(host);var K=5;var clusters=d3.range(K).map(function(k){return {cx:0.15+Math.random()*0.7,cy:0.15+Math.random()*0.7,col:PAL[k]};});
  var pts=[];clusters.forEach(function(c,k){d3.range(32).forEach(function(){pts.push({gx:c.cx+rnorm()*0.05,gy:c.cy+rnorm()*0.05,k:k});});});
  var x=d3.scaleLinear().domain([0,1]).range([18,345]);var y=d3.scaleLinear().domain([0,1]).range([210,14]);
  var dots=svg.append('g').selectAll('circle').data(pts).join('circle').attr('r',3).attr('fill',function(d){return clusters[d.k].col;}).attr('opacity',0.75).attr('cx',function(d){return x(d.gx);}).attr('cy',function(d){return y(d.gy);});
  var k=0;function focus(){var c=clusters[k];x.domain([c.cx-0.2,c.cx+0.2]);y.domain([c.cy-0.2,c.cy+0.2]);
    dots.transition().duration(1300).attr('cx',function(d){return x(d.gx);}).attr('cy',function(d){return y(d.gy);}).attr('opacity',function(d){return d.k===k?0.95:0.1;}).attr('r',function(d){return d.k===k?5:3;});k=(k+1)%K;}
  focus();var iv=setInterval(focus,1900);return function(){clearInterval(iv);};}
function indexChart(host){var svg=newSvg(host);var S=4,N=64;var series=d3.range(S).map(function(){var v=100;return d3.range(N).map(function(){v*=(1+(Math.random()-0.48)*0.06);return v;});});
  var x=d3.scaleLinear().domain([0,N-1]).range([40,350]);var y=d3.scaleLog().domain([0.6,1.9]).range([205,12]);
  var gx=svg.append('g').attr('transform','translate(0,205)');axc(gx.call(d3.axisBottom(x).ticks(5)));var gy=svg.append('g').attr('transform','translate(40,0)');
  var base=0;var paths=series.map(function(_,s){return svg.append('path').attr('fill','none').attr('stroke',PAL[s]).attr('stroke-width',1.8);});
  var rule=svg.append('line').attr('y1',12).attr('y2',205).attr('stroke',INK2).attr('stroke-dasharray','3,3').style('display','none');
  function redraw(){axc(gy.call(d3.axisLeft(y).ticks(4)));paths.forEach(function(p,s){var b=series[s][base];p.datum(series[s]).attr('d',d3.line().x(function(d,i){return x(i);}).y(function(d){return y(Math.max(0.6,Math.min(1.9,d/b)));}));});}
  redraw();svg.append('rect').attr('x',40).attr('width',310).attr('height',205).attr('fill','transparent').on('mousemove',function(event){var i=Math.max(0,Math.min(N-1,Math.round(x.invert(d3.pointer(event)[0]))));base=i;rule.style('display',null).attr('x1',x(i)).attr('x2',x(i));redraw();}).on('mouseout',function(){base=0;rule.style('display','none');redraw();});}
function bandChart(host){var svg=newSvg(host);var N=52;var data=[];var v=60;for(var i=0;i<N;i++){v+=(Math.random()-0.48)*5;var sd=5+3*Math.abs(Math.sin(i/8));data.push({i:i,m:v,lo:v-sd,hi:v+sd});}
  var x=d3.scaleLinear().domain([0,N-1]).range([34,350]);var y=d3.scaleLinear().domain([30,90]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(5)));axc(svg.append('g').attr('transform','translate(34,0)').call(d3.axisLeft(y).ticks(4)));
  svg.append('path').datum(data).attr('fill',ACCENT).attr('opacity',0.18).attr('d',d3.area().x(function(d){return x(d.i);}).y0(function(d){return y(d.lo);}).y1(function(d){return y(d.hi);}).curve(d3.curveBasis));
  svg.append('path').datum(data).attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',1.8).attr('d',d3.line().x(function(d){return x(d.i);}).y(function(d){return y(d.m);}).curve(d3.curveBasis));}
function hertzsprung(host){var svg=newSvg(host);svg.append('rect').attr('width',360).attr('height',230).attr('fill','#0b1020');
  var n=1300;var x=d3.scaleLinear().domain([-0.4,2.0]).range([30,348]);var y=d3.scaleLinear().domain([-6,16]).range([16,212]);
  var color=d3.scaleLinear().domain([-0.4,0.2,0.8,1.4,2.0]).range(['#9bb0ff','#cad7ff','#fff4e8','#ffd2a1','#ff8a5c']);
  var pts=d3.range(n).map(function(){var bv=-0.35+Math.random()*2.3;var mag;if(Math.random()<0.88){mag=-4.5+(bv+0.35)*6.5+rnorm()*1.1;}else{mag=-3.5+rnorm()*1.6;}return [bv,mag];});
  svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx',function(d){return x(d[0]);}).attr('cy',function(d){return y(d[1]);}).attr('r',1.1).attr('fill',function(d){return color(d[0]);}).attr('opacity',0.85);}
function volcanoContours(host){var svg=newSvg(host);var m=56,n=36;var values=new Array(m*n);
  for(var j=0;j<n;j++)for(var i=0;i<m;i++){var dx=(i-m*0.44)/7,dy=(j-n*0.52)/5,dx2=(i-m*0.72)/6,dy2=(j-n*0.4)/5;values[j*m+i]=9*Math.exp(-(dx*dx+dy*dy))+6*Math.exp(-(dx2*dx2+dy2*dy2))+Math.sin(i/5)*0.6;}
  var cs=d3.contours().size([m,n]).thresholds(11)(values);var ex=d3.extent(cs,function(c){return c.value;});var color=d3.scaleSequential(d3.interpolateViridis).domain([ex[0],ex[1]]);
  svg.append('g').attr('transform','scale('+(360/m)+','+(230/n)+')').selectAll('path').data(cs).join('path').attr('d',function(c){return mpToPath(c);}).attr('fill',function(c){return color(c.value);}).attr('stroke','#fff').attr('stroke-width',0.12);}
function disjointForce(host){var svg=newSvg(host);var comps=4;var nodes=[],links=[];var id=0;
  d3.range(comps).forEach(function(c){var start=id;var k=3+Math.floor(Math.random()*4);for(var i=0;i<k;i++)nodes.push({id:id++,c:c});for(var i2=1;i2<k;i2++)links.push({source:start+i2,target:start+Math.floor(Math.random()*i2)});});
  var link=svg.append('g').attr('stroke',INK2).attr('stroke-opacity',0.4).selectAll('line').data(links).join('line');
  var node=svg.append('g').selectAll('circle').data(nodes).join('circle').attr('r',6).attr('fill',function(d){return PAL[d.c];}).attr('stroke',CARD).style('cursor','grab');
  var sim=d3.forceSimulation(nodes).force('charge',d3.forceManyBody().strength(-48)).force('link',d3.forceLink(links).distance(26)).force('x',d3.forceX(180).strength(0.06)).force('y',d3.forceY(115).strength(0.06)).force('collide',d3.forceCollide(9)).on('tick',function(){link.attr('x1',function(d){return d.source.x;}).attr('y1',function(d){return d.source.y;}).attr('x2',function(d){return d.target.x;}).attr('y2',function(d){return d.target.y;});node.attr('cx',function(d){return d.x;}).attr('cy',function(d){return d.y;});});
  node.call(d3.drag().on('start',function(e,d){if(!e.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;}).on('drag',function(e,d){d.fx=e.x;d.fy=e.y;}).on('end',function(e,d){if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}));return function(){sim.stop();};}


/* ===== Observable @d3/gallery -- batch 2 (core d3, sandbox-safe) ===== */
function zoomTreemap(host){var svg=newSvg(host);var W=360,H=212;
  var data={name:'root',children:d3.range(5).map(function(i){return {name:'G'+i,children:d3.range(2+Math.floor(Math.random()*4)).map(function(j){return {name:i+'.'+j,value:12+Math.random()*70};})};})};
  var root=d3.hierarchy(data).sum(function(d){return d.value;}).sort(function(a,b){return b.value-a.value;});
  (d3.treemap().tile(d3.treemapBinary||d3.treemapSquarify).size([W,H]).paddingInner(2))(root);
  var x=d3.scaleLinear().range([0,W]),y=d3.scaleLinear().range([0,H]);var g=svg.append('g');var cur=root;
  function render(node){cur=node;x.domain([node.x0,node.x1]);y.domain([node.y0,node.y1]);var leaves=node.children||[node];
    var sel=g.selectAll('g.cell').data(leaves,function(d){return d.data.name;});sel.exit().remove();
    var en=sel.enter().append('g').attr('class','cell');en.append('rect');en.append('text');
    var m=en.merge(sel).style('cursor','pointer').on('click',function(event,d){event.stopPropagation();render(d.children?d:(node.parent||root));});
    m.select('rect').transition().duration(500).attr('x',function(d){return x(d.x0);}).attr('y',function(d){return y(d.y0);}).attr('width',function(d){return Math.max(0,x(d.x1)-x(d.x0)-1);}).attr('height',function(d){return Math.max(0,y(d.y1)-y(d.y0)-1);}).attr('rx',2).attr('fill',function(d,i){return PAL[i%PAL.length];}).attr('opacity',0.85).attr('stroke',CARD);
    m.select('text').attr('x',function(d){return x(d.x0)+5;}).attr('y',function(d){return y(d.y0)+14;}).attr('font-size',10).attr('font-weight',600).attr('font-family',FONT).attr('fill','#fff').style('pointer-events','none').text(function(d){return d.data.name;});}
  render(root);svg.on('click',function(){if(cur.parent)render(cur.parent);});}
function alluvial(host){var svg=newSvg(host);var cats=[2,3,2];var names=[['A','B'],['X','Y','Z'],['P','Q']];var N=240;
  var items=d3.range(N).map(function(){return cats.map(function(c){return Math.floor(Math.random()*c);});});
  var X=[46,183,318],bw=12,H=184,top=24,gap=10;
  var stageNodes=cats.map(function(c,si){var counts=d3.range(c).map(function(k){return items.filter(function(it){return it[si]===k;}).length;});var tot=d3.sum(counts);var scl=(H-(c-1)*gap)/tot;var yy=top;
    return counts.map(function(cnt,k){var nd={k:k,cnt:cnt,y0:yy,h:cnt*scl};yy+=cnt*scl+gap;return nd;});});
  for(var s=0;s<cats.length-1;s++){(function(si){var L=stageNodes[si],Rr=stageNodes[si+1];var lo=L.map(function(){return 0;}),ro=Rr.map(function(){return 0;});
    for(var a=0;a<L.length;a++)for(var b=0;b<Rr.length;b++){var cnt=items.filter(function(it){return it[si]===a&&it[si+1]===b;}).length;if(!cnt)continue;
      var hL=cnt*(L[a].h/L[a].cnt),hR=cnt*(Rr[b].h/Rr[b].cnt);var y0=L[a].y0+lo[a],y1=Rr[b].y0+ro[b];lo[a]+=hL;ro[b]+=hR;
      var x0=X[si]+bw,x1=X[si+1],cx=(x0+x1)/2;
      svg.append('path').attr('d','M'+x0+','+y0+'C'+cx+','+y0+' '+cx+','+y1+' '+x1+','+y1+'L'+x1+','+(y1+hR)+'C'+cx+','+(y1+hR)+' '+cx+','+(y0+hL)+' '+x0+','+(y0+hL)+'Z').attr('fill',PAL[a%PAL.length]).attr('opacity',0.3);}})(s);}
  stageNodes.forEach(function(nodes,si){nodes.forEach(function(nd){svg.append('rect').attr('x',X[si]).attr('y',nd.y0).attr('width',bw).attr('height',nd.h).attr('fill',PAL[nd.k%PAL.length]);svg.append('text').attr('x',X[si]+bw/2).attr('y',nd.y0-3).attr('text-anchor','middle').attr('font-size',8).attr('font-family',FONT).attr('fill',INK2).text(names[si][nd.k]);});});}
function qqPlot(host){var svg=newSvg(host);var n=70;var data=d3.range(n).map(rnorm).sort(d3.ascending);var x=d3.scaleLinear().domain([-3,3]).range([38,350]);var y=d3.scaleLinear().domain([-3,3]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(6)));axc(svg.append('g').attr('transform','translate(38,0)').call(d3.axisLeft(y).ticks(6)));
  function probit(p){var a=[-39.69683028665376,220.9460984245205,-275.9285104469687,138.357751867269,-30.66479806614716,2.506628277459239],b=[-54.47609879822406,161.5858368580409,-155.6989798598866,66.80131188771972,-13.28068155288572],c=[-0.007784894002430293,-0.3223964580411365,-2.400758277161838,-2.549732539343734,4.374664141464968,2.938163982698783],d=[0.007784695709041462,0.3224671290700398,2.445134137142996,3.754408661907416];var pl=0.02425,q,r;
    if(p<pl){q=Math.sqrt(-2*Math.log(p));return(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);}
    if(p<=1-pl){q=p-0.5;r=q*q;return(((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/(((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1);}
    q=Math.sqrt(-2*Math.log(1-p));return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);}
  svg.append('line').attr('x1',x(-3)).attr('y1',y(-3)).attr('x2',x(3)).attr('y2',y(3)).attr('stroke',HILITE).attr('stroke-dasharray','4,3');
  svg.append('g').selectAll('circle').data(data).join('circle').attr('cx',function(_,i){return x(probit((i+0.5)/n));}).attr('cy',function(v){return y(v);}).attr('r',3).attr('fill',ACCENT).attr('opacity',0.7);}
function normStackArea(host){var svg=newSvg(host);var keys=['a','b','c','d'];var N=26;var data=d3.range(N).map(function(i){var o={i:i};keys.forEach(function(k,ki){o[k]=5+10*Math.abs(Math.sin(i/4+ki))+Math.random()*4;});return o;});
  var st=d3.stack().keys(keys).offset(d3.stackOffsetExpand)(data);var x=d3.scaleLinear().domain([0,N-1]).range([8,352]);var y=d3.scaleLinear().domain([0,1]).range([210,10]);
  svg.selectAll('path').data(st).join('path').attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('opacity',0.85).attr('d',d3.area().x(function(d){return x(d.data.i);}).y0(function(d){return y(d[0]);}).y1(function(d){return y(d[1]);}).curve(d3.curveBasis));}
function thresholdLine(host){var svg=newSvg(host);var N=50;var data=d3.range(N).map(function(i){return [i,50+28*Math.sin(i/6)+Math.random()*8];});var x=d3.scaleLinear().domain([0,N-1]).range([34,350]);var y=d3.scaleLinear().domain([0,100]).range([205,12]);var thr=55;
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(6)));axc(svg.append('g').attr('transform','translate(34,0)').call(d3.axisLeft(y).ticks(4)));
  var yt=y(thr);var off=(yt-12)/(205-12);var defs=svg.append('defs');var grad=defs.append('linearGradient').attr('id','thrln').attr('gradientUnits','userSpaceOnUse').attr('x1',0).attr('y1',12).attr('x2',0).attr('y2',205);
  grad.append('stop').attr('offset',off).attr('stop-color',PAL[1]);grad.append('stop').attr('offset',off).attr('stop-color',HILITE);
  svg.append('line').attr('x1',34).attr('x2',350).attr('y1',yt).attr('y2',yt).attr('stroke',INK2).attr('stroke-dasharray','3,3');
  svg.append('path').datum(data).attr('fill','none').attr('stroke','url(#thrln)').attr('stroke-width',2.2).attr('d',d3.line().x(function(d){return x(d[0]);}).y(function(d){return y(d[1]);}).curve(d3.curveMonotoneX));}
function roseChart(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,118)');var N=12;var data=d3.range(N).map(function(){return 20+Math.random()*80;});
  var ang=d3.scaleBand().domain(d3.range(N)).range([0,2*Math.PI]).padding(0.04);var r=(d3.scaleRadial?d3.scaleRadial():d3.scaleLinear()).domain([0,100]).range([0,102]);
  [25,50,75,100].forEach(function(t){g.append('circle').attr('r',r(t)).attr('fill','none').attr('stroke',GRIDC);});
  var arc=d3.arc().innerRadius(0).outerRadius(function(d){return r(d);}).startAngle(function(_,i){return ang(i);}).endAngle(function(_,i){return ang(i)+ang.bandwidth();}).padAngle(0.01);
  g.selectAll('path').data(data).join('path').attr('fill',function(_,i){return PAL[i%PAL.length];}).attr('opacity',0.82).attr('d',arc);}
function spikeChart(host){var svg=newSvg(host);var N=42;var data=d3.range(N).map(function(i){return [i,Math.abs(45+40*Math.sin(i/5)+rnorm()*18)];});var x=d3.scaleLinear().domain([0,N-1]).range([20,345]);var maxv=d3.max(data,function(d){return d[1];});var len=d3.scaleLinear().domain([0,maxv]).range([0,150]);var baseY=200;
  axc(svg.append('g').attr('transform','translate(0,200)').call(d3.axisBottom(x).ticks(7)));
  svg.selectAll('path').data(data).join('path').attr('d',function(d){var cx=x(d[0]),h=len(d[1]);return 'M'+(cx-3)+','+baseY+'L'+cx+','+(baseY-h)+'L'+(cx+3)+','+baseY+'Z';}).attr('fill',ACCENT).attr('opacity',0.72).attr('stroke',ACCENT).attr('stroke-width',0.5);}
function marginalHist(host){var svg=newSvg(host);var n=170;var data=d3.range(n).map(function(){return [rnormM(0.5,0.15),rnormM(0.5,0.15)];});var x=d3.scaleLinear().domain([0,1]).range([40,330]);var y=d3.scaleLinear().domain([0,1]).range([178,46]);
  svg.append('g').selectAll('circle').data(data).join('circle').attr('cx',function(d){return x(d[0]);}).attr('cy',function(d){return y(d[1]);}).attr('r',2.4).attr('fill',ACCENT).attr('opacity',0.5);
  var bx=d3.bin().domain([0,1]).thresholds(26)(data.map(function(d){return d[0];}));var mx=d3.max(bx,function(b){return b.length;})||1;var hy=d3.scaleLinear().domain([0,mx]).range([0,32]);
  svg.append('g').selectAll('rect').data(bx).join('rect').attr('x',function(b){return x(b.x0)+0.5;}).attr('width',function(b){return Math.max(0,x(b.x1)-x(b.x0)-1);}).attr('y',function(b){return 40-hy(b.length);}).attr('height',function(b){return hy(b.length);}).attr('fill',PAL[2]).attr('opacity',0.7);
  var by=d3.bin().domain([0,1]).thresholds(26)(data.map(function(d){return d[1];}));var my=d3.max(by,function(b){return b.length;})||1;var hx=d3.scaleLinear().domain([0,my]).range([0,24]);
  svg.append('g').selectAll('rect').data(by).join('rect').attr('y',function(b){return y(b.x1)+0.5;}).attr('height',function(b){return Math.max(0,y(b.x0)-y(b.x1)-1);}).attr('x',334).attr('width',function(b){return hx(b.length);}).attr('fill',PAL[2]).attr('opacity',0.7);}


/* ===== Observable @d3/gallery -- batch 3 (core d3, sandbox-safe) ===== */
function regScatter(host){var svg=newSvg(host);var n=55;var data=d3.range(n).map(function(){var gx=Math.random();var gy=0.18+0.62*gx+rnorm()*0.11;return [gx,Math.max(0,Math.min(1,gy))];});
  var x=d3.scaleLinear().domain([0,1]).range([34,350]);var y=d3.scaleLinear().domain([0,1]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(5)));axc(svg.append('g').attr('transform','translate(34,0)').call(d3.axisLeft(y).ticks(5)));
  var mx=d3.mean(data,function(d){return d[0];}),my=d3.mean(data,function(d){return d[1];});var num=0,den=0;data.forEach(function(d){num+=(d[0]-mx)*(d[1]-my);den+=(d[0]-mx)*(d[0]-mx);});var b=num/den,a=my-b*mx;
  svg.append('g').selectAll('circle').data(data).join('circle').attr('cx',function(d){return x(d[0]);}).attr('cy',function(d){return y(d[1]);}).attr('r',3.5).attr('fill',ACCENT).attr('opacity',0.65);
  svg.append('line').attr('x1',x(0)).attr('y1',y(a)).attr('x2',x(1)).attr('y2',y(a+b)).attr('stroke',HILITE).attr('stroke-width',2);}
function ternary(host){var svg=newSvg(host);var S=150,cx=180,top=18;var A=[cx,top],B=[cx-S/2,top+S*Math.sqrt(3)/2],C=[cx+S/2,top+S*Math.sqrt(3)/2];
  function tp(a,b,c){var s=a+b+c;a/=s;b/=s;c/=s;return [a*A[0]+b*B[0]+c*C[0],a*A[1]+b*B[1]+c*C[1]];}
  svg.append('path').attr('d','M'+A+'L'+B+'L'+C+'Z').attr('fill','none').attr('stroke',GRIDC);
  for(var g=1;g<5;g++){var f=g/5;svg.append('path').attr('d','M'+tp(1-f,f,0)+'L'+tp(1-f,0,f)).attr('stroke',GRIDC).attr('stroke-width',0.4).attr('fill','none');
    svg.append('path').attr('d','M'+tp(f,1-f,0)+'L'+tp(0,1-f,f)).attr('stroke',GRIDC).attr('stroke-width',0.4).attr('fill','none');
    svg.append('path').attr('d','M'+tp(f,0,1-f)+'L'+tp(0,f,1-f)).attr('stroke',GRIDC).attr('stroke-width',0.4).attr('fill','none');}
  [['A',A,-6],['B',B,-4],['C',C,-4]].forEach(function(L){svg.append('text').attr('x',L[1][0]).attr('y',L[1][1]+L[2]).attr('text-anchor','middle').attr('font-size',10).attr('font-weight',700).attr('font-family',FONT).attr('fill',INK2).text(L[0]);});
  d3.range(40).forEach(function(){var a=Math.random(),b=Math.random()*(1-a),c=1-a-b;var p=tp(a,b,c);svg.append('circle').attr('cx',p[0]).attr('cy',p[1]).attr('r',3).attr('fill',PAL[Math.floor(a*3)%PAL.length]).attr('opacity',0.7);});}
function gapsLine(host){var svg=newSvg(host);var N=48;var data=d3.range(N).map(function(i){var miss=(i>14&&i<21)||(i>32&&i<36);return {i:i,v:miss?null:50+28*Math.sin(i/6)+Math.random()*7};});
  var x=d3.scaleLinear().domain([0,N-1]).range([34,350]);var y=d3.scaleLinear().domain([0,100]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(6)));axc(svg.append('g').attr('transform','translate(34,0)').call(d3.axisLeft(y).ticks(4)));
  svg.append('path').datum(data).attr('fill','none').attr('stroke',GRIDC).attr('stroke-width',1).attr('stroke-dasharray','2,2').attr('d',d3.line().x(function(d){return x(d.i);}).y(function(d){return y(d.v==null?50:d.v);}));
  svg.append('path').datum(data).attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',2).attr('d',d3.line().defined(function(d){return d.v!=null;}).x(function(d){return x(d.i);}).y(function(d){return y(d.v);}).curve(d3.curveMonotoneX));
  svg.append('g').selectAll('circle').data(data.filter(function(d){return d.v!=null;})).join('circle').attr('cx',function(d){return x(d.i);}).attr('cy',function(d){return y(d.v);}).attr('r',2.4).attr('fill',ACCENT);}
function movingAvg(host){var svg=newSvg(host);var N=80;var raw=[];var v=55;for(var i=0;i<N;i++){v+=(Math.random()-0.5)*9;raw.push(Math.max(10,Math.min(95,v)));}
  var k=9,ma=raw.map(function(_,i){var s=0,c=0;for(var j=Math.max(0,i-k);j<=i;j++){s+=raw[j];c++;}return s/c;});
  var x=d3.scaleLinear().domain([0,N-1]).range([34,350]);var y=d3.scaleLinear().domain([0,100]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(6)));axc(svg.append('g').attr('transform','translate(34,0)').call(d3.axisLeft(y).ticks(4)));
  svg.append('path').datum(raw).attr('fill','none').attr('stroke',GRIDC).attr('stroke-width',1).attr('d',d3.line().x(function(_,i){return x(i);}).y(function(d){return y(d);}));
  svg.append('path').datum(ma).attr('fill','none').attr('stroke',HILITE).attr('stroke-width',2.4).attr('d',d3.line().x(function(_,i){return x(i);}).y(function(d){return y(d);}).curve(d3.curveBasis));}
function dualAxis(host){var svg=newSvg(host);var cats=['Jan','Feb','Mar','Apr','May','Jun','Jul'];var bars=cats.map(function(){return 20+Math.random()*60;});var ln=cats.map(function(){return 2+Math.random()*8;});
  var x=d3.scaleBand().domain(cats).range([40,336]).padding(0.3);var yL=d3.scaleLinear().domain([0,90]).range([200,14]);var yR=d3.scaleLinear().domain([0,11]).range([200,14]);
  axc(svg.append('g').attr('transform','translate(0,200)').call(d3.axisBottom(x)));axc(svg.append('g').attr('transform','translate(40,0)').call(d3.axisLeft(yL).ticks(4)));
  var gr=svg.append('g').attr('transform','translate(336,0)').call(d3.axisRight(yR).ticks(4));gr.selectAll('text').attr('fill',HILITE);gr.selectAll('line,path').attr('stroke',GRIDC);
  svg.selectAll('rect').data(bars).join('rect').attr('x',function(_,i){return x(cats[i]);}).attr('width',x.bandwidth()).attr('y',function(d){return yL(d);}).attr('height',function(d){return 200-yL(d);}).attr('rx',2).attr('fill',PAL[0]).attr('opacity',0.85);
  svg.append('path').datum(ln).attr('fill','none').attr('stroke',HILITE).attr('stroke-width',2.4).attr('d',d3.line().x(function(_,i){return x(cats[i])+x.bandwidth()/2;}).y(function(d){return yR(d);}).curve(d3.curveMonotoneX));
  svg.selectAll('circle').data(ln).join('circle').attr('cx',function(_,i){return x(cats[i])+x.bandwidth()/2;}).attr('cy',function(d){return yR(d);}).attr('r',3).attr('fill',HILITE);}
function barcode(host){var svg=newSvg(host);var groups=['A','B','C'];var y=d3.scaleBand().domain(groups).range([24,196]).padding(0.4);var x=d3.scaleLinear().domain([0,24]).range([42,350]);
  axc(svg.append('g').attr('transform','translate(0,200)').call(d3.axisBottom(x).ticks(8)));axc(svg.append('g').attr('transform','translate(42,0)').call(d3.axisLeft(y)));
  groups.forEach(function(gname,gi){var times=d3.range(30+Math.floor(Math.random()*20)).map(function(){return Math.max(0,Math.min(24,rnormM(10+gi*3,4)));});
    svg.append('g').selectAll('line.bc'+gi).data(times).join('line').attr('x1',function(t){return x(t);}).attr('x2',function(t){return x(t);}).attr('y1',y(gname)).attr('y2',y(gname)+y.bandwidth()).attr('stroke',PAL[gi%PAL.length]).attr('stroke-width',1).attr('opacity',0.5);});}
function vCalendar(host){var svg=d3.select(host).append('svg').attr('width','100%').attr('height',230).attr('viewBox','0 0 360 230');var cs=15;var color=d3.scaleSequential(d3.interpolateViridis).domain([0,1]);
  var weeks=12,ox=70,oy=24;['M','T','W','T','F','S','S'].forEach(function(d,i){svg.append('text').attr('x',ox+i*cs+cs/2).attr('y',18).attr('text-anchor','middle').attr('font-size',8).attr('font-family',FONT).attr('fill',INK2).text(d);});
  for(var w=0;w<weeks;w++){svg.append('text').attr('x',ox-8).attr('y',oy+w*cs+cs/2+3).attr('text-anchor','end').attr('font-size',7).attr('font-family',FONT).attr('fill',INK2).text('W'+(w+1));
    for(var d=0;d<7;d++){var v=Math.max(0,Math.min(1,0.5+0.4*Math.sin((w*7+d)/9)+(Math.random()-0.5)*0.4));svg.append('rect').attr('x',ox+d*cs).attr('y',oy+w*cs).attr('width',cs-2).attr('height',cs-2).attr('rx',2).attr('fill',color(v));}}}
function seasonalRadial(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,118)');var N=48;var years=3;
  var ang=d3.scaleLinear().domain([0,N]).range([0,2*Math.PI]);var r=d3.scaleLinear().domain([0,100]).range([24,104]);
  [25,50,75,100].forEach(function(t){g.append('circle').attr('r',r(t)).attr('fill','none').attr('stroke',GRIDC);});
  ['Q1','Q2','Q3','Q4'].forEach(function(q,i){var a=i/4*2*Math.PI-Math.PI/2;g.append('text').attr('x',Math.cos(a)*112).attr('y',Math.sin(a)*112+3).attr('text-anchor','middle').attr('font-size',9).attr('font-family',FONT).attr('fill',INK2).text(q);});
  d3.range(years).forEach(function(yr){var data=d3.range(N+1).map(function(i){return 45+25*Math.sin((i/N)*2*Math.PI-0.6)+yr*6+Math.random()*6;});
    var line=d3.lineRadial().angle(function(_,i){return ang(i);}).radius(function(d){return r(d);}).curve(d3.curveCardinalClosed);
    g.append('path').datum(data.slice(0,N)).attr('fill','none').attr('stroke',PAL[yr]).attr('stroke-width',1.8).attr('opacity',0.8).attr('d',line);});}


/* ===== Observable @d3/gallery -- batch 4 (core d3, sandbox-safe) ===== */
function tangledTree(host){var svg=newSvg(host);
  var levels=[[{id:'a'}],[{id:'b',p:['a']},{id:'c',p:['a']}],[{id:'d',p:['b']},{id:'e',p:['b','c']},{id:'f',p:['c']}],[{id:'g',p:['d','e']},{id:'h',p:['e','f']}]];
  var colW=86,x0=30,yGap=20,top=24;var pos={};var nodes=[];
  levels.forEach(function(lv,li){lv.forEach(function(nd,ni){var y=top+ni*((190)/(Math.max(1,lv.length-1)||1));if(lv.length===1)y=110;pos[nd.id]={x:x0+li*colW,y:y};nd.x=pos[nd.id].x;nd.y=y;nodes.push(nd);});});
  nodes.forEach(function(nd){(nd.p||[]).forEach(function(pid){var a=pos[pid],b=pos[nd.id];var mx=(a.x+b.x)/2;
    svg.append('path').attr('fill','none').attr('stroke',PAL[(nd.id.charCodeAt(0))%PAL.length]).attr('stroke-width',2).attr('opacity',0.6).attr('d','M'+a.x+','+a.y+'C'+mx+','+a.y+' '+mx+','+b.y+' '+b.x+','+b.y);});});
  svg.append('g').selectAll('circle').data(nodes).join('circle').attr('cx',function(d){return d.x;}).attr('cy',function(d){return d.y;}).attr('r',6).attr('fill',function(d){return PAL[d.id.charCodeAt(0)%PAL.length];}).attr('stroke',CARD).attr('stroke-width',1.5);
  svg.append('g').selectAll('text').data(nodes).join('text').attr('x',function(d){return d.x;}).attr('y',function(d){return d.y-10;}).attr('text-anchor','middle').attr('font-size',9).attr('font-family',FONT).attr('fill',INK2).text(function(d){return d.id.toUpperCase();});}
function phyloTree(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');
  var data={name:'root',children:d3.range(5).map(function(i){return {name:'c'+i,children:d3.range(2+i%3).map(function(j){return {name:'t'+i+j,v:1};})};})};
  var root=d3.hierarchy(data);d3.cluster().size([2*Math.PI,96]).separation(function(a,b){return (a.parent===b.parent?1:2);})(root);
  g.append('g').attr('fill','none').attr('stroke',ACCENT).attr('stroke-opacity',0.55).selectAll('path').data(root.links()).join('path')
    .attr('d',function(d){var sa=d.source.x-Math.PI/2,ta=d.target.x-Math.PI/2;var s=[Math.cos(sa)*d.source.y,Math.sin(sa)*d.source.y];var t=[Math.cos(ta)*d.target.y,Math.sin(ta)*d.target.y];
      return 'M'+s[0]+','+s[1]+'A'+d.source.y+','+d.source.y+' 0 0 '+(d.target.x>d.source.x?1:0)+' '+Math.cos(ta)*d.source.y+','+Math.sin(ta)*d.source.y+'L'+t[0]+','+t[1];});
  g.append('g').selectAll('circle').data(root.descendants()).join('circle').attr('transform',function(d){var a=d.x-Math.PI/2;return 'translate('+Math.cos(a)*d.y+','+Math.sin(a)*d.y+')';}).attr('r',function(d){return d.children?2.5:3.5;}).attr('fill',function(d){return d.children?INK2:ACCENT;});}
function mirrorBeeswarm(host){var svg=newSvg(host);var x=d3.scaleLinear().domain([-3,3]).range([24,345]);
  axc(svg.append('g').attr('transform','translate(0,118)').call(d3.axisBottom(x).ticks(6)));
  [[-1,PAL[0]],[1,PAL[4]]].forEach(function(side){var dir=side[0];var nodes=d3.range(70).map(function(){return {v:rnorm()};});
    var sim=d3.forceSimulation(nodes).force('x',d3.forceX(function(d){return x(d.v);}).strength(1)).force('y',d3.forceY(118+dir*4).strength(0.08)).force('collide',d3.forceCollide(4)).stop();
    for(var i=0;i<140;i++)sim.tick();
    svg.append('g').selectAll('c').data(nodes).join('circle').attr('cx',function(d){return d.x;}).attr('cy',function(d){return 118+dir*Math.abs(d.y-118);}).attr('r',3.5).attr('fill',side[1]).attr('opacity',0.78).attr('stroke',CARD).attr('stroke-width',0.4);});}
function tadpoles(host){var svg=newSvg(host);var W=360,H=230,N=26;
  var pods=d3.range(N).map(function(i){return {x:Math.random()*W,y:Math.random()*H,a:Math.random()*2*Math.PI,sp:0.6+Math.random()*1.2,c:PAL[i%PAL.length],ph:Math.random()*6};});
  var g=svg.append('g');var sel=g.selectAll('path').data(pods).join('path').attr('fill',function(d){return d.c;}).attr('opacity',0.85);var t=0;
  function frame(){t+=0.15;pods.forEach(function(d){d.a+=Math.sin(t+d.ph)*0.12;d.x+=Math.cos(d.a)*d.sp;d.y+=Math.sin(d.a)*d.sp;if(d.x<0)d.x+=W;if(d.x>W)d.x-=W;if(d.y<0)d.y+=H;if(d.y>H)d.y-=H;});
    sel.attr('transform',function(d){return 'translate('+d.x+','+d.y+') rotate('+(d.a*180/Math.PI)+')';}).attr('d',function(d){var wig=Math.sin(t*3+d.ph)*5;return 'M4,0 Q-6,'+wig+' -12,0 Q-6,'+(-wig)+' 4,0 Z';});}
  frame();var iv=setInterval(frame,40);return function(){clearInterval(iv);};}
function predatorPrey(host){var svg=newSvg(host);var a=1.1,b=0.4,c=0.4,d=1.1,dt=0.012;var x=1.0,y=1.0;var pts=[];
  for(var i=0;i<2600;i++){var dx=a*x-b*x*y,dy=c*x*y-d*y;x+=dx*dt;y+=dy*dt;if(i%3===0)pts.push([x,y]);}
  var sx=d3.scaleLinear().domain(d3.extent(pts,function(p){return p[0];})).range([34,350]);var sy=d3.scaleLinear().domain(d3.extent(pts,function(p){return p[1];})).range([205,14]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(sx).ticks(5)));axc(svg.append('g').attr('transform','translate(34,0)').call(d3.axisLeft(sy).ticks(5)));
  var color=d3.scaleSequential(d3.interpolateViridis).domain([0,pts.length]);
  svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx',function(p){return sx(p[0]);}).attr('cy',function(p){return sy(p[1]);}).attr('r',1.3).attr('fill',function(_,i){return color(i);}).attr('opacity',0.8);}
function stippling(host){var svg=newSvg(host);var W=360,H=230;var n=600;
  var pts=d3.range(n).map(function(){var r,x,y;do{x=Math.random();y=Math.random();var dx=x-0.5,dy=y-0.5;r=Math.sqrt(dx*dx+dy*dy);}while(Math.random()>Math.exp(-r*r*6));return [x*W,y*H];});
  for(var it=0;it<3;it++){var del=d3.Delaunay.from(pts);var vor=del.voronoi([0,0,W,H]);var cent=pts.map(function(){return [0,0,0];});
    for(var i=0;i<n;i++){var cell=vor.cellPolygon(i);if(!cell)continue;var cx=0,cy=0,ar=0;for(var j=0;j<cell.length-1;j++){var x0=cell[j][0],y0=cell[j][1],x1=cell[j+1][0],y1=cell[j+1][1];var f=x0*y1-x1*y0;ar+=f;cx+=(x0+x1)*f;cy+=(y0+y1)*f;}ar*=0.5;if(ar){cent[i]=[cx/(6*ar),cy/(6*ar)];}else cent[i]=pts[i];}
    pts=cent.map(function(c){return [Math.max(0,Math.min(W,c[0])),Math.max(0,Math.min(H,c[1]))];});}
  svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx',function(d){return d[0];}).attr('cy',function(d){return d[1];}).attr('r',1.3).attr('fill',INK);}
function shapeScatter(host){var svg=newSvg(host);var sym=[d3.symbolCircle,d3.symbolSquare,d3.symbolTriangle,d3.symbolDiamond,d3.symbolStar,d3.symbolCross];
  var x=d3.scaleLinear().domain([0,1]).range([30,350]);var y=d3.scaleLinear().domain([0,1]).range([205,12]);
  axc(svg.append('g').attr('transform','translate(0,205)').call(d3.axisBottom(x).ticks(5)));axc(svg.append('g').attr('transform','translate(30,0)').call(d3.axisLeft(y).ticks(5)));
  var data=d3.range(48).map(function(){return {x:Math.random(),y:Math.random(),g:Math.floor(Math.random()*6)};});
  svg.append('g').selectAll('path').data(data).join('path').attr('transform',function(d){return 'translate('+x(d.x)+','+y(d.y)+')';}).attr('d',function(d){return d3.symbol(sym[d.g],70)();}).attr('fill',function(d){return PAL[d.g%PAL.length];}).attr('opacity',0.78);}
function phasesMoon(host){var svg=newSvg(host);var cols=8,rows=4,n=cols*rows;var r=18,padX=(360-cols*2*r)/(cols+1),padY=(230-rows*2*r)/(rows+1);
  for(var i=0;i<n;i++){var cx=padX+(i%cols)*(2*r+padX)+r,cy=padY+Math.floor(i/cols)*(2*r+padY)+r;var ph=i/n;
    svg.append('circle').attr('cx',cx).attr('cy',cy).attr('r',r).attr('fill','#11131a');
    var k=Math.cos(ph*2*Math.PI);var lit=svg.append('path').attr('fill','#F4E8C1');
    var left=ph<0.5;var sweep=left?0:1;var rx=Math.abs(k)*r;
    lit.attr('d','M'+cx+','+(cy-r)+'A'+r+','+r+' 0 0 '+(left?1:0)+' '+cx+','+(cy+r)+'A'+rx+','+r+' 0 0 '+sweep+' '+cx+','+(cy-r)+'Z');
    svg.append('circle').attr('cx',cx).attr('cy',cy).attr('r',r).attr('fill','none').attr('stroke',GRIDC).attr('stroke-width',0.5);}}


/* ===== Generative art & simulation (web-famous showpieces, core d3) ===== */
function fourierEpicycles(host){var svg=newSvg(host);var cx=72,cy=115;var terms=6;
  var coeffs=d3.range(terms).map(function(k){var n=2*k+1;return {n:n,r:52*(4/(n*Math.PI))};});
  var circG=svg.append('g'),armG=svg.append('g');var wave=[];
  var tracePath=svg.append('path').attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',1.6);
  var connector=svg.append('line').attr('stroke',INK2).attr('stroke-width',0.6).attr('stroke-dasharray','2,2');var t=0;
  function frame(){t+=0.05;var x=cx,y=cy;circG.selectAll('*').remove();armG.selectAll('*').remove();
    coeffs.forEach(function(c){var px=x,py=y;x+=c.r*Math.cos(c.n*t);y+=c.r*Math.sin(c.n*t);
      circG.append('circle').attr('cx',px).attr('cy',py).attr('r',Math.abs(c.r)).attr('fill','none').attr('stroke',GRIDC).attr('stroke-width',0.7);
      armG.append('line').attr('x1',px).attr('y1',py).attr('x2',x).attr('y2',y).attr('stroke',INK2).attr('stroke-width',0.7);});
    wave.unshift(y);if(wave.length>250)wave.pop();connector.attr('x1',x).attr('y1',y).attr('x2',152).attr('y2',wave[0]);
    tracePath.attr('d','M'+wave.map(function(wy,i){return (152+i*0.82).toFixed(1)+','+wy.toFixed(1);}).join('L'));}
  frame();var iv=setInterval(frame,40);return function(){clearInterval(iv);};}
function doublePendulum(host){var svg=newSvg(host);var cx=180,cy=92;var r1=52,r2=52,m1=10,m2=10,G=1;
  var a1=Math.PI/2+0.7,a2=Math.PI/2+0.1,v1=0,v2=0;var trail=[];
  var tp=svg.append('path').attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',1).attr('opacity',0.55);
  var rod1=svg.append('line').attr('stroke',INK2).attr('stroke-width',2);var rod2=svg.append('line').attr('stroke',INK2).attr('stroke-width',2);
  var b1=svg.append('circle').attr('r',6).attr('fill',PAL[0]);var b2=svg.append('circle').attr('r',6).attr('fill',PAL[4]);
  function step(){var dt=0.06;
    var n1=-G*(2*m1+m2)*Math.sin(a1)-m2*G*Math.sin(a1-2*a2)-2*Math.sin(a1-a2)*m2*(v2*v2*r2+v1*v1*r1*Math.cos(a1-a2));
    var d1=r1*(2*m1+m2-m2*Math.cos(2*a1-2*a2));var ac1=n1/d1;
    var n2=2*Math.sin(a1-a2)*(v1*v1*r1*(m1+m2)+G*(m1+m2)*Math.cos(a1)+v2*v2*r2*m2*Math.cos(a1-a2));
    var d2=r2*(2*m1+m2-m2*Math.cos(2*a1-2*a2));var ac2=n2/d2;
    v1+=ac1*dt;v2+=ac2*dt;a1+=v1*dt;a2+=v2*dt;}
  function frame(){for(var k=0;k<3;k++)step();var x1=cx+r1*Math.sin(a1),y1=cy+r1*Math.cos(a1);var x2=x1+r2*Math.sin(a2),y2=y1+r2*Math.cos(a2);
    rod1.attr('x1',cx).attr('y1',cy).attr('x2',x1).attr('y2',y1);rod2.attr('x1',x1).attr('y1',y1).attr('x2',x2).attr('y2',y2);
    b1.attr('cx',x1).attr('cy',y1);b2.attr('cx',x2).attr('cy',y2);trail.unshift([x2,y2]);if(trail.length>170)trail.pop();
    tp.attr('d','M'+trail.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1);}).join('L'));}
  frame();var iv=setInterval(frame,30);return function(){clearInterval(iv);};}
function fractalTree(host){var svg=newSvg(host);var g=svg.append('g');var t=0;
  function branch(x,y,ang,len,depth){if(depth===0||len<2)return;var sway=Math.sin(t+depth*0.5)*0.045;
    var x2=x+Math.cos(ang)*len,y2=y+Math.sin(ang)*len;
    g.append('line').attr('x1',x).attr('y1',y).attr('x2',x2).attr('y2',y2).attr('stroke',depth>3?'#6B4F3A':PAL[1]).attr('stroke-width',depth*0.6).attr('stroke-linecap','round').attr('opacity',0.9);
    branch(x2,y2,ang-0.5+sway,len*0.72,depth-1);branch(x2,y2,ang+0.5+sway,len*0.72,depth-1);}
  function frame(){t+=0.03;g.selectAll('*').remove();branch(180,222,-Math.PI/2,44,9);}
  frame();var iv=setInterval(frame,60);return function(){clearInterval(iv);};}
function flowField(host){var svg=newSvg(host);var W=360,H=230,N=170;var parts=d3.range(N).map(function(){return {x:Math.random()*W,y:Math.random()*H};});
  var g=svg.append('g');var color=d3.scaleSequential(d3.interpolateViridis).domain([0,W]);var t=0;
  function field(x,y){return Math.sin(x*0.02+t)+Math.cos(y*0.021-t*0.7)+0.6*Math.sin((x+y)*0.015);}
  function frame(){t+=0.015;parts.forEach(function(p){var a=field(p.x,p.y)*Math.PI;var nx=p.x+Math.cos(a)*1.7,ny=p.y+Math.sin(a)*1.7;
    g.append('line').attr('x1',p.x).attr('y1',p.y).attr('x2',nx).attr('y2',ny).attr('stroke',color(p.x)).attr('stroke-width',0.8).attr('opacity',0.22);
    p.x=nx;p.y=ny;if(p.x<0||p.x>W||p.y<0||p.y>H){p.x=Math.random()*W;p.y=Math.random()*H;}});
    var ls=g.selectAll('line');if(ls.size()>2500)ls.filter(function(_,i){return i<N;}).remove();}
  frame();var iv=setInterval(frame,45);return function(){clearInterval(iv);};}
function cliffordAttractor(host){var svg=newSvg(host);var a=-1.4,b=1.6,c=1.0,d=0.7;var x=0,y=0;var pts=[];
  for(var i=0;i<2400;i++){var nx=Math.sin(a*y)+c*Math.cos(a*x);var ny=Math.sin(b*x)+d*Math.cos(b*y);x=nx;y=ny;pts.push([x,y]);}
  var sx=d3.scaleLinear().domain([-2.2,2.2]).range([24,338]);var sy=d3.scaleLinear().domain([-2.2,2.2]).range([210,16]);var color=d3.scaleSequential(d3.interpolateViridis).domain([0,pts.length]);
  svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx',function(p){return sx(p[0]);}).attr('cy',function(p){return sy(p[1]);}).attr('r',0.7).attr('fill',function(_,i){return color(i);}).attr('opacity',0.7);}
function chaosGame(host){var svg=newSvg(host);var V=[[180,16],[26,214],[334,214]];var p=[180,115];var g=svg.append('g');var data=[];
  V.forEach(function(v,i){svg.append('circle').attr('cx',v[0]).attr('cy',v[1]).attr('r',3).attr('fill',PAL[i]);});
  function frame(){for(var k=0;k<45;k++){var vi=Math.floor(Math.random()*3);var v=V[vi];p=[(p[0]+v[0])/2,(p[1]+v[1])/2];data.push([p[0],p[1],vi]);}
    var c=g.selectAll('circle').data(data);c.enter().append('circle').attr('cx',function(d){return d[0];}).attr('cy',function(d){return d[1];}).attr('r',0.8).attr('fill',function(d){return PAL[d[2]];}).attr('opacity',0.75);
    if(data.length>1800)clearInterval(iv);}
  var iv=setInterval(frame,40);frame();return function(){clearInterval(iv);};}
function boids(host){var svg=newSvg(host);var W=360,H=230,N=46;var b=d3.range(N).map(function(i){return {x:Math.random()*W,y:Math.random()*H,vx:rnorm(),vy:rnorm(),c:PAL[i%PAL.length]};});
  var sel=svg.append('g').selectAll('path').data(b).join('path').attr('fill',function(d){return d.c;}).attr('opacity',0.85);
  function frame(){b.forEach(function(bi){var ax=0,ay=0,cx=0,cy=0,sx=0,sy=0,n=0;
    b.forEach(function(bj){if(bi===bj)return;var dx=bj.x-bi.x,dy=bj.y-bi.y,d2=dx*dx+dy*dy;if(d2<2500){ax+=bj.vx;ay+=bj.vy;cx+=bj.x;cy+=bj.y;n++;if(d2<420){sx-=dx;sy-=dy;}}});
    if(n){ax/=n;ay/=n;cx=cx/n-bi.x;cy=cy/n-bi.y;bi.vx+=(ax-bi.vx)*0.03+cx*0.0008+sx*0.004;bi.vy+=(ay-bi.vy)*0.03+cy*0.0008+sy*0.004;}
    var sp=Math.sqrt(bi.vx*bi.vx+bi.vy*bi.vy)||1;bi.vx=bi.vx/sp*1.6;bi.vy=bi.vy/sp*1.6;bi.x+=bi.vx;bi.y+=bi.vy;
    if(bi.x<0)bi.x+=W;if(bi.x>W)bi.x-=W;if(bi.y<0)bi.y+=H;if(bi.y>H)bi.y-=H;});
    sel.attr('transform',function(d){return 'translate('+d.x.toFixed(1)+','+d.y.toFixed(1)+') rotate('+(Math.atan2(d.vy,d.vx)*180/Math.PI).toFixed(1)+')';}).attr('d','M5,0 L-4,3 L-4,-3 Z');}
  frame();var iv=setInterval(frame,45);return function(){clearInterval(iv);};}
function gameOfLife(host){var svg=newSvg(host);var cols=45,rows=29,cs=8;var grid=d3.range(cols*rows).map(function(){return Math.random()<0.3?1:0;});var age=new Array(cols*rows).fill(0);
  var color=d3.scaleSequential(d3.interpolateViridis).domain([0,18]);var g=svg.append('g');
  function idx(c,r){return ((r+rows)%rows)*cols+((c+cols)%cols);}
  function step(){var ng=grid.slice();for(var r=0;r<rows;r++)for(var c=0;c<cols;c++){var nb=0;for(var dr=-1;dr<=1;dr++)for(var dc=-1;dc<=1;dc++){if(dr||dc)nb+=grid[idx(c+dc,r+dr)];}var i=r*cols+c;var al=grid[i]?((nb===2||nb===3)?1:0):(nb===3?1:0);age[i]=al?(grid[i]?age[i]+1:1):0;ng[i]=al;}grid=ng;}
  function frame(){step();var cells=[];for(var i=0;i<grid.length;i++)if(grid[i])cells.push(i);
    var rc=g.selectAll('rect').data(cells,function(d){return d;});rc.exit().remove();
    rc.enter().append('rect').attr('width',cs-1).attr('height',cs-1).attr('rx',1).merge(rc).attr('x',function(i){return (i%cols)*cs;}).attr('y',function(i){return Math.floor(i/cols)*cs;}).attr('fill',function(i){return color(Math.min(18,age[i]));});}
  frame();var iv=setInterval(frame,180);return function(){clearInterval(iv);};}


/* ===== Generative art & simulation (cont.) ===== */
function reactionDiffusion(host){var svg=newSvg(host);var W=60,H=38,cs=6;var A=[],B=[],dA=1.0,dB=0.5,f=0.055,k=0.062;
  for(var i=0;i<W*H;i++){A[i]=1;B[i]=0;}
  for(var s=0;s<14;s++){var cx=5+Math.floor(Math.random()*(W-10)),cy=5+Math.floor(Math.random()*(H-10));for(var yy=-2;yy<=2;yy++)for(var xx=-2;xx<=2;xx++)B[(cy+yy)*W+(cx+xx)]=1;}
  var color=d3.scaleSequential(d3.interpolateViridis).domain([0,0.4]);var g=svg.append('g');
  var rects=g.selectAll('rect').data(d3.range(W*H)).join('rect').attr('x',function(i){return (i%W)*cs;}).attr('y',function(i){return Math.floor(i/W)*cs;}).attr('width',cs).attr('height',cs).attr('shape-rendering','crispEdges');
  function lap(arr,i,x,y){var s=0;s+=arr[i]*-1;s+=(arr[y*W+((x-1+W)%W)]+arr[y*W+((x+1)%W)]+arr[((y-1+H)%H)*W+x]+arr[((y+1)%H)*W+x])*0.2;s+=(arr[((y-1+H)%H)*W+((x-1+W)%W)]+arr[((y-1+H)%H)*W+((x+1)%W)]+arr[((y+1)%H)*W+((x-1+W)%W)]+arr[((y+1)%H)*W+((x+1)%W)])*0.05;return s;}
  function step(){var nA=A.slice(),nB=B.slice();for(var y=0;y<H;y++)for(var x=0;x<W;x++){var i=y*W+x;var a=A[i],b=B[i];var abb=a*b*b;nA[i]=a+(dA*lap(A,i,x,y)-abb+f*(1-a));nB[i]=b+(dB*lap(B,i,x,y)+abb-(k+f)*b);}A=nA;B=nB;}
  function frame(){for(var n=0;n<8;n++)step();rects.attr('fill',function(i){return color(B[i]);});}
  frame();var iv=setInterval(frame,55);return function(){clearInterval(iv);};}
function dla(host){var svg=newSvg(host);var W=360,H=230,cx=180,cy=115;var stuck=[[cx,cy]];var g=svg.append('g');var color=d3.scaleSequential(d3.interpolateViridis).domain([0,900]);
  g.append('circle').attr('cx',cx).attr('cy',cy).attr('r',2).attr('fill',color(0));var R=10;
  function near(x,y){for(var i=stuck.length-1;i>=0;i--){var dx=stuck[i][0]-x,dy=stuck[i][1]-y;if(dx*dx+dy*dy<16)return true;}return false;}
  function frame(){for(var w=0;w<22;w++){var ang=Math.random()*2*Math.PI;var x=cx+Math.cos(ang)*R,y=cy+Math.sin(ang)*R;
    for(var step=0;step<140;step++){x+=(Math.random()-0.5)*4;y+=(Math.random()-0.5)*4;if(near(x,y)){stuck.push([x,y]);g.append('circle').attr('cx',x).attr('cy',y).attr('r',2).attr('fill',color(stuck.length));var d=Math.sqrt((x-cx)*(x-cx)+(y-cy)*(y-cy));if(d+12>R)R=Math.min(130,d+12);break;}
      if((x-cx)*(x-cx)+(y-cy)*(y-cy)>(R+30)*(R+30))break;}}
    if(stuck.length>900||R>=130)clearInterval(iv);}
  var iv=setInterval(frame,45);return function(){clearInterval(iv);};}
function rule30(host){var svg=newSvg(host);var cols=89,cs=4,rows=57;var row=d3.range(cols).map(function(i){return i===Math.floor(cols/2)?1:0;});var g=svg.append('g');
  for(var r=0;r<rows;r++){(function(r,cur){for(var c=0;c<cols;c++){if(cur[c])g.append('rect').attr('x',c*cs).attr('y',r*cs).attr('width',cs).attr('height',cs).attr('fill',INK);}})(r,row);
    var nxt=row.map(function(_,c){var l=row[(c-1+cols)%cols],m=row[c],rr=row[(c+1)%cols];return (l^(m|rr))?1:0;});row=nxt;}}
function lissajous(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var A=96,B=86;var a=3,b=2;var path=g.append('path').attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',1.6);var dot=g.append('circle').attr('r',4).attr('fill',HILITE);var delta=0;
  function frame(){delta+=0.012;var pts=[];for(var t=0;t<=2*Math.PI;t+=0.02){pts.push([A*Math.sin(a*t+delta),B*Math.sin(b*t)]);}
    path.attr('d','M'+pts.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1);}).join('L'));var h=pts[0];dot.attr('cx',h[0]).attr('cy',h[1]);}
  frame();var iv=setInterval(frame,40);return function(){clearInterval(iv);};}
function metaballs(host){var svg=newSvg(host);var W=72,H=46,cs=5;var balls=d3.range(5).map(function(i){return {x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-0.5)*1.2,vy:(Math.random()-0.5)*1.2,r:6+Math.random()*5,c:i};});
  var values=new Array(W*H);var color=d3.scaleSequential(d3.interpolateViridis).domain([0.4,2.2]);var g=svg.append('g');
  var rects=g.selectAll('rect').data(d3.range(W*H)).join('rect').attr('x',function(i){return (i%W)*cs;}).attr('y',function(i){return Math.floor(i/W)*cs;}).attr('width',cs).attr('height',cs).attr('shape-rendering','crispEdges');
  function frame(){balls.forEach(function(b){b.x+=b.vx;b.y+=b.vy;if(b.x<0||b.x>W)b.vx*=-1;if(b.y<0||b.y>H)b.vy*=-1;});
    for(var y=0;y<H;y++)for(var x=0;x<W;x++){var s=0;balls.forEach(function(b){var dx=x-b.x,dy=y-b.y;s+=b.r*b.r/(dx*dx+dy*dy+1);});values[y*W+x]=s;}
    rects.attr('fill',function(i){var v=values[i];return v<0.8?'#0b1020':color(v);});}
  frame();var iv=setInterval(frame,55);return function(){clearInterval(iv);};}
function lsystem(host){var svg=newSvg(host);var axiom='X';var rules={X:'F+[[X]-X]-F[-FX]+X',F:'FF'};var s=axiom;
  for(var it=0;it<4;it++){var ns='';for(var i=0;i<s.length;i++){ns+=(rules[s[i]]||s[i]);}s=ns;}
  var x=180,y=228,ang=-Math.PI/2,len=5.2,da=25*Math.PI/180;var stack=[];var d='M'+x+','+y;
  for(var k=0;k<s.length;k++){var ch=s[k];
    if(ch==='F'){x+=Math.cos(ang)*len;y+=Math.sin(ang)*len;d+='L'+x.toFixed(1)+','+y.toFixed(1);}
    else if(ch==='+'){ang+=da;}else if(ch==='-'){ang-=da;}
    else if(ch==='['){stack.push([x,y,ang]);}else if(ch===']'){var st=stack.pop();x=st[0];y=st[1];ang=st[2];d+='M'+x.toFixed(1)+','+y.toFixed(1);}}
  svg.append('path').attr('d',d).attr('fill','none').attr('stroke',PAL[1]).attr('stroke-width',0.7).attr('opacity',0.9);}
function waveInterference(host){var svg=newSvg(host);var W=72,H=46,cs=5;var src=[[18,23],[54,23]];var color=d3.scaleSequential(d3.interpolateViridis).domain([-2,2]);var g=svg.append('g');
  var rects=g.selectAll('rect').data(d3.range(W*H)).join('rect').attr('x',function(i){return (i%W)*cs;}).attr('y',function(i){return Math.floor(i/W)*cs;}).attr('width',cs).attr('height',cs).attr('shape-rendering','crispEdges');var t=0;
  function frame(){t+=0.3;rects.attr('fill',function(i){var x=i%W,y=Math.floor(i/W);var s=0;src.forEach(function(p){var d=Math.sqrt((x-p[0])*(x-p[0])+(y-p[1])*(y-p[1]));s+=Math.sin(d*0.6-t);});return color(s);});}
  frame();var iv=setInterval(frame,45);return function(){clearInterval(iv);};}
function sortViz(host){var svg=newSvg(host);var n=42;var arr=d3.shuffle(d3.range(1,n+1));var x=d3.scaleBand().domain(d3.range(n)).range([8,352]).padding(0.12);var y=d3.scaleLinear().domain([0,n]).range([210,12]);
  var bars=svg.selectAll('rect').data(d3.range(n)).join('rect').attr('x',function(i){return x(i);}).attr('width',x.bandwidth()).attr('rx',1);
  var i=0,j=0;function render(hl){bars.attr('y',function(k){return y(arr[k]);}).attr('height',function(k){return 210-y(arr[k]);}).attr('fill',function(k){return (k===hl||k===hl+1)?HILITE:(k>=n-i?PAL[1]:ACCENT);});}
  render(-1);
  function frame(){if(arr[j]>arr[j+1]){var t=arr[j];arr[j]=arr[j+1];arr[j+1]=t;}render(j);j++;if(j>=n-1-i){j=0;i++;if(i>=n-1){clearInterval(iv);bars.attr('fill',PAL[1]);return;}}}
  var iv=setInterval(frame,45);return function(){clearInterval(iv);};}


/* ===== Generative art & simulation (cont.) ===== */
function mandelbrot(host){var svg=newSvg(host);var W=90,H=58,cs=4;var g=svg.append('g');var maxI=60;var color=d3.scaleSequential(d3.interpolateViridis).domain([0,maxI]);
  var cells=[];for(var py=0;py<H;py++)for(var px=0;px<W;px++){var x0=(px/W)*3.2-2.3,y0=(py/H)*2.3-1.15;var x=0,y=0,i=0;
    while(x*x+y*y<=4&&i<maxI){var xt=x*x-y*y+x0;y=2*x*y+y0;x=xt;i++;}cells.push({px:px,py:py,i:i});}
  g.selectAll('rect').data(cells).join('rect').attr('x',function(d){return d.px*cs;}).attr('y',function(d){return d.py*cs;}).attr('width',cs).attr('height',cs).attr('shape-rendering','crispEdges').attr('fill',function(d){return d.i>=maxI?'#05060a':color(d.i);});}
function juliaSet(host){var svg=newSvg(host);var W=72,H=46,cs=5;var g=svg.append('g');var maxI=42;var color=d3.scaleSequential(d3.interpolateViridis).domain([0,maxI]);
  var rects=g.selectAll('rect').data(d3.range(W*H)).join('rect').attr('x',function(i){return (i%W)*cs;}).attr('y',function(i){return Math.floor(i/W)*cs;}).attr('width',cs).attr('height',cs).attr('shape-rendering','crispEdges');var t=0;
  function frame(){t+=0.03;var cre=0.7885*Math.cos(t),cim=0.7885*Math.sin(t);
    rects.attr('fill',function(idx){var px=idx%W,py=Math.floor(idx/W);var x=(px/W)*3.0-1.5,y=(py/H)*2.0-1.0,i=0;
      while(x*x+y*y<=4&&i<maxI){var xt=x*x-y*y+cre;y=2*x*y+cim;x=xt;i++;}return i>=maxI?'#05060a':color(i);});}
  frame();var iv=setInterval(frame,90);return function(){clearInterval(iv);};}
function maurerRose(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var R=100;var line=g.append('path').attr('fill','none').attr('stroke',ACCENT).attr('stroke-width',0.6).attr('opacity',0.85);
  var petal=g.append('path').attr('fill','none').attr('stroke',HILITE).attr('stroke-width',1.4);var n=6,d=71;var walk=0;
  function frame(){walk+=0.4;var dd=71+Math.sin(walk*0.03)*40;var pts=[];for(var th=0;th<=360;th++){var k=th*dd*Math.PI/180;var r=R*Math.sin(n*k);pts.push([r*Math.cos(k),r*Math.sin(k)]);}
    line.attr('d','M'+pts.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1);}).join('L'));
    var pp=[];for(var t2=0;t2<=360;t2++){var kk=t2*Math.PI/180;var rr=R*Math.sin(n*kk);pp.push([rr*Math.cos(kk),rr*Math.sin(kk)]);}
    petal.attr('d','M'+pp.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1);}).join('L'));}
  frame();var iv=setInterval(frame,55);return function(){clearInterval(iv);};}
function spirograph(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var paths=[];var R=92;
  [[5,3,0.62],[7,4,0.5],[11,6,0.4]].forEach(function(cfg,i){var Rr=cfg[0],rr=cfg[1],d=cfg[2];var pts=[];
    for(var t=0;t<=2*Math.PI*rr;t+=0.03){var x=(Rr-rr)*Math.cos(t)+d*rr*Math.cos((Rr-rr)/rr*t);var y=(Rr-rr)*Math.sin(t)-d*rr*Math.sin((Rr-rr)/rr*t);pts.push([x*R/Rr,y*R/Rr]);}
    g.append('path').attr('fill','none').attr('stroke',PAL[i*2%PAL.length]).attr('stroke-width',1).attr('opacity',0.8).attr('d','M'+pts.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1);}).join('L'));});}
function dejong(host){var svg=newSvg(host);var a=-2.0,b=-2.0,c=-1.2,d=2.0;var x=0,y=0;var pts=[];
  for(var i=0;i<3400;i++){var nx=Math.sin(a*y)-Math.cos(b*x);var ny=Math.sin(c*x)-Math.cos(d*y);x=nx;y=ny;pts.push([x,y]);}
  var sx=d3.scaleLinear().domain([-2.2,2.2]).range([20,340]);var sy=d3.scaleLinear().domain([-2.2,2.2]).range([212,14]);
  var B=14,buckets=d3.range(B).map(function(){return [];});
  pts.forEach(function(p,i){buckets[Math.min(B-1,Math.floor(i/pts.length*B))].push('M'+sx(p[0]).toFixed(1)+','+sy(p[1]).toFixed(1)+'h0.7');});
  var color=d3.scaleSequential(d3.interpolateViridis).domain([0,B-1]);
  buckets.forEach(function(seg,bi){svg.append('path').attr('d',seg.join('')).attr('stroke',color(bi)).attr('stroke-width',0.8).attr('stroke-linecap','round').attr('opacity',0.7);});}
function truchet(host){var svg=newSvg(host);var cs=24,cols=15,rows=10,ox=0,oy=0;var g=svg.append('g');
  for(var r=0;r<rows;r++)for(var c=0;c<cols;c++){var x=c*cs,y=r*cs;var t=Math.random()<0.5;var col=PAL[(r+c)%PAL.length];
    g.append('rect').attr('x',x).attr('y',y).attr('width',cs).attr('height',cs).attr('fill','none');
    if(t){g.append('path').attr('d','M'+x+','+(y+cs/2)+'A'+(cs/2)+','+(cs/2)+' 0 0 1 '+(x+cs/2)+','+y).attr('fill','none').attr('stroke',col).attr('stroke-width',2);
      g.append('path').attr('d','M'+(x+cs/2)+','+(y+cs)+'A'+(cs/2)+','+(cs/2)+' 0 0 1 '+(x+cs)+','+(y+cs/2)).attr('fill','none').attr('stroke',col).attr('stroke-width',2);}
    else{g.append('path').attr('d','M'+(x+cs/2)+','+y+'A'+(cs/2)+','+(cs/2)+' 0 0 1 '+(x+cs)+','+(y+cs/2)).attr('fill','none').attr('stroke',col).attr('stroke-width',2);
      g.append('path').attr('d','M'+x+','+(y+cs/2)+'A'+(cs/2)+','+(cs/2)+' 0 0 0 '+(x+cs/2)+','+(y+cs)).attr('fill','none').attr('stroke',col).attr('stroke-width',2);}}}
function langtonAnt(host){var svg=newSvg(host);var cols=45,rows=29,cs=8;var grid=new Array(cols*rows).fill(0);var ax=22,ay=14,dir=0;var g=svg.append('g');
  var rects=g.selectAll('rect').data(d3.range(cols*rows)).join('rect').attr('x',function(i){return (i%cols)*cs;}).attr('y',function(i){return Math.floor(i/cols)*cs;}).attr('width',cs-0.5).attr('height',cs-0.5).attr('fill','#fff');
  var ant=g.append('rect').attr('width',cs).attr('height',cs).attr('fill',HILITE);var dx=[0,1,0,-1],dy=[-1,0,1,0];
  function frame(){for(var s=0;s<6;s++){var i=ay*cols+ax;if(grid[i]===0){dir=(dir+1)%4;grid[i]=1;}else{dir=(dir+3)%4;grid[i]=0;}
    ax=(ax+dx[dir]+cols)%cols;ay=(ay+dy[dir]+rows)%rows;}
    rects.attr('fill',function(d){return grid[d]?INK:'#fff';});ant.attr('x',ax*cs).attr('y',ay*cs);}
  frame();var iv=setInterval(frame,55);return function(){clearInterval(iv);};}
function nbody(host){var svg=newSvg(host);var W=360,H=230;var bodies=d3.range(7).map(function(i){var a=i/7*2*Math.PI,r=60;return {x:180+Math.cos(a)*r,y:115+Math.sin(a)*r,vx:Math.sin(a)*0.6,vy:-Math.cos(a)*0.6,m:3+Math.random()*4,c:PAL[i%PAL.length],tr:[]};});
  var g=svg.append('g');var tG=svg.append('g');
  function frame(){for(var k=0;k<2;k++){bodies.forEach(function(bi){var fx=0,fy=0;bodies.forEach(function(bj){if(bi===bj)return;var dx=bj.x-bi.x,dy=bj.y-bi.y,d2=dx*dx+dy*dy+40;var f=bj.m/d2;var d=Math.sqrt(d2);fx+=f*dx/d;fy+=f*dy/d;});bi.vx+=fx*0.6;bi.vy+=fy*0.6;});
    bodies.forEach(function(b){b.x+=b.vx;b.y+=b.vy;if(b.x<0||b.x>W)b.vx*=-0.8;if(b.y<0||b.y>H)b.vy*=-0.8;b.x=Math.max(0,Math.min(W,b.x));b.y=Math.max(0,Math.min(H,b.y));b.tr.unshift([b.x,b.y]);if(b.tr.length>22)b.tr.pop();});}
    var tp=tG.selectAll('path').data(bodies);tp.enter().append('path').merge(tp).attr('fill','none').attr('stroke',function(b){return b.c;}).attr('stroke-width',1).attr('opacity',0.4).attr('d',function(b){return 'M'+b.tr.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1);}).join('L');});
    var c=g.selectAll('circle').data(bodies);c.enter().append('circle').merge(c).attr('cx',function(b){return b.x;}).attr('cy',function(b){return b.y;}).attr('r',function(b){return b.m*0.9;}).attr('fill',function(b){return b.c;});}
  frame();var iv=setInterval(frame,33);return function(){clearInterval(iv);};}


/* ===== Generative art & simulation (cont.) ===== */
function barnsleyFern(host){var svg=newSvg(host);var x=0,y=0;var pts=[];
  for(var i=0;i<5000;i++){var r=Math.random(),nx,ny;
    if(r<0.01){nx=0;ny=0.16*y;}else if(r<0.86){nx=0.85*x+0.04*y;ny=-0.04*x+0.85*y+1.6;}
    else if(r<0.93){nx=0.2*x-0.26*y;ny=0.23*x+0.22*y+1.6;}else{nx=-0.15*x+0.28*y;ny=0.26*x+0.24*y+0.44;}
    x=nx;y=ny;pts.push([x,y]);}
  var sx=d3.scaleLinear().domain([-2.8,2.8]).range([70,290]);var sy=d3.scaleLinear().domain([0,10]).range([226,6]);
  var d=pts.map(function(p){var px=sx(p[0]).toFixed(1),py=sy(p[1]).toFixed(1);return 'M'+px+','+py+'h0.8';}).join('');
  svg.append('path').attr('d',d).attr('stroke',PAL[2]).attr('stroke-width',0.9).attr('stroke-linecap','round').attr('opacity',0.8);}
function wireframeCube(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');
  var V=[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]];
  var E=[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];
  var lines=g.selectAll('line').data(E).join('line').attr('stroke',ACCENT).attr('stroke-width',1.4);
  var dots=g.selectAll('circle').data(V).join('circle').attr('r',2.5).attr('fill',HILITE);var t=0;
  function frame(){t+=0.02;var ca=Math.cos(t),sa=Math.sin(t),cb=Math.cos(t*0.7),sb=Math.sin(t*0.7);var sc=70;
    var P=V.map(function(v){var x=v[0]*ca-v[2]*sa,z=v[0]*sa+v[2]*ca;var y=v[1]*cb-z*sb;z=v[1]*sb+z*cb;var f=2.4/(z+3.2);return [x*sc*f,y*sc*f];});
    lines.attr('x1',function(e){return P[e[0]][0];}).attr('y1',function(e){return P[e[0]][1];}).attr('x2',function(e){return P[e[1]][0];}).attr('y2',function(e){return P[e[1]][1];});
    dots.attr('cx',function(_,i){return P[i][0];}).attr('cy',function(_,i){return P[i][1];});}
  frame();var iv=setInterval(frame,33);return function(){clearInterval(iv);};}
function perlinTerrain(host){var svg=newSvg(host);var W=72,H=46,cs=5;var g=svg.append('g');var color=d3.scaleSequential(d3.interpolateViridis).domain([-1.4,1.4]);
  var perm=d3.shuffle(d3.range(256));perm=perm.concat(perm);
  function fade(t){return t*t*t*(t*(t*6-15)+10);}function lerp(a,b,t){return a+t*(b-a);}
  function grad(h,x,y){var u=(h&1)?-x:x,v=(h&2)?-y:y;return u+v;}
  function noise(x,y){var X=Math.floor(x)&255,Y=Math.floor(y)&255;x-=Math.floor(x);y-=Math.floor(y);var u=fade(x),v=fade(y);
    var aa=perm[perm[X]+Y],ab=perm[perm[X]+Y+1],ba=perm[perm[X+1]+Y],bb=perm[perm[X+1]+Y+1];
    return lerp(lerp(grad(aa,x,y),grad(ba,x-1,y),u),lerp(grad(ab,x,y-1),grad(bb,x-1,y-1),u),v);}
  var rects=g.selectAll('rect').data(d3.range(W*H)).join('rect').attr('x',function(i){return (i%W)*cs;}).attr('y',function(i){return Math.floor(i/W)*cs;}).attr('width',cs).attr('height',cs).attr('shape-rendering','crispEdges');var t=0;
  function frame(){t+=0.04;rects.attr('fill',function(i){var x=i%W,y=Math.floor(i/W);var n=noise(x*0.08+t,y*0.08)+0.5*noise(x*0.16,y*0.16+t);return color(n);});}
  frame();var iv=setInterval(frame,70);return function(){clearInterval(iv);};}
function starfield(host){var svg=newSvg(host);var W=360,H=230,cx=180,cy=115;var N=160;var stars=d3.range(N).map(function(){return {x:(Math.random()-0.5)*W,y:(Math.random()-0.5)*H,z:Math.random()*W};});
  var g=svg.append('g');var sel=g.selectAll('line').data(stars).join('line').attr('stroke','#fff').attr('stroke-linecap','round');svg.insert('rect',':first-child').attr('width',W).attr('height',H).attr('fill','#05060a');
  function frame(){sel.each(function(d){d.z-=6;if(d.z<1){d.x=(Math.random()-0.5)*W;d.y=(Math.random()-0.5)*H;d.z=W;}});
    sel.attr('x1',function(d){return cx+d.x/d.z*W*0.9;}).attr('y1',function(d){return cy+d.y/d.z*W*0.9;}).attr('x2',function(d){var z2=d.z+6;return cx+d.x/z2*W*0.9;}).attr('y2',function(d){var z2=d.z+6;return cy+d.y/z2*W*0.9;}).attr('stroke-width',function(d){return (1-d.z/W)*2.2;}).attr('opacity',function(d){return 1-d.z/W;});}
  frame();var iv=setInterval(frame,33);return function(){clearInterval(iv);};}
function matrixRain(host){var svg=newSvg(host);var W=360,H=230,cols=40,fs=11;var cw=W/cols;var drops=d3.range(cols).map(function(){return Math.floor(Math.random()*-30);});
  svg.append('rect').attr('width',W).attr('height',H).attr('fill','#05080a');var g=svg.append('g').attr('font-family','monospace').attr('font-size',fs);
  var glyphs='01<>|/\\=+*#'.split('');
  function frame(){g.selectAll('text').remove();for(var c=0;c<cols;c++){for(var k=0;k<16;k++){var row=drops[c]-k;if(row<0||row*fs>H)continue;
    g.append('text').attr('x',c*cw+2).attr('y',row*fs).attr('fill',k===0?'#d6ffe0':'#2ecc71').attr('opacity',Math.max(0,1-k/16)).text(glyphs[Math.floor(Math.random()*glyphs.length)]);}
    drops[c]++;if(drops[c]*fs>H+200)drops[c]=Math.floor(Math.random()*-20);}}
  frame();var iv=setInterval(frame,70);return function(){clearInterval(iv);};}
function rule110(host){var svg=newSvg(host);var cols=89,cs=4,rows=57;var row=d3.range(cols).map(function(i){return i===cols-2?1:0;});var g=svg.append('g');var color=d3.scaleSequential(d3.interpolateViridis).domain([0,rows]);
  for(var r=0;r<rows;r++){(function(r,cur){for(var c=0;c<cols;c++){if(cur[c])g.append('rect').attr('x',c*cs).attr('y',r*cs).attr('width',cs).attr('height',cs).attr('fill',color(r));}})(r,row);
    var nxt=row.map(function(_,c){var l=row[(c-1+cols)%cols],m=row[c],rr=row[(c+1)%cols];var p=(l<<2)|(m<<1)|rr;return (110>>p)&1;});row=nxt;}}
function hilbert(host){var svg=newSvg(host);var order=5,n=1<<order;var N=n*n;var pts=[];
  function d2xy(d){var rx,ry,t=d,x=0,y=0;for(var s=1;s<n;s*=2){rx=1&(t/2);ry=1&(t^rx);if(ry===0){if(rx===1){x=s-1-x;y=s-1-y;}var tmp=x;x=y;y=tmp;}x+=s*rx;y+=s*ry;t=Math.floor(t/4);}return [x,y];}
  for(var d=0;d<N;d++)pts.push(d2xy(d));var sc=210/(n-1),ox=75,oy=10;var color=d3.scaleSequential(d3.interpolateViridis).domain([0,N]);
  for(var i=0;i<pts.length-1;i++){svg.append('line').attr('x1',ox+pts[i][0]*sc).attr('y1',oy+pts[i][1]*sc).attr('x2',ox+pts[i+1][0]*sc).attr('y2',oy+pts[i+1][1]*sc).attr('stroke',color(i)).attr('stroke-width',1.6);}}
function phylloBloom(host){var svg=newSvg(host);var g=svg.append('g').attr('transform','translate(180,115)');var N=380;var gold=Math.PI*(3-Math.sqrt(5));var color=d3.scaleSequential(d3.interpolateViridis).domain([0,N]);
  var dots=g.selectAll('circle').data(d3.range(N)).join('circle').attr('r',0).attr('fill',function(i){return color(i);});var t=0;
  function frame(){t+=0.015;dots.attr('cx',function(i){var a=i*gold+t;var r=5.5*Math.sqrt(i);return Math.cos(a)*r;}).attr('cy',function(i){var a=i*gold+t;var r=5.5*Math.sqrt(i);return Math.sin(a)*r;}).attr('r',function(i){return 1.6+i/N*2.4;});}
  frame();var iv=setInterval(frame,45);return function(){clearInterval(iv);};}

var SECTIONS=[
  ['Distribution',[['Histogram',drawHistogram],['Density (KDE)',drawDensity],['Boxplot',drawBox],['Violin',drawViolin],['Ridgeline',drawRidgeline],['Beeswarm',drawBeeswarm],['Mirrored beeswarm',mirrorBeeswarm],['Dot / strip plot',dotplot],['Population pyramid',pyramid]]],
  ['Correlation',[['Scatter',drawScatter],['Bubble',drawBubble],['Connected scatter',drawConnScatter],['Scatterplot matrix',splom],['Heatmap',drawHeatmap],['Viridis heatmap',drawViridis],['Contour density',drawContour],['Voronoi',drawVoronoi],['Voronoi stippling',stippling],['Hexbin density',hexbin],['Closest point on path',closestPoint],['Hertzsprung–Russell',hertzsprung],['Volcano contours',volcanoContours],['Q–Q plot',qqPlot],['Marginal histogram',marginalHist],['Trend / regression',regScatter],['Ternary plot',ternary]]],
  ['Ranking',[['Barplot',drawBars],['Horizontal bar',drawHBar],['Lollipop',drawLollipop],['Circular barplot',drawCircBar],['Radar / spider',drawRadar],['Parallel coordinates',drawParallel],['Diverging stacked bar',divergingBar],['Bullet charts',bullet],['Sortable bar (auto)',sortableBar],['Word cloud',wordcloud],['Spike chart',spikeChart]]],
  ['Part of a whole',[['Pie',drawPie],['Donut',drawDonut],['Nested donut',nestedDonut],['Treemap',drawTreemap],['Circular packing',drawPack],['Bubble chart (labeled)',bubbleChart],['Waffle chart',waffle],['Funnel',funnel],['Marimekko',drawMarimekko],['Waterfall',waterfall],['Pie chart update',pieUpdate],['Nightingale rose',roseChart],['Phases of the moon',phasesMoon]]],
  ['Grouped & stacked bars',[['Stacked bar',drawStackBar],['Grouped bar chart',groupedBar],['Horizontal grouped bar',hgroup],['Stacked ↔ grouped bars',stackGroup],['100% stacked bar',pct100],['100% stacked area',normStackArea],['Dual-axis combo',dualAxis]]],
  ['Evolution (time series)',[['Line (draw)',drawLine],['Multi-line',drawMultiLine],['Multi-line + Voronoi (hover)',multiLineVoronoi],['Area',drawArea],['Gradient area',gradArea],['Step line',stepline],['Stacked area',drawStackArea],['Streamgraph',drawStream],['Streamgraph (hover)',streamHover],['Horizon chart',horizon],['Difference chart',differenceChart],['Candlestick / OHLC',drawCandle],['Line transition (live)',lineTransition],['Zoomable area (scroll/drag)',zoomableArea],['Bump chart',bump],['Slope chart',slope],['Index chart (hover)',indexChart],['Band chart',bandChart],['Threshold-color line',thresholdLine],['Line with gaps',gapsLine],['Moving average',movingAvg]]],
  ['Hierarchy',[['Dendrogram',drawDendro],['Radial tidy tree',drawRadialTree],['Phylogenetic tree',phyloTree],['Tangled tree',tangledTree],['Sunburst',drawSunburst],['Zoomable sunburst',drawZoomSun],['Sunburst + breadcrumb (hover)',sunburstBread],['Zoomable icicle',drawIcicle],['Collapsible tree',drawTree],['Collapsible indented tree',indentedTree],['Hierarchical bar (drill-down)',hierBar],['Zoomable circle packing',circlePack],['Zoomable treemap',zoomTreemap]]],
  ['Flow & network',[['Chord',drawChord],['Directed chord',chordDirected],['Sankey flow',sankey],['Arc diagram',drawArc],['Edge bundling (hover)',drawBundle],['Adjacency matrix (hover)',matrix],['Draggable force',drawDragForce],['Collision detection (hover)',collision],['Multi-foci force layout',multiFoci],['Mobile patent suits (force+arrows)',patentSuits],['Interactive graph editor',graphEditor],['Disjoint force graph',disjointForce],['Alluvial / parallel sets',alluvial]]],
  ['Gauges & radial',[['Radial gauges',drawGauges],['Needle gauges (live)',needleGauges],['Liquid fill gauge',liquidGauge],['Polar clock (live)',polarClock],['Radial line',radialLine],['Radial stacked bar',radialStack],['Stacked radial area',stackedRadialArea],['Spiral circle',spiralCircle],['Seasonal radial',seasonalRadial]]],
  ['Time & calendar',[['Calendar heatmap',calendar],['Gantt timeline',gantt],['Punch card',punchcard],['Marey’s trains (schedule)',mareyTrains],['Barcode timeline',barcode],['Vertical calendar',vCalendar]]],
  ['Interaction',[['Tooltip (pointer)',drawTooltip],['Nearest-point (Delaunay)',drawNearest],['Zoom & pan scatter',drawZoomScatter],['Quadtree (hover)',quadtreeViz],['Brush handles',brushHandles]]],
  ['Animation & algorithms',[['General update pattern',drawGUP],['Elastic bars',drawElastic],['Shape tweening',shapeTween],['Bar chart race',drawBarRace],['Wave motion',waveMotion],['Phyllotaxis',phyllotaxis],['Maze generator (backtracker)',mazeGen],['Quicksort (animated)',quickSort],['Poisson-disc sampling',poisson],['Lorenz attractor',lorenz],['Predator & prey (phase)',predatorPrey],['Tadpoles (live)',tadpoles],['Epicyclic gearing',gears],['Connected particles',particles],['OMG particles! (live)',omgParticles],['Wealth & health of nations',wealthHealth],['Scatterplot tour',scatterTour],['Scatter with shapes',shapeScatter]]],
  ['Scales, color & text',[['Every ColorBrewer scale',colorBrewer],['Automatic text sizing',autoText],['Wrapping long labels',wrapLabels],['Gradient-along-stroke',gradientStroke]]],
  ['Generative art & simulation',[['Fourier epicycles',fourierEpicycles],['Double pendulum',doublePendulum],['Fractal tree',fractalTree],['Flow field',flowField],['Clifford attractor',cliffordAttractor],['Chaos game (Sierpinski)',chaosGame],['Boids flocking',boids],["Conway’s Game of Life",gameOfLife],['Reaction-diffusion (Turing)',reactionDiffusion],['Dendrite growth (DLA)',dla],['Rule 30 automaton',rule30],['Lissajous curves',lissajous],['Metaballs',metaballs],['L-system plant',lsystem],['Wave interference',waveInterference],['Sorting visualizer',sortViz],['Mandelbrot set',mandelbrot],['Julia set (animated)',juliaSet],['Maurer rose',maurerRose],['Spirograph',spirograph],['De Jong attractor',dejong],['Truchet tiles',truchet],["Langton’s ant",langtonAnt],['N-body orbits',nbody],['Barnsley fern (IFS)',barnsleyFern],['Rotating wireframe cube',wireframeCube],['Perlin terrain',perlinTerrain],['Starfield warp',starfield],['Matrix rain',matrixRain],['Rule 110 automaton',rule110],['Hilbert curve',hilbert],['Phyllotaxis bloom',phylloBloom]]]
];
function Tile(props){var ref=R.useRef(null);
  R.useEffect(function(){var host=ref.current;if(!host)return;host.innerHTML='';var cleanup;try{cleanup=props.draw(host);}catch(e){host.innerHTML='<div style="color:#B00020;font:11px ui-monospace,monospace;padding:8px">'+String((e&&e.message)||e)+'</div>';}return function(){try{if(cleanup)cleanup();}catch(_){}try{d3.select(host).selectAll('*').remove();}catch(_){}};},[]);
  return R.createElement('div',{style:{background:CARD,border:'1px solid '+GRIDC,borderRadius:12,padding:14,display:'flex',flexDirection:'column'}},
    R.createElement('div',{style:{fontFamily:FONT,fontWeight:700,fontSize:13,marginBottom:8,color:INK}},props.title),
    R.createElement('div',{ref:ref,style:{flex:1,minHeight:230}}));}
function App(props){var count=0;SECTIONS.forEach(function(s){count+=s[1].length;});
  return R.createElement('div',{style:{padding:26,fontFamily:FONT,background:CANVAS,color:INK}},
    R.createElement('div',{style:{borderLeft:'6px solid '+ACCENT,paddingLeft:14,marginBottom:4}},
      R.createElement('h1',{style:{margin:0,fontSize:24,letterSpacing:'-0.3px'}},'The Du Bois D3 Gallery'),
      R.createElement('p',{style:{margin:'4px 0 0',color:INK2,fontSize:13}}, count+' visualizations in one custom page — Du Bois design-system palette, core d3 only (sandbox allowlist = d3@7).')),
    R.createElement('div',{style:{height:18}}),
    SECTIONS.map(function(sec,si){return R.createElement('div',{key:si,style:{marginBottom:28}},
      R.createElement('h2',{style:{margin:'0 0 12px',fontSize:15,color:ACCENT,borderBottom:'2px solid '+GRIDC,paddingBottom:5}},sec[0]),
      R.createElement('div',{style:{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(300px,1fr))',gap:16}},
        sec[1].map(function(t,i){return R.createElement(Tile,{key:i,title:t[0],draw:t[1]});})));}));}
module.exports.default=App;
"""

def main():
    ap = argparse.ArgumentParser(description="Deploy the Du Bois D3 Custom-Page Gallery.")
    ap.add_argument("--profile", required=True, help="Databricks CLI profile")
    ap.add_argument("--warehouse", required=True, help="SQL warehouse id")
    ap.add_argument("--parent-path", default=None, help="Workspace folder (default: your home)")
    ap.add_argument("--name", default="Du Bois Custom-Viz Gallery III — D3 Interactive Custom Page (178 Tiles)", help="Dashboard display name")
    a = ap.parse_args()
    did, url = deploy(a.name, [{"name": "dubois", "displayName": "Du Bois D3 Gallery",
                                "widgets": [custom_page_widget("w_dubois", CODE, w=12, h=120)]}],
                      a.profile, a.warehouse, a.parent_path, publish=True, theme=DUBOIS_THEME)
    print("DASHBOARD_ID", did)
    print("PUBLISHED_URL", url)


if __name__ == "__main__":
    main()
