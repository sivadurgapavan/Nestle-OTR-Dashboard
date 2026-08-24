import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="OTR Ticket Intelligence", page_icon="📊", layout="wide")
DATA = Path(__file__).parent/"data"/"OTR_cleaned.csv"
LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Nestl%C3%A9_textlogo.svg/330px-Nestl%C3%A9_textlogo.svg.png"
NESTLE_BLUE = "#0085c3"
BLUE_SCALE = ["#0085c3", "#339ddf", "#66b6eb", "#99ceec"]
NESTLE_RED = "#d70c14"

theme = st.sidebar.selectbox("Appearance", ["Light", "Dark"], index=0)
dark_mode = theme == "Dark"
theme_colors = {
    "page": "#101820" if dark_mode else "#f5f7fb",
    "surface": "#182631" if dark_mode else "#ffffff",
    "border": "#2e4554" if dark_mode else "#e5e9f0",
    "text": "#e8f0f5" if dark_mode else "#17212b",
    "muted": "#b4c4ce" if dark_mode else "#536273",
    "insight": "#193246" if dark_mode else "#eaf2fb",
    "header_start": "#005b87" if dark_mode else NESTLE_BLUE,
    "header_end": "#0074a9" if dark_mode else "#006da3",
    "plot_template": "plotly_dark" if dark_mode else "plotly_white",
}

@st.cache_data
def load():
    x=pd.read_csv(DATA)
    for c in ["Ticket_DateTime","Ticket_Date","Closed_Date"]:
        if c in x: x[c]=pd.to_datetime(x[c],errors="coerce")
    return x

df=load()

if st.sidebar.button("Refresh data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.markdown(f"""<style>
.stApp{{background:{theme_colors['page']};color:{theme_colors['text']}}}
.main{{background:{theme_colors['page']}}}.block-container{{padding-top:1rem}}
.header{{background:linear-gradient(90deg,{theme_colors['header_start']},{theme_colors['header_end']});color:white;padding:18px 24px;border-radius:12px;margin-bottom:15px}}
.header h1,.header p{{color:white!important}}
.brand{{display:inline-flex;background:#FFFFFF;padding:7px 14px;border-radius:6px;margin-bottom:8px}}
.brand img{{display:block;width:126px;height:auto}}
.insight{{background:{theme_colors['insight']};border-left:5px solid {theme_colors['header_end']};color:{theme_colors['text']};padding:12px;border-radius:8px}}
div[data-testid="stMetric"]{{background:{theme_colors['surface']};border:1px solid {theme_colors['border']};padding:10px;border-radius:10px}}
div[data-testid="stMetric"] label, div[data-testid="stCaptionContainer"]{{color:{theme_colors['muted']}}}
h1,h2,h3,p,span,label{{color:{theme_colors['text']}}}
</style>""",unsafe_allow_html=True)

st.sidebar.title("OTR Dashboard")
page=st.sidebar.radio("Page",["1 — Executive Overview","2 — Root Cause & Responsibility","3 — Operations / Action Tracker"])

dmin=df.Ticket_Date.min().date(); dmax=df.Ticket_Date.max().date()
dr=st.sidebar.date_input("Ticket Date",value=(dmin,dmax),min_value=dmin,max_value=dmax)
if isinstance(dr,(tuple,list)) and len(dr)==2:
    start,end=dr
else: start=end=dr

def pick(label,col):
    vals=sorted(df[col].dropna().astype(str).unique())
    return st.sidebar.multiselect(label,vals)

filters={"ASM_Name":pick("ASM", "ASM_Name"),"Distributor_Name":pick("Distributor","Distributor_Name"),
         "DC":pick("DC CODE","DC"),"Module_Name":pick("Module","Module_Name"),"Responsible_Area":pick("Responsible Area","Responsible_Area"),
         "Current_Status":pick("Status","Current_Status"),"Issue_Category":pick("Issue Category","Issue_Category")}

f=df[(df.Ticket_Date.dt.date>=start)&(df.Ticket_Date.dt.date<=end)].copy()
for col,vals in filters.items():
    if vals: f=f[f[col].astype(str).isin(vals)]

def ticket_count(frame, status=None):
    if status is not None:
        frame=frame[frame.Current_Status==status]
    return frame["Ticket Number"].nunique()

if page.startswith("1"):
    st.markdown(f'<div class="header"><div class="brand"><img src="{LOGO_URL}" alt="Nestlé logo"></div><h1>OTR EXECUTIVE DASHBOARD</h1><p>Overview of OTR ticket status, workload and key metrics</p></div>',unsafe_allow_html=True)
    total=ticket_count(f); closed=ticket_count(f,"Closed"); pending=ticket_count(f,"Pending"); reopened=ticket_count(f,"Reopened")
    rate=closed/total if total else 0
    a,b,c,d,e=st.columns(5)
    a.metric("Total Tickets",f"{total:,}"); b.metric("Closed",f"{closed:,}"); c.metric("Pending",f"{pending:,}"); d.metric("Reopened",f"{reopened:,}"); e.metric("Closure Rate",f"{rate:.1%}")
    st.caption(f"Showing {total:,} tickets after filters | {start:%d %b %Y} to {end:%d %b %Y}")
    top_issue=f.Issue_Category.fillna("Unclassified").value_counts().idxmax() if len(f) else "-"
    top_area=f.Responsible_Area.fillna("Unclassified").value_counts().idxmax() if len(f) else "-"
    st.markdown(f'<div class="insight">💡 <b>Key insight:</b> {top_issue} is the leading issue category; {top_area} has the highest responsibility volume.</div>',unsafe_allow_html=True)
    l,r=st.columns(2)
    with l:
        m=f.groupby(f.Ticket_Date.dt.to_period("M")).size().reset_index(name="Tickets"); m["Month"]=m.Ticket_Date.astype(str)
        fig=px.line(m,x="Month",y="Tickets",markers=True,title="Ticket Volume by Month",template=theme_colors["plot_template"])
        fig.update_traces(line_color=NESTLE_BLUE, marker_color=NESTLE_BLUE)
        st.plotly_chart(fig,use_container_width=True)
    with r:
        s=f.Status_Group.value_counts().reset_index(); s.columns=["Status","Tickets"]
        status_colors={"Closed":NESTLE_BLUE,"Pending":NESTLE_RED,"Reopened":NESTLE_RED}
        st.plotly_chart(px.pie(s,names="Status",values="Tickets",hole=.55,title="Ticket Status Distribution",template=theme_colors["plot_template"],color="Status",color_discrete_map=status_colors,color_discrete_sequence=BLUE_SCALE),use_container_width=True)
    l,r=st.columns(2)
    with l:
        x=f.Issue_Category.fillna("Unclassified").value_counts().head(8).sort_values()
        st.plotly_chart(px.bar(x,x=x.values,y=x.index,orientation="h",title="Top Issue Categories",template=theme_colors["plot_template"],color_discrete_sequence=BLUE_SCALE),use_container_width=True)
    with r:
        x=f.Responsible_Area.fillna("Unclassified").value_counts().sort_values()
        st.plotly_chart(px.bar(x,x=x.values,y=x.index,orientation="h",title="Tickets by Responsible Area",template=theme_colors["plot_template"],color_discrete_sequence=BLUE_SCALE),use_container_width=True)
    st.subheader("Open workload by age")
    open_tickets=f[f.Current_Status.isin(["Pending","Reopened"])]
    age_order=["0–3 Days","4–7 Days","8–15 Days",">15 Days"]
    age_counts=open_tickets.Age_Bucket.value_counts().reindex(age_order).fillna(0).reset_index()
    age_counts.columns=["Age Bucket","Tickets"]
    st.plotly_chart(px.bar(age_counts,x="Age Bucket",y="Tickets",text_auto=True,title="Pending and reopened tickets by age",template=theme_colors["plot_template"],color_discrete_sequence=[NESTLE_RED]),use_container_width=True)

elif page.startswith("2"):
    st.markdown(f'<div class="header"><div class="brand"><img src="{LOGO_URL}" alt="Nestlé logo"></div><h1>ROOT CAUSE & RESPONSIBILITY ANALYSIS</h1><p>Issues, responsible areas, ASM workload, modules and distributors</p></div>',unsafe_allow_html=True)
    charts=[("Issue Category","Issue_Category"),("Responsible Area","Responsible_Area"),("ASM","ASM_Name"),("Module","Module_Name")]
    for i,(title,col) in enumerate(charts):
        if i%2==0: l,r=st.columns(2)
        box=l if i%2==0 else r
        x=f[col].fillna("Unclassified").value_counts().head(12).sort_values()
        with box:
            st.plotly_chart(px.bar(x,x=x.values,y=x.index,orientation="h",title=f"Tickets by {title}",template=theme_colors["plot_template"],color_discrete_sequence=BLUE_SCALE),use_container_width=True)
    st.subheader("Top Distributors")
    x=f.Distributor_Name.fillna("Unassigned").value_counts().head(15).rename("Tickets").to_frame()
    st.dataframe(x,use_container_width=True)

else:
    st.markdown(f'<div class="header"><div class="brand"><img src="{LOGO_URL}" alt="Nestlé logo"></div><h1>OTR OPERATIONS / ACTION TRACKER</h1><p>Track pending and reopened tickets, ageing and follow-up</p></div>',unsafe_allow_html=True)
    a=f[f.Current_Status.isin(["Pending","Reopened"])].copy()
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Pending",ticket_count(a,"Pending")); c2.metric("Reopened",ticket_count(a,"Reopened")); c3.metric(">15 Days",a.loc[a.Age_Days>15,"Ticket Number"].nunique()); c4.metric("Average Age",f'{a.Age_Days.mean():.1f} days' if len(a) else "0")
    l,r=st.columns([2,1])
    with l:
        cols=["Ticket Number","Ticket_Date","Current_Status","ASM_Name","Distributor_Name","Issue_Category","Responsible_Area","Module_Name","Age_Days","Remarks_Updated"]
        cols=[c for c in cols if c in a.columns]
        st.subheader("Pending & Reopened Ticket Queue")
        st.dataframe(a[cols].sort_values("Age_Days",ascending=False),use_container_width=True,height=520)
    with r:
        x=a.Age_Bucket.value_counts().reindex(["0–3 Days","4–7 Days","8–15 Days",">15 Days"]).fillna(0).reset_index(); x.columns=["Age Bucket","Tickets"]
        st.plotly_chart(px.pie(x,names="Age Bucket",values="Tickets",hole=.45,title="Ageing",template=theme_colors["plot_template"],color_discrete_sequence=BLUE_SCALE),use_container_width=True)
        x=a.ASM_Name.fillna("Unassigned").value_counts().head(10).sort_values()
        st.plotly_chart(px.bar(x,x=x.values,y=x.index,orientation="h",title="Backlog by ASM",template=theme_colors["plot_template"],color_discrete_sequence=BLUE_SCALE),use_container_width=True)

st.sidebar.divider()
st.sidebar.caption(f"{len(df):,} ticket records loaded")
st.sidebar.caption(f"Data period: {df.Ticket_Date.min():%d %b %Y} – {df.Ticket_Date.max():%d %b %Y}")
st.sidebar.caption("Source: OTR_cleaned.csv")
