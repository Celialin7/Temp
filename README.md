output1[fuzzy_score_col] = [
                # ↓↓↓↓↓↓↓↓↓↓ 临时 QC 修改行 (兼容所有 Python 版本) ↓↓↓↓↓↓↓↓↓↓
                # 原理：print 返回 None，None or X 会返回 X。所以既打印了日志，又存入了数据。
                (print(f"QC -> A: {a} | B: {b} | SCORE: {fuzz.token_set_ratio(str(a), str(b))}") or fuzz.token_set_ratio(str(a), str(b)))
                # ↑↑↑↑↑↑↑↑↑↑ 检查完后，删掉这一行，换回 fuzz.token_set_ratio(str(a), str(b)) 即可 ↑↑↑↑↑↑↑↑↑↑
                
                for a, b in zip(
                    df1[df1_col].astype(str).str.lower().str.replace(r'[,#.!]', '', regex=True),
                    df2[df2_col].astype(str).str.lower().str.replace(r'[,#.!]', '', regex=True)
                )
            ]
