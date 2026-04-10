WITH branch_mapping AS (
  SELECT 'pb' AS category, [251] AS branch_codes UNION ALL
  SELECT 'cmb', [288] UNION ALL
  SELECT 'digital', [300] UNION ALL
  SELECT 'rbrss', [350, 351, 352] UNION ALL
  SELECT 'rbvhis', [360] UNION ALL
  SELECT 'other', [400]
),
policy_raw AS (
  SELECT 'pb' AS category, policy_number FROM UNNEST([
    -- pb list
  ]) AS policy_number UNION ALL
  SELECT 'cmb', policy_number FROM UNNEST([
    -- cmb list
  ]) AS policy_number UNION ALL
  SELECT 'digital', policy_number FROM UNNEST([
    -- digital list
  ]) AS policy_number UNION ALL
  SELECT 'rbrss', policy_number FROM UNNEST([
    -- rbrss list
  ]) AS policy_number UNION ALL
  SELECT 'rbvhis', policy_number FROM UNNEST([
    -- rbvhis list
  ]) AS policy_number UNION ALL
  SELECT 'other', policy_number FROM UNNEST([
    -- other list
  ]) AS policy_number
),
expanded_branch AS (
  SELECT category, b AS branch_code
  FROM branch_mapping, UNNEST(branch_codes) AS b
),
db_data AS (
  SELECT
    d.policy_number,
    d.branch_code
  FROM `your_dataset.your_table` d
  JOIN expanded_branch eb
    ON d.branch_code = eb.branch_code
)

SELECT
  COALESCE(p.category, eb.category) AS category,
  COALESCE(p.policy_number, d.policy_number) AS policy_number,
  COALESCE(d.branch_code, eb.branch_code) AS branch_code,
  CASE
    WHEN p.policy_number IS NOT NULL AND d.policy_number IS NOT NULL THEN 'FOUND_IN_DB'
    WHEN p.policy_number IS NOT NULL AND d.policy_number IS NULL THEN 'NOT_FOUND_IN_DB'
    WHEN p.policy_number IS NULL AND d.policy_number IS NOT NULL THEN 'EXTRA_IN_DB'
  END AS status
FROM policy_raw p
FULL OUTER JOIN expanded_branch eb
  ON p.category = eb.category
FULL OUTER JOIN db_data d
  ON p.policy_number = d.policy_number
  AND eb.branch_code = d.branch_code
ORDER BY category, policy_number;
