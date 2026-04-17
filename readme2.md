join_pattern = (
    r"left\s+join\b[\s\S]*?\)\s*(?:as\s+)?auto_closed\s+on\b[\s\S]*?"
    r"(?=\bleft\s+join\b|\bright\s+join\b|\binner\s+join\b|\bfull\s+join\b|"
    r"\bwhere\b|\bgroup\s+by\b|\border\s+by\b|\bhaving\b|\blimit\b|$)"
)
