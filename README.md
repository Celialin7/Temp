
def clean_columns(df, target_value):
    def remove_substrings(row):
        # 只处理 col1 == target_value 的行
        if row['col1'] != target_value:
            return row['col2']
        
        out = row['col2']
        for c in ['col3', 'col4']:
            if pd.notna(row[c]) and isinstance(out, str) and row[c] in out:
                out = out.replace(row[c], '')
        return out
    
    df['col2'] = df.apply(remove_substrings, axis=1)
    return df
