df['a_clean'] = df['col_a'].astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)
df['b_clean'] = df['col_b'].astype(str).str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)


df['newcol'] = [
    'Y' if (a == b) or (a in b) or (b in a) or (fuzz.ratio(a, b) > 80) else 'N'
    for a, b in zip(df['a_clean'], df['b_clean'])
]
