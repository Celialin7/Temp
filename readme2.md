import pandas as pd
import numpy as np

# ==========================================
# 1. 模拟数据 (这一步是为了证明代码能处理脏数据，你实际使用时请替换为你的读取代码)
# ==========================================
data = {
    'col1': ['2025-02-01', '2025-05-01', 'N/A', '2025-01-20', '2025-12-31'], # 结束日期 (包含脏数据)
    'col2': ['2025-01-01', '2025-04-01', '2025-01-01', pd.NaT, '2025-12-01'], # 开始日期 (包含NaT)
    'col3': ['No', 'Yes', 'No', 'No - check', 'No'] # 包含 'No' 的列
}
comp = pd.DataFrame(data)

# ==========================================
# 2. 定义 2025 澳门假期 (硬编码，最稳)
# ==========================================
macau_2025_holidays = [
    '2025-01-01', '2025-01-29', '2025-01-30', '2025-01-31', '2025-04-04', 
    '2025-04-18', '2025-04-19', '2025-05-01', '2025-05-05', '2025-05-31', 
    '2025-10-01', '2025-10-02', '2025-10-07', '2025-10-29', '2025-11-02', 
    '2025-12-08', '2025-12-20', '2025-12-21', '2025-12-24', '2025-12-25'
]
# 关键：必须转为 numpy 的 datetime64[D] 格式
holidays_np = np.array(macau_2025_holidays, dtype='datetime64[D]')

# ==========================================
# 3. 数据清洗与预处理 (防报错的核心)
# ==========================================
# 3.1 强制转为 datetime，错误变成 NaT
comp['col1'] = pd.to_datetime(comp['col1'], errors='coerce')
comp['col2'] = pd.to_datetime(comp['col2'], errors='coerce')

# 3.2 【新增关键步骤】去时区 + 去时间 (只保留日期)
# 这一步能防止 Numpy 在转换类型时因为时区问题报错，也能规避很多 NaT 相关的怪异行为
comp['col1'] = comp['col1'].dt.tz_localize(None).dt.normalize()
comp['col2'] = comp['col2'].dt.tz_localize(None).dt.normalize()

# ==========================================
# 4. 计算工作日 (Numpy 逻辑)
# ==========================================
# 4.1 创建掩码：只有两个日期都不是 NaT 的行，才是有效行
valid_mask = comp['col1'].notna() & comp['col2'].notna()

# 4.2 初始化结果列 (默认为 NaN)
comp['business_days_diff'] = np.nan

# 4.3 只对有效行进行计算
# 这一步保证了传入 np.busday_count 的数组里绝对没有 NaT
if valid_mask.any():
    # 提取有效数据并转为 numpy 数组
    start_dates = comp.loc[valid_mask, 'col2'].values.astype('datetime64[D]')
    end_dates = comp.loc[valid_mask, 'col1'].values.astype('datetime64[D]')
    
    # 计算并将结果填回对应的行
    comp.loc[valid_mask, 'business_days_diff'] = np.busday_count(
        start_dates, 
        end_dates, 
        weekmask='1111100', 
        holidays=holidays_np
    )

# ==========================================
# 5. 生成 Exception (符合你的业务逻辑)
# ==========================================
# 逻辑：(天数差 > 10) AND (col3 包含 'No')
# fillna(0) 是为了防止 business_days_diff 为 NaN 时比较报错
# na=False 是为了防止 col3 为 NaN 时报错
exception_condition = (comp['business_days_diff'].fillna(0) > 10) & \
                      (comp['col3'].astype(str).str.contains('No', case=False, na=False))

comp['S1_Exception'] = np.where(exception_condition, 'exception', '')

# ==========================================
# 6. 验证输出
# ==========================================
print("代码运行成功，未报错。结果如下：")
print(comp[['col2', 'col1', 'col3', 'business_days_diff', 'S1_Exception']])
