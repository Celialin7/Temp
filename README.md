def keep_latest_one(df):
    def pick(g):
        # Step 1: 只保留 cola=1 的
        g1 = g[g['cola'] == 1]

        # Step 2: 如果没有 1，则返回空（或返回最早的 0，看你需求）
        if g1.empty:
            return g.iloc[0:0]   # 返回空 DF，不会引发错误

        # Step 3: 如果只有一行 1，直接返回
        if len(g1) == 1:
            return g1

        # Step 4: 超过一行 1，取最新 date
        return g1.sort_values('date').tail(1)

    return df.groupby('caseid', group_keys=False).apply(pick)
