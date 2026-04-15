join_pattern = (
    r"left\s+join\s*\(.*?\)\s*auto_closed\s+on\s+.*?"
    r"(?=\bleft\s+join\b|\bright\s+join\b|\binner\s+join\b|\bfull\s+join\b|"
    r"\bwhere\b|\bgroup\s+by\b|\border\s+by\b|\bhaving\b|\blimit\b|$)"
)
modified_sql = re.sub(join_pattern, " ", modified_sql, flags=re.IGNORECASE | re.DOTALL)
