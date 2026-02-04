import pandas as pd
import re
import os
import configparser

def patch_pandas_read_sql():
    """
    Monkey patches pd.read_sql.
    Reads configuration from ../config/cpi_config.txt to apply:
    1. 'auto_closed' cleanup.
    2. LOB condition injection.
    3. Date partition injection via subquery.
    """

    # --- 1. SETUP & CONFIGURATION ---
    TARGET_TABLES = ["table1", "table2", "table3", "table4"]
    
    # Dynamically locate the config file
    # Gets the directory of this script (utilities/), goes up one level, then into config/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, '..', 'config', 'cpi_config.txt')

    # Read the config file
    config = configparser.RawConfigParser() # RawConfigParser avoids issues if your SQL has % symbols
    config.read(config_path)

    # Extract values (with defaults just in case file is missing)
    try:
        PARTITION_SQL = config.get('sql_patch', 'partition_sql')
        LOB_CONDITION = config.get('sql_patch', 'lob_condition')
        print(f"ℹ️ Loaded Config - Partition: [{PARTITION_SQL}] | LOB: [{LOB_CONDITION}]")
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        print(f"❌ Error reading cpi_config.txt: {e}")
        print("Please ensure [sql_patch] section exists with partition_sql and lob_condition.")
        return

    # --- 2. PREVENT DOUBLE PATCHING ---
    if hasattr(pd, '_original_read_sql'):
        print("ℹ️ pd.read_sql is already patched. Skipping re-patch.")
        return

    # Save the original function
    pd._original_read_sql = pd.read_sql

    # --- 3. DEFINE THE WRAPPER LOGIC ---
    def auto_partition_read_sql(sql, con, **kwargs):
        modified_sql = sql

        # A. REMOVE 'auto_closed' LOGIC
        # Remove the specific LEFT JOIN
        join_pattern = r"left\s+join\s+\(select\s+\*\s+from\s+table\s+c\)\s+auto_closed\s+on\s+c\.key\s*=\s*auto_closed\.key"
        modified_sql = re.sub(join_pattern, "", modified_sql, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove columns from SELECT (e.g., ", auto_closed.case")
        modified_sql = re.sub(r",\s*auto_closed\.\w+", "", modified_sql, flags=re.IGNORECASE)
        modified_sql = re.sub(r"auto_closed\.\w+\s*,", "", modified_sql, flags=re.IGNORECASE)

        # Remove condition from WHERE (e.g., "AND auto_closed.case is null")
        modified_sql = re.sub(r"and\s+auto_closed\.case\s+is\s+null", "", modified_sql, flags=re.IGNORECASE)

        # B. INJECT LOB CONDITION
        # If 'WHERE' exists, insert LOB check immediately after it with an 'AND'
        if re.search(r"\bwhere\b", modified_sql, re.IGNORECASE):
            modified_sql = re.sub(r"\bwhere\b", f"WHERE {LOB_CONDITION} AND", modified_sql, count=1, flags=re.IGNORECASE)
        else:
            # If no 'WHERE' exists, add one at the end
            modified_sql += f" WHERE {LOB_CONDITION}"

        # C. INJECT PARTITIONS (Subquery Method)
        for table in TARGET_TABLES:
            # Find table name (whole word match)
            pattern = re.compile(r'\b' + re.escape(table) + r'\b', re.IGNORECASE)
            
            if pattern.search(modified_sql):
                # Replace 'table' with '(SELECT * FROM table WHERE partition)'
                replacement = f"(SELECT * FROM {table} WHERE {PARTITION_SQL})"
                modified_sql = pattern.sub(replacement, modified_sql)
                print(f"✅ [Auto-SQL] Partitioned: {table}")

        # Execute original read_sql with the modified query
        return pd._original_read_sql(modified_sql, con, **kwargs)

    # --- 4. APPLY THE PATCH ---
    pd.read_sql = auto_partition_read_sql
    print("🚀 Success: pd.read_sql has been patched using settings from cpi_config.txt.")
