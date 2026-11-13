def run_batch(ids, batch_size=1000, tag=""):
    total_records = len(ids)
    total_batches = math.ceil(total_records / batch_size)
    results = []
    for batch_number, start in enumerate(range(0, total_records, batch_size), start=1):
        custid_batch = ids[start:start + batch_size]
        custidlist = ",".join(
            f"'{cid.replace(chr(39), chr(39)*2)}'"
            for cid in custid_batch
        )
        # 你的 SQL 查询...
        # rows = query(...)
        # results.extend(rows)
        print(f"[{tag}] batch {batch_number}/{total_batches}, start={start}, size={len(custid_batch)}")
    return results
