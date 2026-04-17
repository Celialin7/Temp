
pattern_block = r"(?is)left\s+join(?:(?!left\s+join).)*?\)\s*auto_closed"
modified_sql = re.sub(pattern_block, "", modified_sql)

pattern_line = r"(?im)^.*?\bauto_closed\b.*?$\n?"
modified_sql = re.sub(pattern_line, "", modified_sql)
