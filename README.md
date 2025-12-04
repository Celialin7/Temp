for idx, col_name in enumerate(st.session_state.final_df.columns):
            if col_name in mws_cols:
                # 写入(行, 列, 内容, 格式) -> MWS 是蓝色
                worksheet.write(0, idx, col_name, blue_fmt)
            elif col_name in crt_cols:
                # CRT 是粉色
                worksheet.write(0, idx, col_name, pink_fmt)
            else:
                # 其他生成的列（比如 match_xxx, fuzzy_score）保持默认样式
                worksheet.write(0, idx, col_name, default_fmt)
