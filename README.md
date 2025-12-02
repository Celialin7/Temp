def clean_cols(df, target_value):
    df['col2'] = df.apply(lambda r: r['col2']
                          .replace(r['col3'] if pd.notna(r['col3']) else '', '')
                          .replace(r['col4'] if pd.notna(r['col4']) else '', '')
                          if r['col1'] == target_value else r['col2'], axis=1)
    return df
