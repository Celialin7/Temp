import pandas as pd

# 假设你的 DataFrame 叫 df，那一列叫 'content'
# 这里是一个简单的正则逻辑：
# 1. ((?:\d{4}/)?\d{1,2}/\d{1,2} ... ) : 匹配日期 (2025/07/07 或 07/07) + 可选的时间
# 2. [\s\S]*? : 匹配后面的任意文字(非贪婪模式)
# 3. (?= ... |$) : 这是一个“断言”，意思是直到看见“下一个日期”或者“字符串结尾”才停止
pattern = r'((?:\d{4}/)?\d{1,2}/\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?[\s\S]*?)(?=(?:\d{4}/)?\d{1,2}/\d{1,2}|$)'

# 一行代码实现：查找所有匹配段 -> 转成列表 -> 变成 DataFrame -> 自动对齐索引
split_df = pd.DataFrame(df['content'].str.findall(pattern).tolist(), index=df.index)

# (可选) 给新列重命名，比如 col_0, col_1...
split_df = split_df.add_prefix('segment_')

# 将结果合并回原表
df_final = pd.concat([df, split_df], axis=1)

# 打印查看结果
print(df_final)
