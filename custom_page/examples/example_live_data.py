#!/usr/bin/env python3
"""EXAMPLE: D3 bound to LIVE Unity Catalog data (not synthetic).

The main gallery (build_custom_page.py) draws 178 tiles from synthetic data to showcase
D3 technique. THIS example shows the capability that makes a custom page more than a pretty
demo: rendering D3 — and a native KPI — from live, governed SQL queries against Unity Catalog.

It binds two datasets over `samples.bakehouse.sales_transactions` and renders:
  • viz.Value         -> a KPI bound to SUM(totalPrice)
  • viz.CustomWidget  -> a D3 bar chart drawn from "revenue by product" query rows

Verified rendering (Oct 2026): KPI = 66,471; bars labeled with the real
top products (Golden Gate Ginger, Outback Oatmeal, ...).

KEY GOTCHA (learned the hard way): viz.CustomWidget REQUIRES a `schema` prop. Omit it and the
whole page crashes with "Custom Page sandbox failed to render. render: Cannot convert
undefined or null to object". viz.Value needs no schema. Rows arrive at render(config,data)
as data.main.rows (array-of-arrays, column order).

Usage:
  python3 example_live_data.py --profile <cli-profile> --warehouse <id> [--parent-path /Users/you]

Requires the workspace preview "Custom pages in AI/BI dashboards" to be enabled, and read
access to samples.bakehouse (the built-in Databricks samples catalog).
"""
import argparse, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from deploy_custom_page import custom_page_widget, deploy

CODE = r"""/** @custom-page-source jsx */
var R=require('react'); var viz=require('@databricks/viz'); var d3=require('d3');
var PAL=['#2463EB','#2EB88A','#AB47BD','#F69E23','#DD2C4D','#1BA3BB'];
var INK='#11171C', INK2='#5F7281', GRIDC='#E8ECF0', FONT='DM Sans, Inter, system-ui, sans-serif';

// D3 bar chart drawn from the live query rows handed to render(config,data).
function BarsFromData(props){
  var ref=R.useRef(null);
  var main=(props.data&&props.data.main)?props.data.main:{};
  var rows=main.rows||[];
  R.useEffect(function(){
    var host=ref.current; if(!host) return; host.innerHTML='';
    if(!rows.length){host.innerHTML='<div style="color:#5F7281;font:12px '+FONT+';padding:12px">waiting for rows…</div>';return;}
    var data=rows.map(function(r){return {product:String(r[0]), rev:Number(r[1])};})
                 .filter(function(x){return !isNaN(x.rev);}).slice(0,12);
    var W=680,H=330,m={t:14,r:18,b:98,l:66};
    var svg=d3.select(host).append('svg').attr('width','100%').attr('viewBox','0 0 '+W+' '+H);
    var x=d3.scaleBand().domain(data.map(function(d){return d.product;})).range([m.l,W-m.r]).padding(0.18);
    var y=d3.scaleLinear().domain([0,d3.max(data,function(d){return d.rev;})]).nice().range([H-m.b,m.t]);
    svg.append('g').attr('transform','translate(0,'+(H-m.b)+')').call(d3.axisBottom(x))
      .selectAll('text').attr('transform','rotate(-40)').style('text-anchor','end').attr('fill',INK2).attr('font-size',10).attr('font-family',FONT);
    svg.append('g').attr('transform','translate('+m.l+',0)').call(d3.axisLeft(y).ticks(5).tickFormat(d3.format('~s')))
      .selectAll('text').attr('fill',INK2).attr('font-family',FONT);
    svg.selectAll('rect.bar').data(data).join('rect').attr('class','bar')
      .attr('x',function(d){return x(d.product);}).attr('width',x.bandwidth())
      .attr('y',H-m.b).attr('height',0).attr('rx',3).attr('fill',function(_,i){return PAL[i%PAL.length];})
      .transition().duration(800).delay(function(_,i){return i*45;})
      .attr('y',function(d){return y(d.rev);}).attr('height',function(d){return (H-m.b)-y(d.rev);});
  },[JSON.stringify(rows)]);
  return R.createElement('div',{ref:ref,style:{width:'100%'}});
}

function App(props){
  var card={background:'#fff',border:'1px solid '+GRIDC,borderRadius:12,padding:16,marginBottom:16};
  return R.createElement('div',{style:{padding:24,fontFamily:FONT,background:'#F5F7FA',color:INK}},
    R.createElement('div',{style:{borderLeft:'6px solid #2272B4',paddingLeft:14,marginBottom:16}},
      R.createElement('h1',{style:{margin:0,fontSize:22}},'D3 bound to LIVE Unity Catalog data'),
      R.createElement('p',{style:{margin:'4px 0 0',color:INK2,fontSize:13}},'viz.Value KPI + viz.CustomWidget\u2192D3 bars, both from samples.bakehouse.sales_transactions.')),
    R.createElement('div',{style:{display:'grid',gridTemplateColumns:'1fr 2fr',gap:16}},
      // ---- native KPI from a live aggregate (no schema needed) ----
      R.createElement('div',{style:card},
        R.createElement('div',{style:{fontWeight:700,fontSize:13,marginBottom:8}},'Total revenue (viz.Value)'),
        R.createElement(viz.Value,{widgetId:'kpi_rev',
          queries:[{queryName:'main',query:{datasetName:'kpi',
            fields:[{fieldName:'total_rev',expression:'`total_rev`'}],disaggregatedData:true}}]})),
      // ---- D3 drawn from live query rows (schema prop is MANDATORY) ----
      R.createElement('div',{style:card},
        R.createElement('div',{style:{fontWeight:700,fontSize:13,marginBottom:8}},'Revenue by product (D3 from live query)'),
        R.createElement(viz.CustomWidget,{widgetId:'bars_rev',
          schema:{fields:[{name:'product',type:'string'},{name:'revenue',type:'number'}]},
          queries:[{queryName:'main',query:{datasetName:'products',
            fields:[{fieldName:'product',expression:'`product`'},
                    {fieldName:'revenue',expression:'`revenue`'}],
            disaggregatedData:true}}],
          render:function(config,data){return R.createElement(BarsFromData,{data:data});}}))));
}
module.exports.default=App;
"""

DATASETS = [
    {"name": "ds_products", "displayName": "Revenue by product",
     "queryLines": ["SELECT product, ROUND(SUM(totalPrice)) AS revenue "
                    "FROM samples.bakehouse.sales_transactions GROUP BY product ORDER BY revenue DESC"]},
    {"name": "ds_kpi", "displayName": "Total revenue",
     "queryLines": ["SELECT ROUND(SUM(totalPrice)) AS total_rev, COUNT(*) AS txns "
                    "FROM samples.bakehouse.sales_transactions"]},
]
DATASET_MAP = [{"alias": "products", "datasetId": "ds_products"},
               {"alias": "kpi", "datasetId": "ds_kpi"}]


def main():
    ap = argparse.ArgumentParser(description="Deploy the live-data custom-page example.")
    ap.add_argument("--profile", required=True)
    ap.add_argument("--warehouse", required=True)
    ap.add_argument("--parent-path", default=None)
    ap.add_argument("--name", default="D3 Live-Data Example (bakehouse)")
    a = ap.parse_args()

    # syntax-check the embedded JS first (one syntax error blanks the whole page)
    open("/tmp/_cp_example.js", "w").write(CODE)
    chk = subprocess.run(["node", "--check", "/tmp/_cp_example.js"], capture_output=True, text=True)
    if chk.returncode != 0:
        raise SystemExit("JS syntax error:\n" + chk.stderr)

    did, url = deploy(a.name,
                      [{"name": "live", "displayName": "Live Data",
                        "widgets": [custom_page_widget("w_live", CODE, DATASET_MAP, w=12, h=30)]}],
                      a.profile, a.warehouse, a.parent_path, publish=True, datasets=DATASETS)
    print("DASHBOARD_ID", did)
    print("PUBLISHED_URL", url)


if __name__ == "__main__":
    main()
