import pandas as pd
import re

def patch_pandas_read_sql():
    """
    Monkeys patches pd.read_sql to:
    1. Remove obsolete 'auto_closed' logic (Joins, Columns, Where clauses).
    2. Inject 'lineofbusiness' filter into the WHERE clause.
    3. Inject date partitions into target tables using the subquery method.
    """
    
    # --- CONFIGURATION ---
    # Update this list with your actual 4 table names
    TARGET_TABLES = ["table1", "table2", "table3", "table4"] 
    PARTITION_SQL = "cdf_feed_dt >= '2026-01-31'"
    LOB_CONDITION = "c.lineofbusiness IN ('a', 'b', 'c')"

    # --- PREVENT DOUBLE PATCHING ---
    if hasattr(pd, '_original_read_sql'):
        print("ℹ️ pd.read_sql is already patched. Skipping re-patch.")
        return

    # Save the original function
    pd._original_read_sql = pd.read_sql

    # --- DEFINE THE WRAPPER LOGIC ---
    def auto_partition_read_sql(sql, con, **kwargs):
        modified_sql = sql

        # 1. REMOVE 'auto_closed' LOGIC
        # Remove the specific LEFT JOIN
        join_pattern = r"left\s+join\s+\(select\s+\*\s+from\s+table\s+c\)\s+auto_closed\s+on\s+c\.key\s*=\s*auto_closed\.key"
        modified_sql = re.sub(join_pattern, "", modified_sql, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove columns from SELECT (e.g., ", auto_closed.case")
        modified_sql = re.sub(r",\s*auto_closed\.\w+", "", modified_sql, flags=re.IGNORECASE)
        modified_sql = re.sub(r"auto_closed\.\w+\s*,", "", modified_sql, flags=re.IGNORECASE)

        # Remove condition from WHERE (e.g., "AND auto_closed.case is null")
        modified_sql = re.sub(r"and\s+auto_closed\.case\s+is\s+null", "", modified_sql, flags=re.IGNORECASE)

        # 2. INJECT LOB CONDITION
        # If 'WHERE' exists, insert LOB check immediately after it with an 'AND'
        if re.search(r"\bwhere\b", modified_sql, re.IGNORECASE):
            modified_sql = re.sub(r"\bwhere\b", f"WHERE {LOB_CONDITION} AND", modified_sql, count=1, flags=re.IGNORECASE)
        else:
            # If no 'WHERE' exists, add one at the end
            modified_sql += f" WHERE {LOB_CONDITION}"

        # 3. INJECT PARTITIONS (Subquery Method)
        for table in TARGET_TABLES:
            # Find table name (whole word match)
            pattern = re.compile(r'\b' + re.escape(table) + r'\b', re.IGNORECASE)
            
            if pattern.search(modified_sql):
                # Replace 'table' with '(SELECT * FROM table WHERE partition)'
                # This works for both FROM and LEFT JOIN clauses safely
                replacement = f"(SELECT * FROM {table} WHERE {PARTITION_SQL})"
                modified_sql = pattern.sub(replacement, modified_sql)
                print(f"✅ [Auto-SQL] Partitioned: {table}")

        # Execute original read_sql with the modified query
        return pd._original_read_sql(modified_sql, con, **kwargs)

    # --- APPLY THE PATCH ---
    pd.read_sql = auto_partition_read_sql
    print("🚀 Success: pd.read_sql has been patched with auto-partition and cleanup logic.")
