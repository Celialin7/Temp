import pandas as pd
import numpy as np

# 假设 comparison_map, mws, crt 已经定义

# 1. Fix OCR: set_index, reindex 拼写错误
df1 = mws.set_index('Customer_ID')
# 确保 df2 和 df1 的 index 完全对齐
df2 = crt.set_index('Customer_ID').reindex(df1.index)

output1 = pd.DataFrame(index=df1.index)
final_col_order = ['Customer_ID'] # 建议保留ID在最前

for df1_col, df2_cols in comparison_map.items():
    # 2. Fix Logic: 单个字符串用 append，列表用 extend
    final_col_order.append(df1_col)
    final_col_order.extend(df2_cols)
    
    # 3. Smart Merge Logic (Miss Check):
    # 逻辑：如果列里的值只包含 空格、横杠(-)、下划线(_)，或者本来就是空，替换为 NaN
    # 然后检查是否这一行全是 NaN
    indicator_col_miss = f'miss_{df1_col}'
    
    # 这一行代码替代了你原本复杂的 np.where 和 lambda
    is_row_empty = df2[df2_cols].astype(str).replace(r'^[-_\s]*$', np.nan, regex=True).isna().all(axis=1)
    # 注意：astype(str) 会把原本的 NaN 变成 'nan'，所以我们要额外把字符串 'nan' 也视为缺失，或者更严谨点只处理非 NaN 值
    # 更稳妥的写法（不强制转 str 以保留原始 NaN）：
    # is_row_empty = df2[df2_cols].replace(r'^[-_\s]*$', np.nan, regex=True).isna().all(axis=1)
    
    output1[indicator_col_miss] = np.where(is_row_empty, 'Y', 'N')
    final_col_order.append(indicator_col_miss)

    for df2_col in df2_cols:
        indicator_col_name = f'match_{df1_col}_vs_{df2_col}'
        # Fix: 确保比较时都是字符串并转大写，处理 NaN 防止报错
        val1 = df1[df1_col].astype(str).str.upper().replace('NAN', '')
        val2 = df2[df2_col].astype(str).str.upper().replace('NAN', '')
        
        output1[indicator_col_name] = (val1 == val2).astype(int)
        final_col_order.append(indicator_col_name)

# 4. Fix Merge: 修正了原来混乱的 merge 语法，直接用 concat 更简单（因为 index 已经对齐）
# 将原始数据 df1, df2 和 结果 output1 横向拼接
output2 = pd.concat([df1, df2, output1], axis=1).reset_index()

# 筛选最终列顺序 (过滤掉可能不存在的列名以防万一)
output2 = output2[[c for c in final_col_order if c in output2.columns]]

print(output2.columns)
output2.head()
