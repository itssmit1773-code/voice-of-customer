WITH denominators AS (
    SELECT segment, COUNT(*) AS segment_reports,
           COUNT(DISTINCT user_id) AS segment_known_reporters
    FROM scoped GROUP BY segment
)
SELECT segment, topic, COUNT(*) AS reports,
       COUNT(DISTINCT user_id) AS known_reporters,
       COUNT(DISTINCT account_id) AS accounts,
       segment_reports, segment_known_reporters,
       1.0 * COUNT(*) / segment_reports AS report_share,
       1.0 * COUNT(DISTINCT user_id) / NULLIF(segment_known_reporters, 0) AS reporter_share
FROM scoped JOIN denominators USING (segment)
GROUP BY segment, topic
ORDER BY segment, reports DESC, topic;
