def clean_cols(df, target_value):
    """
    对 col1 == target_value 的行进行处理：
    col2 中如果包含 col3，则去掉；
    col2 中如果包含 col4，也去掉。
    """
    def process_row(row):
        if row['col1'] != target_value:
            return row['col2']   # 不处理

        out = row['col2']

        # 去掉 col3
        if pd.notna(row['col3']) and row['col3'] in out:
            out = out.replace(row['col3'], '')

        # 去掉 col4
        if pd.notna(row['col4']) and row['col4'] in out:
            out = out.replace(row['col4'], '')

        return out

    df['col2'] = df.apply(process_row, axis=1)
    return df
