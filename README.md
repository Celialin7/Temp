(print(f"QC -> A: {a} | B: {b} | SCORE: {(s := fuzz.token_set_ratio(str(a), str(b)))}") or s)
