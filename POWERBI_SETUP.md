# Power BI Version

A native `.pbix` file must be created in Power BI Desktop, which is not available on macOS. The prepared files in this project are ready for import.

## Import

1. Open Power BI Desktop on Windows.
2. Select **Get data > Excel** and choose `data/OTR_cleaned.xlsx`, or choose **Text/CSV** and use `data/OTR_cleaned.csv`.
3. Load the table.
4. Import `powerbi_theme.json` from **View > Themes > Browse for themes**.
5. Create the measures below.

## Measures

```DAX
Total Tickets = DISTINCTCOUNT(OTR_cleaned[Ticket Number])

Closed Tickets = CALCULATE([Total Tickets], OTR_cleaned[Current_Status] = "Closed")

Pending Tickets = CALCULATE([Total Tickets], OTR_cleaned[Current_Status] = "Pending")

Reopened Tickets = CALCULATE([Total Tickets], OTR_cleaned[Current_Status] = "Reopened")

Closure Rate = DIVIDE([Closed Tickets], [Total Tickets], 0)

Open Tickets = CALCULATE([Total Tickets], OTR_cleaned[Current_Status] IN {"Pending", "Reopened"})

Average Open Age = CALCULATE(AVERAGE(OTR_cleaned[Age_Days]), OTR_cleaned[Current_Status] IN {"Pending", "Reopened"})

Tickets Over 15 Days = CALCULATE([Total Tickets], OTR_cleaned[Current_Status] IN {"Pending", "Reopened"}, OTR_cleaned[Age_Days] > 15)
```

## Recommended pages

- **Executive Overview:** KPI cards, ticket volume by month, status donut, top issue categories, responsible-area bar chart.
- **Root Cause & Responsibility:** issue category, responsible area, ASM, module, and distributor visuals.
- **Operations / Action Tracker:** pending/reopened table, age bucket donut, backlog by ASM, and open-ticket KPIs.

The cleaned data contains 1,088 records from January 1 through June 30, 2026, with Excel date serials corrected and no 1970 date artifacts.
