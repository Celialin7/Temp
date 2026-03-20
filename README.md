def filter_group(g):
    # 若有 0 和 1，则去掉最小值（0），保留所有 1
    if g['cola'].nunique() == 2:
        return g[g['cola'] == 1]

    # 如果所有 cola 都一样（全 1 或全 0）
    # 多行则根据 date 保留最近一行
    if len(g) > 1:
        return g.sort_values('date').iloc[-1:]   # 末行 = 最大日期

    # 单行直接返回
    return g

df_filtered = df.groupby('caseid', group_keys=False).apply(filter_group)
