join_pattern = (
    r"\bleft\s+join\s*\(.*?\)\s*(?:as\s+)?auto_closed\b"
    r"\s+on\b.*?"
    r"(?=\bleft\s+join\b|\bright\s+join\b|\binner\s+join\b|\bfull\s+join\b|\bwhere\b|\bgroup\s+by\b|\border\s+by\b|\bhaving\b|\blimit\b|$)"
)
