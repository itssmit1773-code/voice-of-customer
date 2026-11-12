SELECT topic,
       COUNT(*) AS reports,
       ROUND(1.0 * COUNT(*) / (SELECT COUNT(*) FROM scoped), 5) AS report_share,
       COUNT(DISTINCT user_id) AS known_reporters,
       COUNT(DISTINCT account_id) AS accounts,
       SUM(user_id IS NULL) AS anonymous_reports,
       SUM(severity = 'blocking') AS predicted_blockers,
       SUM(severity = 'review') AS unknown_severity,
       SUM(sentiment = 'negative') AS predicted_negative
FROM scoped
GROUP BY topic
ORDER BY reports DESC, topic;
