import pandas as pd
import glob

#Week 1: dataset aggregation
# Use glob to check all csv listing files, and use latin1 for encoding
sold_files = glob.glob('CRMLSSold202*.csv') 
datasets = [pd.read_csv(f, encoding='latin1') for f in sold_files]
df_sold = pd.concat(datasets)
#concat into one singular dataframe

initial_row_count = len(df_sold)
# Filter only for residential property types, according to handbook
df_sold = df_sold[df_sold['PropertyType'] == 'Residential']
post_filter_row_count = len(df_sold)
print(f"Initial rows: {initial_row_count}, Post-Residential filter: {post_filter_row_count}")
#check row counts after the filter

#Week 2-3: dataset structuring and validation
# fetch data from fred url
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url) 

# convert data from FRED to datetime in the date column, then rename for clarity
mortgage.columns = ['date', 'rate_30yr_fixed']
mortgage['date'] = pd.to_datetime(mortgage['date'])
# resample weekly rates to monthly averages 
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = mortgage.groupby('year_month')['rate_30yr_fixed'].mean().reset_index()

# create join key for listings based on ListingContractDate 
df_sold['year_month'] = pd.to_datetime(df_sold['CloseDate']).dt.to_period('M')

# merge economic data onto listing dataset 
df_enriched = df_sold.merge(mortgage_monthly, on='year_month', how='left')
# check for unmatched rows (rate should not be null)
print(f"Validation: Missing Mortgage Rates = {df_enriched['rate_30yr_fixed'].isnull().sum()}")

# numeric distribution summary for ClosePrice, LivingArea, and DaysOnMarket
cols_to_summary = ['ClosePrice', 'LivingArea', 'DaysOnMarket', 'rate_30yr_fixed']
print("\n[Statistical Summary]:")
print(df_enriched[cols_to_summary].describe(percentiles=[.25, .5, .75, .9]))
# save everything to enriched listing dataset for cleaning
df_enriched.to_csv('enriched_sold_2024_2026.csv', index=False)