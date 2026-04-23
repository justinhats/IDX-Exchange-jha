import pandas as pd

# load cleaned dataset
df = pd.read_csv('final_cleaned_sold.csv')

# date conversions
date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate']
for col in date_cols:
    df[col] = pd.to_datetime(df[col])

# price ratio from close to original
df['price_ratio'] = df['ClosePrice'] / df['OriginalListPrice']

# normalize price across sizes
df['price_per_sqft'] = df['ClosePrice'] / df['LivingArea']

# time from listing to contract signing
df['listing_to_contract_days'] = (df['PurchaseContractDate'] - df['ListingContractDate']).dt.days

# time from contract signing to closing
df['contract_to_close_days'] = (df['CloseDate'] - df['PurchaseContractDate']).dt.days

# year-month period 
df['YrMo'] = df['CloseDate'].dt.to_period('M')

# summary statistics: close price, price per sqft, days on market, price ratio compared by median and mean
def generate_segment_summary(df, groupby_cols):
    summary = df.groupby(groupby_cols).agg({
        'ClosePrice': ['median', 'mean'],
        'price_per_sqft': 'mean',
        'DaysOnMarket': 'median',
        'price_ratio': 'mean'
    }).reset_index()
    return summary

# required segments
property_segment = generate_segment_summary(df, ['PropertyType', 'PropertySubType'])
geo_segment = generate_segment_summary(df, ['CountyOrParish', 'MLSAreaMajor'])
office_segment = generate_segment_summary(df, ['ListOfficeName', 'BuyerOfficeName'])

# Apply IQR to identify outliers
def apply_iqr_filter(df, column):
    Q1 = df[column].quantile(0.25) 
    Q3 = df[column].quantile(0.75) 
    IQR = Q3 - Q1 
    lower = Q1 - 1.5 * IQR 
    upper = Q3 + 1.5 * IQR 
    
    # extreme values flagged for review
    df[f'{column}_outlier_flag'] = (df[column] < lower) | (df[column] > upper)
    return df, lower, upper

# apply to needed fields
for col in ['ClosePrice', 'LivingArea', 'DaysOnMarket']:
    df, low, high = apply_iqr_filter(df, col)

# filter out the outleirs
df_filtered = df[~(df['ClosePrice_outlier_flag'] | 
                   df['LivingArea_outlier_flag'] | 
                   df['DaysOnMarket_outlier_flag'])].copy()

# final summary
print(f"Post IQR Cleaned Rows: {len(df_filtered)} (Original: {len(df)})") 
print(f"Median ClosePrice Before/After: {df['ClosePrice'].median()} / {df_filtered['ClosePrice'].median()}") 

# datasets.
df.to_csv('sold_with_outlier_flags.csv', index=False)
df_filtered.to_csv('final_market_data_for_tableau.csv', index=False)