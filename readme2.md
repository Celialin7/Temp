batch_size= 1_000
total_records = len (11)
total_batches = math.ceil(total_records / batch_size)
# Store each query result here
results = []
for batch_number, start in enumerate(range(0, total_records, batch_size), start-1):
# Take the next batch of up to 1,000 customer IDs
custid batch = caseid[start: start + batch_size]
# Escape single quotes before inserting values into the SQL statement
custidlist = ",".join(
f"' {customer_id.replace(chr(39), chr(39) * 2)}i
for customer id in custid_batch
