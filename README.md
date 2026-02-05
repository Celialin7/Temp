import traceback

...
        # 调用原生函数（包一层 try/except 便于定位 return 时抛出的异常）
        try:
            result = pd._original_read_sql(modified_sql, con, **kwargs)
            return result
        except Exception as e:
            # 打印异常的类型、repr、args，避免 str(e) 为空时看不到内容
            print(
                f"❌ [Auto-SQL] pd._original_read_sql 执行失败: "
                f"type={type(e).__name__}, repr={repr(e)}, args={getattr(e, 'args', None)}",
                file=sys.stderr,
            )
            # 打印连接对象信息，排查是否是连接/驱动层问题
            print(
                f"   con type={type(con)}, module={getattr(con.__class__, '__module__', '')}",
                file=sys.stderr,
            )
            # 打印 SQL 片段
            print(f"   modified_sql 前 500 字符: {modified_sql[:500]!r}", file=sys.stderr)
            # 打印完整 traceback，便于定位是驱动/DB/栈上的哪一层报的错
            traceback.print_exc()
            raise
