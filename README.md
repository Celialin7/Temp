match_counts = pd.Series({
    f'match_{d1}_vs_{d2}': ((output3[f'match_{d1}_vs_{d2}'] == 0) & (output3[f'is_missing_{d1}'] != 'Y')).sum()
    for d1, d2_list in comparison_map.items() 
    for d2 in d2_list
})
