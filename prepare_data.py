import pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parent
src=ROOT/'data'/'OTR_original.xlsx'
out=ROOT/'data'/'OTR_cleaned.csv'
out_excel=ROOT/'data'/'OTR_cleaned.xlsx'
df=pd.read_excel(src,sheet_name='Sheet1')
df=df[df['Ticket Number'].notna()].copy()

def parse_date(values):
    numeric=pd.to_numeric(values,errors='coerce')
    excel_dates=pd.to_datetime(numeric,unit='D',origin='1899-12-30',errors='coerce')
    text_dates=pd.to_datetime(values.where(numeric.isna()),dayfirst=True,errors='coerce')
    return text_dates.combine_first(excel_dates)

for c in ['Ticket_DateTime','Ticket_Date','Closed_Date']:
    if c in df: df[c]=parse_date(df[c])

start=pd.Timestamp('2026-01-01')
end=pd.Timestamp('2026-06-30 23:59:59')
df=df[df['Ticket_Date'].between(start,end)].copy()
ref=df['Ticket_Date'].max()
df['Age_Days']=(ref-df['Ticket_Date']).dt.days.clip(lower=0)
df['Status_Group']=df['Current_Status'].fillna('Unknown').replace({'Not Related to DC':'Not Related'})
df['Age_Bucket']=pd.cut(df['Age_Days'],[-1,3,7,15,float('inf')],labels=['0–3 Days','4–7 Days','8–15 Days','>15 Days'])
df=df.dropna(axis=1,how='all')
df.to_csv(out,index=False)
df.to_excel(out_excel,index=False)
print(f'Saved {len(df):,} rows')
