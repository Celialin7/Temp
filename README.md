WITH branch_mapping AS (
  SELECT 'pb' AS category, 251 AS branch_code UNION ALL
  SELECT 'cmb', 288 UNION ALL
  SELECT 'digital', 300 UNION ALL
  SELECT 'rbrss', 350 UNION ALL
  SELECT 'rbvhis', 360 UNION ALL
  SELECT 'other', 400
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
)
SELECT
  p.category,
  m.branch_code,
  p.policy_number,
  CASE WHEN d.policy_number IS NOT NULL THEN 'FOUND_IN_DB'
       ELSE 'NOT_FOUND_IN_DB'
  END AS status
FROM policy_raw p
JOIN branch_mapping m USING (category)
LEFT JOIN `your_dataset.your_table` d
  ON p.policy_number = d.policy_number
  AND m.branch_code = d.branch_code
ORDER BY p.category, p.policy_number;
