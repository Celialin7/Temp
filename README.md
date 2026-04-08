import pandas as pd
import traceback

def log_file(scenario, country_cd, Action, time, err, filename):
    """
    记录执行日志（含错误定位信息）
    最小改动原则：
    - 保留原字段和原错误映射
    - 仅增加错误类型/错误位置字段
    """
    df_log = pd.DataFrame(columns=[
        "Scenario Id",
        "Country Cd",
        "Action",
        "Time",
        "Error Description",
        "Filename",
        "Error Type",         # 新增：SQL / Python / Unknown
        "Error Class",        # 新增：异常类名
        "Error File",         # 新增：实际报错文件
        "Error Line",         # 新增：实际报错行号
        "Error Function",     # 新增：实际报错函数
        "Raw Error"           # 新增：原始错误信息
    ])

    # 1) 统一错误文本
    err_text = str(err)

    # 2) 保留你原有的错误映射逻辑
    if "Ticket expired" in err_text:
        err1 = "KERBEROS Ticket Expired"
    elif "Table not found" in err_text:
        err1 = "Table/Db not available or Permission restricted"
    elif "Scenario Id" in err_text:
        err1 = "Table/Db not available or Permission restricted"
    else:
        err1 = err_text

    # 3) 提取 traceback（如果 err 是 Exception 对象）
    err_class = type(err).__name__ if isinstance(err, BaseException) else "Unknown"
    tb_file = filename
    tb_line = None
    tb_func = None

    if isinstance(err, BaseException) and err.__traceback__ is not None:
        tb_list = traceback.extract_tb(err.__traceback__)
        if tb_list:
            last = tb_list[-1]  # 最后一层通常是实际抛错位置
            tb_file = last.filename
            tb_line = last.lineno
            tb_func = last.name

    # 4) 判断错误类型（SQL or Python）
    # 先看 Action，再看错误文本关键字
    action_text = str(Action).lower()
    err_lower = err_text.lower()
    sql_hints = [
        "sql", "read_sql", "query", "syntax error", "table not found",
        "database", "dbapi", "odbc", "hive", "presto", "trino"
    ]

    if any(k in action_text for k in ["sql", "read_sql", "query"]) or any(k in err_lower for k in sql_hints):
        err_type = "SQL"
    else:
        err_type = "Python"

    # 5) 写入日志（兼容新 pandas，不用弃用的 append）
    row = {
        "Scenario Id": scenario,
        "Country Cd": country_cd,
        "Action": Action,
        "Time": time,
        "Error Description": err1,
        "Filename": filename,      # 保留你原字段
        "Error Type": err_type,
        "Error Class": err_class,
        "Error File": tb_file,
        "Error Line": tb_line,
        "Error Function": tb_func,
        "Raw Error": err_text,
    }
    df_log.loc[len(df_log)] = row

    return df_log
