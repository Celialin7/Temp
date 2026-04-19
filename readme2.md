import os
import re
import sys

import pandas as pd


def patch_python_files_for_dc_query(project_root=None):
    """
    Batch-rewrite cpi*.py files:
    1) Insert two hive set lines right after `conn, cursor = db_util.db_connect()` (insert once only)
    2) Replace `<df_var> = pd.read_sql(<sql_expr>,conn)` with `<df_var> = dc.query(<sql_expr>)`
       while preserving the left-hand dataframe variable name.
    """
    if project_root is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, ".."))

    set_line_1 = 'dc.query("set hive.strict.checks.no.partition.filter=false")'
    set_line_2 = 'dc.query("set hive.mapred.mode=nonstrict")'
    import_line = "from utilities.common_util import dc"

    patched_files = 0
    updated_connect_blocks = 0
    updated_read_sql_lines = 0

    for root, _, files in os.walk(project_root):
        for name in files:
            if not (name.startswith("cpi") and name.endswith(".py")):
                continue

            path = os.path.join(root, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    original = f.read()
            except Exception:
                continue

            lines = original.splitlines()
            new_lines = []
            file_changed = False

            for line in lines:
                m_conn = re.match(r"^([ \t]*)conn, cursor = db_util\.db_connect\(\)[ \t]*$", line)
                if m_conn:
                    indent = m_conn.group(1)
                    new_lines.append(line)
                    next1 = indent + set_line_1
                    next2 = indent + set_line_2
                    if next1 not in lines and next2 not in lines:
                        new_lines.append(next1)
                        new_lines.append(next2)
                        file_changed = True
                        updated_connect_blocks += 1
                    continue

                m_sql = re.match(
                    r"^([ \t]*)([A-Za-z_]\w*)\s*=\s*pd\.read_sql\(\s*(.*?)\s*,\s*conn\s*\)[ \t]*$",
                    line,
                )
                if m_sql:
                    indent, df_var, sql_expr = m_sql.groups()
                    replaced = f"{indent}{df_var} = dc.query({sql_expr})"
                    new_lines.append(replaced)
                    if replaced != line:
                        file_changed = True
                        updated_read_sql_lines += 1
                    continue

                new_lines.append(line)

            has_dc_query = any("dc.query(" in l for l in new_lines)
            has_dc_import = any(l.strip() == import_line for l in new_lines)
            if has_dc_query and not has_dc_import:
                insert_at = 0
                for i, l in enumerate(new_lines):
                    s = l.strip()
                    if s.startswith("import ") or s.startswith("from "):
                        insert_at = i + 1
                new_lines.insert(insert_at, import_line)
                file_changed = True

            if file_changed:
                patched_files += 1
                with open(path, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines) + ("\n" if original.endswith("\n") else ""))

    print(
        f"🛠️ [Auto-PyPatch] files={patched_files}, "
        f"db_connect_blocks={updated_connect_blocks}, read_sql_lines={updated_read_sql_lines}"
    )
    sys.stdout.flush()


def _remove_auto_closed(sql):
    modified_sql = sql
    auto_closed_end_pat = re.compile(r"\)\s*(?:as\s+)?auto_closed\b", flags=re.IGNORECASE)
    left_join_pat = re.compile(r"\bleft\s+join\b", flags=re.IGNORECASE)
    removed_block_count = 0
    removed_line_count = 0

    def _preview(text, limit=220):
        compact = " ".join(text.split())
        if len(compact) <= limit:
            return compact
        return compact[:limit] + " ..."

    # Step 1: for each ") auto_closed", remove from the nearest LEFT JOIN to this point.
    search_pos = 0
    while True:
        end_match = auto_closed_end_pat.search(modified_sql, search_pos)
        if not end_match:
            break

        nearest_left_join = None
        for join_match in left_join_pat.finditer(modified_sql, 0, end_match.start()):
            nearest_left_join = join_match

        if nearest_left_join:
            block_start = nearest_left_join.start()
            block_end = end_match.end()
            removed_block = modified_sql[block_start:block_end]
            start_line = modified_sql.count("\n", 0, block_start) + 1
            end_line = modified_sql.count("\n", 0, block_end) + 1
            removed_block_count += 1
            print(
                f"🧹 [auto_closed] removed JOIN block #{removed_block_count} "
                f"(lines {start_line}-{end_line}): {_preview(removed_block)}"
            )
            modified_sql = (
                modified_sql[:block_start]
                + modified_sql[block_end:]
            )
            search_pos = block_start
        else:
            print(
                "⚠️ [auto_closed] found ') auto_closed' but no preceding LEFT JOIN; "
                "skipping block delete."
            )
            search_pos = end_match.end()

    # Step 2: remove entire lines containing auto_closed to clean SELECT/WHERE leftovers.
    lines = modified_sql.splitlines()
    if len(lines) > 1:
        kept_lines = []
        for line_no, line in enumerate(lines, start=1):
            if "auto_closed" in line.lower():
                removed_line_count += 1
                print(
                    f"🧹 [auto_closed] removed line {line_no}: {_preview(line, limit=180)}"
                )
                continue
            kept_lines.append(line)
        modified_sql = "\n".join(kept_lines)
        if modified_sql and modified_sql != sql and sql.endswith("\n"):
            modified_sql += "\n"
    else:
        # Single-line SQL safeguard: avoid dropping the whole statement.
        before = modified_sql
        modified_sql = re.sub(r",\s*auto_closed\.\w+", "", modified_sql, flags=re.IGNORECASE)
        modified_sql = re.sub(r"auto_closed\.\w+\s*,", "", modified_sql, flags=re.IGNORECASE)
        modified_sql = re.sub(
            r"\b(?:and|or)\s+auto_closed\.\w+\s+is\s+null\b",
            "",
            modified_sql,
            flags=re.IGNORECASE,
        )
        modified_sql = re.sub(
            r"\bon\b[\s\S]*?auto_closed\.\w+[\s\S]*?"
            r"(?=\bleft\s+join\b|\bright\s+join\b|\binner\s+join\b|\bfull\s+join\b|"
            r"\bwhere\b|\bgroup\s+by\b|\border\s+by\b|\bhaving\b|\blimit\b|$)",
            " ",
            modified_sql,
            flags=re.IGNORECASE,
        )
        if modified_sql != before:
            removed_line_count += 1
            print("🧹 [auto_closed] cleaned single-line SQL fragments containing auto_closed.")

    if modified_sql != sql:
        print(
            f"✅ [auto_closed] cleanup done. blocks={removed_block_count}, "
            f"lines/fragments={removed_line_count}, len {len(sql)} -> {len(modified_sql)}"
        )

    return modified_sql


def patch_pandas_read_sql(rewrite_python_files=False):
    """
    Patch pandas.read_sql:
    - optional .py bulk rewrite (db_connect + read_sql -> dc.query)
    - SQL cleanup for auto_closed fragments only
    """
    if rewrite_python_files:
        patch_python_files_for_dc_query()

    if hasattr(pd, "_original_read_sql"):
        print("ℹ️ pd.read_sql is already patched. Skipping re-patch.")
        return

    pd._original_read_sql = pd.read_sql

    def auto_read_sql(sql, con, **kwargs):
        modified_sql = _remove_auto_closed(sql)

        has_placeholder = bool(re.search(r"\?|:\w+", modified_sql))
        params_value = kwargs.get("params")
        params_non_empty = (
            params_value is not None
            and isinstance(params_value, (list, tuple, dict))
            and len(params_value) > 0
        )
        if not has_placeholder and params_non_empty:
            kwargs = {k: v for k, v in kwargs.items() if k != "params"}

        if hasattr(con, "query") and not hasattr(con, "cursor"):
            result = con.query(modified_sql)
            return result if isinstance(result, pd.DataFrame) else pd.DataFrame(result)

        return pd._original_read_sql(modified_sql, con, **kwargs)

    pd.read_sql = auto_read_sql
    print("🚀 Success: pd.read_sql has been patched (auto_closed cleanup only).")
    sys.stdout.flush()


def _get_dc():
    try:
        from utilities import db_util

        dc, _ = db_util.db_connect()
        return dc
    except Exception:
        return None


def patch_dc_query(dc=None):
    """
    Patch dc.query(sql):
    - SQL cleanup for auto_closed fragments only
    """
    if dc is None:
        dc = _get_dc()
    if dc is None:
        print("❌ patch_dc_query: unable to get dc.")
        return

    if hasattr(dc, "_original_query"):
        print("ℹ️ dc.query is already patched. Skipping re-patch.")
        return

    dc._original_query = dc.query

    def auto_query(sql):
        modified_sql = _remove_auto_closed(sql)
        return dc._original_query(modified_sql)

    dc.query = auto_query
    print("🚀 Success: dc.query has been patched (auto_closed cleanup only).")
    sys.stdout.flush()
