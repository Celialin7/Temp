WITH category_mapping AS (
  SELECT 'pb' AS category, 251 AS branch_code,
    -- 👇 这里粘贴 pb 的 policy numbers
    ['P001','P002','P003'] AS policy_list

  UNION ALL
  SELECT 'cmb', 288,
    -- 👇 CMB 的 policy list
    ['C101','C102','C103']

  UNION ALL
  SELECT 'digital', 300,
    -- 👇 Digital 的 policy list
    ['D201','D202']

  UNION ALL
  SELECT 'rbrss', 350,
    -- 👇 rbrss 的 policy list
    ['R401','R402']

  UNION ALL
  SELECT 'rbvhis', 360,
    -- 👇 rbvhis 的 policy list
    ['V501','V502','V503']

  UNION ALL
  SELECT 'other', 400,
    -- 👇 第六类的 policy list
    ['O601','O602']
),

-- 展开数组为行
policy_expanded AS (
  SELECT
    category,
    branch_code,
    policy AS policy_number
  FROM category_mapping,
  UNNEST(policy_list) AS policy
)

-- 与数据库关联并找差异
SELECT
  p.category,
  p.branch_code,
  p.policy_number,
  CASE
    WHEN d.policy_number IS NOT NULL THEN 'FOUND_IN_DB'
    ELSE 'NOT_FOUND_IN_DB'
  END AS status
FROM policy_expanded p
LEFT JOIN `your_dataset.your_table` d
  ON p.policy_number = d.policy_number
  AND p.branch_code = d.branch_code
ORDER BY category, policy_number;
