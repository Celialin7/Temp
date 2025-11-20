miss_counts = (final_result.filter(like='is_missing_') == 'Y').sum()
match_counts = (final_result.filter(like='match_') == 0).sum()
report_df = pd.concat([
    miss_counts.rename('Issue_Count').to_frame().assign(Check_Type='Completeness (Missing)'),
    match_counts.rename('Issue_Count').to_frame().assign(Check_Type='Accuracy (Mismatch)')
]).reset_index().rename(columns={'index': 'Column_Name'})

report_df = report_df.sort_values(by='Issue_Count', ascending=False)

print("--- Data Quality Summary Report ---")
print(report_df)
