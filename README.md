def clean_col2(df, target):
    df.loc[
        (df['col1'] == target) &
        df['col2'].notna() &
        df['col3'].notna() &
        df.apply(lambda r: r['col3'] in r['col2'], axis=1),
        'col2'
    ] = df.apply(lambda r: r['col2'].replace(r['col3'], ''), axis=1)
    return df
