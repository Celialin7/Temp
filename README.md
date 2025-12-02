df['col1'] = df.apply(
    lambda r: r['col1']
        .replace(r['col2'], '') if pd.notna(r['col2']) and r['col2'] in r['col1'] else r['col1'],
    axis=1
)

df['col1'] = df.apply(
    lambda r: r['col1']
        .replace(r['col3'], '') if pd.notna(r['col3']) and r['col3'] in r['col1'] else r['col1'],
    axis=1
)
