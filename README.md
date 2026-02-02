# db_util.py

from dataconnect import DC   # 你实际使用的库，根据你的情况修改

class DummyCursor:
    """为了兼容旧代码而包装实际的 DC 连接"""
    def __init__(self, conn):
        self.conn = conn

    def execute(self, sql, params=None):
        # 适配 DC 接口：假设 DC 的执行方法是 run(sql)
        # 如果不是 run()，你告诉我实际方法名即可
        if params:
            return self.conn.run(sql, params)
        return self.conn.run(sql)

    def fetchall(self):
        # 适配 DC 查询结果
        return self.conn.fetchall()

    def fetchone(self):
        return self.conn.fetchone()


def db_connect():
    """不改旧代码的前提下，返回 conn 和 cursor"""
    conn = DC('cops', 'prod')   # 你简化后的连接方式
    cursor = DummyCursor(conn)
    return conn, cursor
