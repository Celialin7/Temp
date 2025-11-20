for df2_col in df2_cols:
        # --- 1. 先做默认的精确匹配 (作为基础) ---
        indicator_col_name = f'match_{df1_col}_vs_{df2_col}'
        output1[indicator_col_name] = (df1[df1_col] == df2[df2_col]).astype(int)
        final_col_order.append(indicator_col_name)

        # --- 2. 【核心修改】针对 Address 和 Employer_name 的特殊处理 ---
        if df1_col in ['Residential_address', 'Employer_name']:
            
            # 为了代码复用和效率，先生成处理后的临时列表 (去标点、转小写)
            norm_a_list = df1[df1_col].astype(str).str.lower().str.replace(r'[,#.!]', '', regex=True)
            norm_b_list = df2[df2_col].astype(str).str.lower().str.replace(r'[,#.!]', '', regex=True)
            
            # 【需求 1 实现】更新 Match Indicator
            # 逻辑：如果 A等于B 或 A包含B 或 B包含A，则结果为 1，否则为 0
            output1[indicator_col_name] = [
                1 if (a == b) or (a in b) or (b in a) else 0
                for a, b in zip(norm_a_list, norm_b_list)
            ]

            # 【需求 2 实现】计算 Fuzzy Score (Employer_name 也适用)
            fuzzy_score_col = f'fuzzy_score_{df1_col}_vs_{df2_col}'
            
            output1[fuzzy_score_col] = [
                # 保留你的 QC print 逻辑，复用上面处理好的 norm_a/b_list
                (print(f"QC -> ID: {pid} | A: {a} | B: {b} | SCORE: {fuzz.token_set_ratio(str(a), str(b))}") or fuzz.token_set_ratio(str(a), str(b)))
                
                for a, b, pid in zip(norm_a_list, norm_b_list, df1.index)
            ]
            
            final_col_order.append(fuzzy_score_col)
