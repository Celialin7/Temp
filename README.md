import pandas as pd
import re

# =============================================================================
# Auto-inject Partition Logic (Monkey Patching)
# =============================================================================

# 1. Configure your table names and corresponding partition conditions
# Format: 'database.table_name': 'partition_condition'
# Note: It is best to use the full table name to avoid mis-matching substrings
TABLE_PARTITION_MAP = {
    "db_name.table_A": "ds = '20251001'",  
    "db_name.table_B": "pt_date >= '2024-01-01' AND pt_date <= '2024-12-31'",
    "project_db.customer_list": "version = 'v2'",
    # Add the 4 tables and their corresponding partitions you need to handle here
}

# 2. Save the original pandas read_sql method (prevent infinite recursion)
# Use hasattr to check and prevent double patching if this file is imported multiple times
if not hasattr(pd, '_original_read_sql'):
    pd._original_read_sql = pd.read_sql

# 3. Define the interceptor function
def auto_partition_read_sql(sql, con, **kwargs):
    """
    Intercepts all pd.read_sql calls and automatically injects partition conditions for specific tables.
    """
    modified_sql = sql
    
    for table_name, partition_condition in TABLE_PARTITION_MAP.items():
        # Use regex for case-insensitive matching
        # \b ensures we match the whole word (complete table name), not part of another word
        pattern = re.compile(r'\b' + re.escape(table_name) + r'\b', re.IGNORECASE)
        
        if pattern.search(modified_sql):
            # --- Core Magic: Subquery Replacement Method ---
            # Principle: Replace "FROM table" with "FROM (SELECT * FROM table WHERE partition) AS table"
            # This is the safest method as it automatically adapts to Aliases, Joins, and existing Where clauses 
            # in the original code.
            
            # The replacement string: (SELECT * FROM table_name WHERE partition_condition)
            # Note: Usually the legacy code has an alias following the table name 
            # (e.g., FROM table t1), so replacing 'table' with '(subquery)' results in '(subquery) t1', which is valid SQL.
            replacement = f"(SELECT * FROM {table_name} WHERE {partition_condition})"
            
            modified_sql = pattern.sub(replacement, modified_sql)
            
            # Print log for debugging (to confirm replacement success)
            print(f"✅ [Auto-Partition] Injected partition for table: {table_name}")

    # If SQL was modified, print a preview (useful for debugging, can be commented out later)
    if modified_sql != sql:
        print(f"🔄 Modified SQL Preview: {modified_sql[:150]}...")

    # 4. Call the original pandas read_sql to execute the modified SQL
    return pd._original_read_sql(modified_sql, con, **kwargs)

# 5. Overwrite (Monkey Patch) pandas read_sql
pd.read_sql = auto_partition_read_sql

print("🚀 Common Util Loaded: pd.read_sql has been patched to handle partitions automatically.")
