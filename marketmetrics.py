import pandas as pd

# load cleaned data
df = pd.read_csv('final_cleaned_sold.csv')

# keep only the necessary info for dashboards; remove metadata and secondary school info.
core_fields = [
    'ListingKey', 'CloseDate', 'ClosePrice', 'ListPrice', 'OriginalListPrice', 
    'LivingArea', 'DaysOnMarket', 'Latitude', 'Longitude', 'PropertySubType', 
    'City', 'CountyOrParish', 'PostalCode', 'YearBuilt', 'rate_30yr_fixed',
    'ListOfficeName', 'BuyerOfficeName', 'ListAgentFullName', 'year_month'
]
df = df[core_fields].copy()

# flag outliers and then filter out. IQR to identify outliers
def remove_iqr_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return df[(df[column] >= lower) & (df[column] <= upper)]

# Aapply for price, sqft, and days on market
df = remove_iqr_outliers(df, 'ClosePrice')
df = remove_iqr_outliers(df, 'LivingArea')
df = remove_iqr_outliers(df, 'DaysOnMarket')

# get rid of unrealistic values that might still be in data after IQR filtering.
df = df[
    (df['ClosePrice'] > 50000) &    # Removes distressed sales/placeholder prices
    (df['LivingArea'] > 200) &      # Removes non-residential footprints
    (df['YearBuilt'] > 1800)        # Removes potential data entry errors in year
]

# create price ratio and price per sqft for metrics in dashboards.
df['price_ratio'] = df['ClosePrice'] / df['OriginalListPrice']
df['price_per_sqft'] = df['ClosePrice'] / df['LivingArea']

df.to_csv('final_market_data_for_tableau.csv', index=False)

print(f"Final columns: {len(df.columns)}. Final rows: {len(df)}.")