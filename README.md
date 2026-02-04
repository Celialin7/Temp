import pandas as pd
import re

# =============================================================================
# SQL Injection & Cleanup Logic (Monkey Patching)
# =============================================================================

# 1. DEFINITIONS
# List all table names that need the partition applied.
# Note: Ensure these match the names in your SQL exactly (case-insensitive).
TARGET_TABLES = [
    "table1", "table2", "table3", "table4" 
]

PARTITION_SQL = "cdf_feed_dt >= '2026-01-31'"
LOB_CONDITION = "c.lineofbusiness IN ('a', 'b', 'c')"

# 2. Save original read_sql
if not hasattr(pd, '_original_read_sql'):
    pd._original_read_sql = pd.read_sql

def auto_partition_read_sql(sql, con, **kwargs):
    modified_sql = sql

    # ---------------------------------------------------------
    # STEP 1: REMOVE 'auto_closed' LOGIC (Clean up)
    # ---------------------------------------------------------
    
    # A. Remove the specific LEFT JOIN for auto_closed
    # Regex explains: Match 'left join', optional spaces, the subquery, 'auto_closed', 
    # and the 'on' condition. Re.DOTALL allows matching across newlines.
    join_pattern = r"left\s+join\s+\(select\s+\*\s+from\s+table\s+c\)\s+auto_closed\s+on\s+c\.key\s*=\s*auto_closed\.key"
    modified_sql = re.sub(join_pattern, "", modified_sql, flags=re.IGNORECASE | re.DOTALL)

    # B. Remove 'auto_closed' from SELECT columns
    # matches ", auto_closed.col" or "auto_closed.col,"
    modified_sql = re.sub(r",\s*auto_closed\.\w+", "", modified_sql, flags=re.IGNORECASE)
    modified_sql = re.sub(r"auto_closed\.\w+\s*,", "", modified_sql, flags=re.IGNORECASE)

    # C. Remove 'auto_closed' from WHERE clause
    # Matches "AND auto_closed.case is null"
    modified_sql = re.sub(r"and\s+auto_closed\.case\s+is\s+null", "", modified_sql, flags=re.IGNORECASE)

    # ---------------------------------------------------------
    # STEP 2: INJECT NEW LOB CONDITION
    # ---------------------------------------------------------
    
    # Find 'WHERE' and insert the new condition immediately after it.
    # Result: WHERE c.lineofbusiness IN (...) AND original_condition...
    if re.search(r"\bwhere\b", modified_sql, re.IGNORECASE):
        modified_sql = re.sub(r"\bwhere\b", f"WHERE {LOB_CONDITION} AND", modified_sql, count=1, flags=re.IGNORECASE)
    else:
        # Fallback: if no WHERE exists, add one (unlikely in your case, but safe)
        modified_sql += f" WHERE {LOB_CONDITION}"

    # ---------------------------------------------------------
    # STEP 3: INJECT PARTITIONS (Smart Subquery Method)
    # ---------------------------------------------------------
    
    for table in TARGET_TABLES:
        # Regex to find the table name. \b ensures we don't match 'table10' when looking for 'table1'.
        pattern = re.compile(r'\b' + re.escape(table) + r'\b', re.IGNORECASE)
        
        if pattern.search(modified_sql):
            # Replace: table_name 
            # With: (SELECT * FROM table_name WHERE cdf_feed_dt >= '2026-01-31')
            # This works perfectly for both "FROM table" and "LEFT JOIN table"
            replacement = f"(SELECT * FROM {table} WHERE {PARTITION_SQL})"
            modified_sql = pattern.sub(replacement, modified_sql)
            print(f"✅ [Auto-SQL] Partitioned: {table}")

    # ---------------------------------------------------------
    # DEBUGGING (Optional)
    # ---------------------------------------------------------
    # Remove comment below to see the final SQL in your output
    # if modified_sql != sql:
    #    print(f"🔄 Final SQL:\n{modified_sql}")

    return pd._original_read_sql(modified_sql, con, **kwargs)

# 3. Apply Patch
pd.read_sql = auto_partition_read_sql
print("🚀 Common Util Loaded: SQL logic patched (Auto-closed removed, LOB added, Partitions applied).")
