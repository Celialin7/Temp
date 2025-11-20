output1[fuzzy_score_col] = [
               
                (print(f"QC -> ID: {pid} | A: {a} | B: {b} | SCORE: {fuzz.token_set_ratio(str(a), str(b))}") or fuzz.token_set_ratio(str(a), str(b)))              
                for a, b, pid in zip(
                    df1[df1_col].astype(str).str.lower().str.replace(r'[,#.!]', '', regex=True),
                    df2[df2_col].astype(str).str.lower().str.replace(r'[,#.!]', '', regex=True),
                    df1.index  # <--- 【关键修改】把 party_id (即索引) 加进来一起循环
                )
            ]
