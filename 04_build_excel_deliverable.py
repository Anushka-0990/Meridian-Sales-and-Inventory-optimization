"""
ENGAGEMENT: Meridian Retail Corp - Sales & Inventory Optimization
Deliverable 04: Client-ready Excel workbook (.xlsx)
Combines SQL results + model outputs into a formatted, charted workbook
the way an analyst packages a client data pack (python + openpyxl).
"""
import sqlite3, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, PieChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList

DB = "warehouse.db"
OUT = "retail_analytics_deliverable.xlsx"
conn = sqlite3.connect(DB)

# ---------- palette ----------
NAVY   = "1F3864"; BLUE="0B5FA5"; ORANGE="E07B00"
LIGHT  = "DDEBF7"; WHITE="FFFFFF"; GREY="F2F2F2"
BOLD = Font(bold=True, color="FFFFFF")
HDR  = Font(bold=True, color=WHITE, size=11)
title_f = Font(bold=True, size=16, color=NAVY)
sub_f   = Font(size=10, italic=True, color="595959")
thin = Side(style="thin", color="BFBFBF")
border = Border(left=thin,right=thin,top=thin,bottom=thin)

def style_header(ws, row, ncols, fill=NAVY):
    for c in range(1, ncols+1):
        cell = ws.cell(row=row, column=c)
        cell.font = HDR
        cell.fill = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border

def autofit(ws, widths):
    for i,w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

wb = Workbook()

# =========================================================
# SHEET 1 : EXECUTIVE SUMMARY
# =========================================================
ws = wb.active; ws.title = "Executive Summary"
ws.merge_cells("A1:H1"); ws["A1"]="MERIDIAN RETAIL CORP  |  Sales & Inventory Optimization"
ws["A1"].font=title_f
ws.merge_cells("A2:H2"); ws["A2"]="Analytics engagement - Data-backed retail decisions  |  Prepared for management review"
ws["A2"].font=sub_f

# load KPI
q1 = pd.read_sql_query("""SELECT COUNT(DISTINCT order_id) o, ROUND(SUM(sales),0) rev,
 ROUND(SUM(profit),0) profit, ROUND(SUM(profit)/SUM(sales)*100,1) m,
 ROUND(100.0*SUM(is_return)/COUNT(*),1) rr FROM fact_orders""", conn)
rev, prof, mar, rr = q1.iloc[0].rev, q1.iloc[0].profit, q1.iloc[0].m, q1.iloc[0].rr

row = 4
ws.cell(row=row,column=1,value="Revenue (USD)").font=Font(bold=True,color=NAVY)
ws.cell(row=row,column=2,value=f"$ {rev:,.0f}").font=BOLD
ws.cell(row=row,column=1).fill=PatternFill("solid",fgColor=LIGHT)
ws.cell(row=row,column=2).fill=PatternFill("solid",fgColor=LIGHT)
ws.cell(row=row,column=1).border=border; ws.cell(row=row,column=2).border=border
ws.cell(row=row+1,column=1,value="Gross Profit (USD)").font=Font(bold=True,color=NAVY)
ws.cell(row=row+1,column=2,value=f"$ {prof:,.0f}").font=BOLD
ws.cell(row=row+1,column=1).fill=PatternFill("solid",fgColor=LIGHT)
ws.cell(row=row+1,column=2).fill=PatternFill("solid",fgColor=LIGHT)
ws.cell(row=row+1,column=1).border=border; ws.cell(row=row+1,column=2).border=border
ws.cell(row=row+2,column=1,value="Net Margin %").font=Font(bold=True,color=NAVY)
ws.cell(row=row+2,column=2,value=f"{mar}%").font=BOLD
ws.cell(row=row+2,column=1).fill=PatternFill("solid",fgColor=LIGHT)
ws.cell(row=row+2,column=2).fill=PatternFill("solid",fgColor=LIGHT)
ws.cell(row=row+2,column=1).border=border; ws.cell(row=row+2,column=2).border=border
ws.cell(row=row+3,column=1,value="Line-item Return Rate %").font=Font(bold=True,color=NAVY)
ws.cell(row=row+3,column=2,value=f"{rr}%").font=BOLD
ws.cell(row=row+3,column=1).fill=PatternFill("solid",fgColor=LIGHT)
ws.cell(row=row+3,column=2).fill=PatternFill("solid",fgColor=LIGHT)
ws.cell(row=row+3,column=1).border=border; ws.cell(row=row+3,column=2).border=border

# Regional table + chart  (Q2)
reg = pd.read_sql_query("""SELECT region r, ROUND(SUM(sales),0) rev,
  ROUND(SUM(profit),0) prof, ROUND(SUM(profit)/SUM(sales)*100,1) m,
  ROUND(100.0*SUM(is_return)/COUNT(*),1) rr FROM fact_orders GROUP BY 1 ORDER BY prof DESC""", conn)
trow = 12
ws.cell(row=trow,column=1,value="Regional P&L").font=Font(bold=True,size=13,color=NAVY)
ws.cell(row=trow+1,column=1,value="Region"); ws.cell(row=trow+1,column=2,value="Revenue")
ws.cell(row=trow+1,column=3,value="Profit"); ws.cell(row=trow+1,column=4,value="Margin%")
ws.cell(row=trow+1,column=5,value="Return%")
style_header(ws, trow+1, 5, BLUE)
for i,r in reg.iterrows():
    rr_ = trow+2+i
    vals=[r.r, r.rev, r.prof, r.m, r.rr]
    for j,v in enumerate(vals,start=1):
        c=ws.cell(row=rr_,column=j,value=v); c.border=border
    ws.cell(row=rr_,column=2).number_format='#,##0'
    ws.cell(row=rr_,column=3).number_format='#,##0'
last=trow+1+len(reg)
# bar chart profit by region
ch1 = BarChart(); ch1.type="bar"; ch1.style=10; ch1.title="Regional Profit (USD)"
data=Reference(ws, min_col=3, min_row=trow+1, max_row=last-1)
cats=Reference(ws, min_col=1, min_row=trow+2, max_row=last-1)
ch1.add_data(data, titles_from_data=True); ch1.set_categories(cats)
ch1.legend=None; ch1.width=9; ch1.height=6
ws.add_chart(ch1, "H12")

# Sub-category top profitability chart (Q3)
subq = pd.read_sql_query("""SELECT sub_category s, ROUND(SUM(profit),0) p
  FROM fact_orders GROUP BY 1 ORDER BY p DESC LIMIT 8""", conn)
srow=last+2
ws.cell(row=srow,column=1,value="Top Profit Sub-categories").font=Font(bold=True,size=13,color=NAVY)
ws.cell(row=srow+1,column=1,value="Sub-Category"); ws.cell(row=srow+1,column=2,value="Profit")
style_header(ws, srow+1, 2, ORANGE)
for i,r in subq.iterrows():
    ws.cell(row=srow+2+i,column=1,value=r.s).border=border
    c=ws.cell(row=srow+2+i,column=2,value=r.p); c.border=border; c.number_format='#,##0'
slast=srow+1+len(subq)
ch2=BarChart(); ch2.type="bar"; ch2.style=11; ch2.title="Top 8 profit sub-categories"
data=Reference(ws,min_col=2,min_row=srow+1,max_row=slast-1)
cats=Reference(ws,min_col=1,min_row=srow+2,max_row=slast-1)
ch2.add_data(data,titles_from_data=True); ch2.set_categories(cats)
ch2.legend=None; ch2.width=9; ch2.height=7
ws.add_chart(ch2,"H28")
autofit(ws,[22,16,16,12,12,3,3,3,3,22,12,12,12])

# =========================================================
# SHEET 2 : REGION x CATEGORY (SQL mart)
# =========================================================
ws2 = wb.create_sheet("Region x Category")
ws2.append(["Region","Category","Sub-Category","Units","Sales","Profit"])
style_header(ws2,1,6)
m = pd.read_sql_query("SELECT * FROM mart_region_category ORDER BY region, category, sales DESC", conn)
for _,r in m.iterrows():
    ws2.append([r.region,r.category,r.sub_category,r.quantity,r.sales,r.profit])
for rr_ in range(2, ws2.max_row+1):
    for cc_ in range(1,7):
        ws2.cell(row=rr_,column=cc_).border=border
    ws2.cell(row=rr_,column=5).number_format='#,##0'
    ws2.cell(row=rr_,column=6).number_format='#,##0'
autofit(ws2,[12,16,16,10,14,14])
# pivot-ish: P&L by category profit chart
cat = pd.read_sql_query("SELECT category c, ROUND(SUM(profit),0) p FROM fact_orders GROUP BY 1 ORDER BY p DESC",conn)
ch3=BarChart(); ch3.title="Profit by Category"; ch3.style=12
ws2.append([]); ws2.append(["Category","Profit"])
for i,r in cat.iterrows(): ws2.append([r.c,r.p])
style_header(ws2, ws2.max_row-len(cat), 2)
data=Reference(ws2,min_col=2,min_row=ws2.max_row-len(cat)+1,max_row=ws2.max_row)
cats=Reference(ws2,min_col=1,min_row=ws2.max_row-len(cat)+1,max_row=ws2.max_row)
ch3.add_data(data,titles_from_data=True); ch3.set_categories(cats); ch3.legend=None
ws2.add_chart(ch3,"I2")

# =========================================================
# SHEET 3 : Monthly trend (SQL Q6)
# =========================================================
ws3 = wb.create_sheet("Monthly Trend")
mon = pd.read_sql_query("""SELECT order_year y, order_month mo, ROUND(SUM(sales),0) rev,
 ROUND(SUM(profit),0) prof FROM fact_orders GROUP BY 1,2 ORDER BY 1,2""",conn)
ws3.append(["Year","Month","Revenue","Profit"]); style_header(ws3,1,4)
mon["label"]=mon.y.astype(str)+"-"+mon.mo.astype(str).str.zfill(2)
for _,r in mon.iterrows():
    ws3.append([r.y,r.mo,r.rev,r.prof])
for rr_ in range(2,ws3.max_row+1):
    for cc_ in range(1,5): ws3.cell(row=rr_,column=cc_).border=border
    ws3.cell(row=rr_,column=3).number_format='#,##0'; ws3.cell(row=rr_,column=4).number_format='#,##0'
ws3.insert_cols(5); ws3.column_dimensions['A'].width=8
# separate data for line chart with labels
lab=ws3.cell(row=1,column=6,value="Label"); 
ws3.cell(row=1,column=7,value="Revenue"); ws3.cell(row=1,column=8,value="Profit")
for i,r in mon.iterrows():
    ws3.cell(row=i+2,column=6,value=r.label)
    ws3.cell(row=i+2,column=7,value=r.rev)
    ws3.cell(row=i+2,column=8,value=r.prof)
ch4=LineChart(); ch4.title="Monthly Revenue & Profit Trend"; ch4.style=12
data=Reference(ws3,min_col=7,min_row=1,max_row=1+len(mon))
cats=Reference(ws3,min_col=6,min_row=2,max_row=1+len(mon))
ch4.add_data(data,titles_from_data=True); ch4.set_categories(cats); ch4.width=22; ch4.height=9
ch4.y_axis.title="USD"
ws3.add_chart(ch4,"J2")
autofit(ws3,[8,8,10,12,3,9,12,12])

# =========================================================
# SHEET 4 : ABC x XYZ inventory policy
# =========================================================
ws4 = wb.create_sheet("Inventory Policy")
inv = pd.read_csv("outputs/inventory_policy.csv")
# take the top A & B items sample for readability
view = inv[inv.abc_class.isin(["A","B"])].sort_values(["abc_class","profit"],ascending=[True,False]).head(60)
cols=["product_name","category","sub_category","abc_class","xyz_class","inventory_policy",
      "avg_monthly_demand","safety_stock","reorder_point","recommended_max_stock","stock_action"]
ws4.append(["ABC","XYZ","Policy"," # SKUs"]); 
piv = inv.groupby(["abc_class","xyz_class","inventory_policy"]).size().reset_index(name="n")
style_header(ws4,1,4)
for _,r in piv.iterrows():
    ws4.append([r.abc_class,r.xyz_class,r.inventory_policy,r.n])
for rr_ in range(2,ws4.max_row+1):
    for cc_ in range(1,5): ws4.cell(row=rr_,column=cc_).border=border
autofit(ws4,[8,8,44,8])
# representative inventory table
t = ws4.max_row+2
ws4.cell(row=t,column=1,value="Sample SKU-level policy (A & B class)").font=Font(bold=True,size=13,color=NAVY)
hdr = ["Product","Category","Sub-Cat","ABC","XYZ","avg mo demand","Safety stock","Reorder point","Max stock"]
for j,h in enumerate(hdr,start=1): ws4.cell(row=t+1,column=j,value=h)
style_header(ws4, t+1, len(hdr), BLUE)
for i,r in view.iterrows():
    rr_=t+2+i
    vals=[r.product_name,r.category,r.sub_category,r.abc_class,r.xyz_class,
          r.avg_monthly_demand,r.safety_stock,r.reorder_point,r.recommended_max_stock]
    for j,v in enumerate(vals,start=1):
        ws4.cell(row=rr_,column=j,value=v).border=border
autofit(ws4,[46,16,14,7,7,12,12,12,12])

# =========================================================
# SHEET 5 : Forecast
# =========================================================
ws5 = wb.create_sheet("12-mo Forecast")
fc = pd.read_csv("outputs/forecast_demand.csv").sort_values("revenue_forecast_total_12m",ascending=False)
ws5.append(["Sub-Category","Hist Units","Forecast 12m Units","Hist Revenue","Forecast 12m Revenue",
            "Revenue holdout MAPE %"])
style_header(ws5,1,6)
for _,r in fc.iterrows():
    ws5.append([r.sub_category,r.hist_units,r.units_forecast_total_12m,r.hist_revenue,
                r.revenue_forecast_total_12m,r.revenue_holdout_mape_pct])
for rr_ in range(2,ws5.max_row+1):
    for cc_ in range(1,7): ws5.cell(row=rr_,column=cc_).border=border
for c in [3,5,6]:
    for rr_ in range(2,ws5.max_row+1): ws5.cell(row=rr_,column=c).number_format='#,##0'
autofit(ws5,[16,12,16,12,18,18])

conn.close()
wb.save(OUT)
print("Saved", OUT)
