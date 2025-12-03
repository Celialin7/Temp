# ------------------------------
# TABS CREATION
# ------------------------------
tab1, tab2 = st.tabs(["Preview", "Analysis"])

# ------------------------------
# TAB 1: PREVIEW
# ------------------------------
with tab1:
    if st.session_state.mws is not None and st.session_state.crt is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("MWS (Top 5)")
            st.dataframe(st.session_state.mws.head())
        with c2:
            st.subheader("CRT (Top 5)")
            st.dataframe(st.session_state.crt.head())
    else:
        st.info("Please upload both MWS and CRT files to see the preview.")

# ------------------------------
# TAB 2: ANALYSIS
# ------------------------------
with tab2:
    # 只有当文件都上传了才显示运行按钮
    if st.session_state.mws is not None and st.session_state.crt is not None:
        
        if st.button("Run Analysis"):
            with st.spinner("Processing data..."):
                try:
                    # 1. 从 session_state 获取数据 (使用 copy 防止修改原始上传数据)
                    mws = st.session_state.mws.copy()
                    crt = st.session_state.crt.copy()

                    # 2. 读取外部 Mapping 文件 (修正了路径格式)
                    # 注意：确保这个路径在运行 streamlit 的电脑上是真实存在的
                    base_path = r'C:\Users\44108136\Documents\Jupyter_Code\2025\4_WCO HK\1_documentation\\'
                    
                    ctymap = pd.read_excel(base_path + 'Country Code Mapping Table.xlsx', sheet_name='Country_vs_Country Cc')
                    ctymap = ctymap.drop_duplicates().rename(columns={'Country': 'Country_Residence'})

                    # 3. 执行你的分析逻辑
                    # Rename CRT column first
                    crt = crt.rename(columns={'Customer Number': 'Customer_ID'})

                    # Filter: Keep CRT rows where ID exists in MWS
                    # 增加 .astype(str) 以防 ID 是数字格式导致报错
                    valid_ids = mws['Customer_ID'].astype(str).str.strip()
                    crt = crt[crt['Customer_ID'].astype(str).str.strip().isin(valid_ids)]

                    # Merge with Country Map
                    crt = crt.merge(
                        ctymap, 
                        left_on='Country Of Residency', 
                        right_on='Group Country Code', 
                        how='left'
                    )

                    # Clean Risk Rating
                    if 'Risk Rating' in crt.columns:
                        crt['Risk Rating'] = crt['Risk Rating'].astype(str).str.upper().replace({'LOW': 'L'})

                    # 4. 将结果存回 session_state 以便后续使用或导出
                    st.session_state.final_df = crt
                    
                    st.success(f"Analysis complete! Result shape: {crt.shape}")
                    st.dataframe(crt.head())

                except Exception as e:
                    st.error(f"Analysis failed: {e}")
    else:
        st.warning("Please upload files in the 'Upload' section first.")
