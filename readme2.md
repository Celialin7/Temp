import pandas as pd
import numpy as np

# Assume df1 and df2 are your remaining 1.1k unmatched dataframes
# Columns expected: ['txn_ref', 'customer_id', 'trade_date', 'currency', 'amount']

# --- STEP 1: NORMALIZE DATA (Fixes datatype and format worries) ---
def normalize_data(df):
    d = df.copy()
    # Standardize strings (strip whitespaces, make uppercase)
    d['customer_id'] = d['customer_id'].astype(str).str.strip().str.upper()
    d['currency'] = d['currency'].astype(str).str.strip().str.upper()
    
    # Convert dates to standard datetime objects (handles different string formats automatically)
    d['trade_date'] = pd.to_datetime(d['trade_date'], errors='coerce')
    
    # Convert amounts to standard floats, rounded to 2 decimals
    d['amount'] = pd.to_numeric(d['amount'], errors='coerce').round(2)
    return d

df1_clean = normalize_data(df1)
df2_clean = normalize_data(df2)

# --- STEP 2: PASS A (Match ID + Date + Currency -> Check Amount) ---
# We merge on the keys, then check if amounts are extremely close (e.g., within 0.05 difference)
match_A = pd.merge(df1_clean, df2_clean, on=['customer_id', 'trade_date', 'currency'], suffixes=('_src1', '_src2'))

# Smart Check: isclose allows a tolerance for floating point or slight fee discrepancies
match_A['amount_match'] = np.isclose(match_A['amount_src1'], match_A['amount_src2'], atol=0.05)
successful_A = match_A[match_A['amount_match'] == True]

# --- STEP 3: PASS B (Match ID + Amount + Currency -> Check Date) ---
# We merge on amount instead, and check if the dates are within 1-2 days of each other
match_B = pd.merge(df1_clean, df2_clean, on=['customer_id', 'amount', 'currency'], suffixes=('_src1', '_src2'))

# Smart Check: Calculate date difference in days (handles T+1 / T+2 settlement mismatches)
match_B['date_diff_days'] = (match_B['trade_date_src1'] - match_B['trade_date_src2']).dt.days.abs()
match_B['date_match'] = match_B['date_diff_days'] <= 2 # Tolerance of 2 days
successful_B = match_B[match_B['date_match'] == True]

# Note: In a production script, you would want to drop records from df1/df2 
# that matched in Pass A before running Pass B to avoid duplicate matching!
