WITH topics AS (
    SELECT DISTINCT topic FROM scoped
), counts AS (
    SELECT month, topic, COUNT(*) AS reports
    FROM scoped GROUP BY month, topic
), totals AS (
    SELECT month, COUNT(*) AS total_reports
    FROM scoped GROUP BY month
)
SELECT month, topic, COALESCE(reports, 0) AS reports, total_reports,
       1.0 * COALESCE(reports, 0) / total_reports AS report_share
FROM totals CROSS JOIN topics LEFT JOIN counts USING (month, topic)
ORDER BY month, topic;
