import pandas as pd

# load the enriched datasets
sold = pd.read_csv('enriched_sold_2024_2026.csv', encoding='latin1')
listings = pd.read_csv('enriched_listings_2024_2026.csv', encoding='latin1')

def clean_mls_data(df, label):
    initial_rows = len(df)
    
    # convert to datetime format
    date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # check for consistency, create boolean flags for logical errors
    df['listing_after_close_flag'] = df['ListingContractDate'] > df['CloseDate']
    df['purchase_after_close_flag'] = df['PurchaseContractDate'] > df['CloseDate']
    df['negative_timeline_flag'] = df['ListingContractDate'] > df['PurchaseContractDate']
    
    # check for geographic anomalies - missing or invalid California coordinates
    df['invalid_geo_flag'] = (df['Latitude'].isnull()) | (df['Longitude'].isnull()) | \
                             (df['Latitude'] == 0) | (df['Longitude'] >= 0)
    
    # filter rows with invalid numeric values
    clean_df = df[
        (df['ClosePrice'] > 0) & 
        (df['LivingArea'] > 0) & 
        (df['DaysOnMarket'] >= 0)
    ].copy()
    
    # document
    print(f"--- {label.upper()} CLEANING SUMMARY ---")
    print(f"Rows before numeric cleaning: {initial_rows}")
    print(f"Rows after numeric cleaning: {len(clean_df)}")
    print(f"Invalid Date Timelines detected: {df['negative_timeline_flag'].sum()}")
    print(f"Invalid Geo Records detected: {df['invalid_geo_flag'].sum()}")
    
    # save as a cleaned csv
    clean_df.to_csv(f'final_cleaned_{label}.csv', index=False)
    return clean_df

# execute for both datasets
clean_sold = clean_mls_data(sold, 'sold')
clean_listings = clean_mls_data(listings, 'listings')