import pandas as pd

# load datasets
sold = pd.read_csv('enriched_sold_2024_2026.csv', encoding='latin1')
listings = pd.read_csv('enriched_listings_2024_2026.csv', encoding='latin1')

def refined_cleaning(df, label):
    # column reduction: drop fields with more than 90% missing values and redundant data.
    cols_to_drop = [
        'UnparsedAddress.1', 'Latitude.1', 'Longitude.1', 'PropertyType.1',
        'ListPrice.1', 'CloseDate.1', 'DaysOnMarket.1', 'ListAgentFirstName.1',
        'ListAgentLastName.1', 'MiddleOrJuniorSchoolDistrict'
    ]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    # convert date and time for consistency
    date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # remove duplicates
    df = df.dropna(subset=['ListingKey', 'ClosePrice', 'ListPrice', 'LivingArea'])
    
    # remove impossible values (negative bedrooms or bathrooms), small sqft and negative prices and such.
    df = df[
        (df['ClosePrice'] > 0) & 
        (df['LivingArea'] > 50) & 
        (df['DaysOnMarket'] >= 0) &
        (df['BedroomsTotal'] >= 0) &
        (df['BathroomsTotalInteger'] >= 0)
    ]

    # if listing date is after closing date, flag as an error
    df['neg_timeline_flag'] = df['ListingContractDate'] > df['CloseDate']
    
    # California coordinates must be negative longitude and positive latitude
    df['bad_geo_flag'] = (df['Longitude'] >= 0) | (df['Latitude'] <= 0)

    # export summary
    print(f"{label.upper()} Refined Summary")
    print(f"Final Count: {len(df)} rows")
    print(f"Geographic errors flagged: {df['bad_geo_flag'].sum()}")
    print(f"Timeline errors flagged: {df['neg_timeline_flag'].sum()}")
    
    df.to_csv(f'final_cleaned_{label}.csv', index=False)
    return df

# Execute
clean_sold = refined_cleaning(sold, 'sold')
clean_listings = refined_cleaning(listings, 'listings')