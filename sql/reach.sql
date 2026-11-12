SELECT topic, COUNT(DISTINCT user_id) AS observed_reporters,
       COUNT(DISTINCT account_id) AS observed_accounts,
       COUNT(*) AS reports, SUM(user_id IS NULL) AS anonymous_reports
FROM scoped
WHERE topic NOT IN ('review', 'other')
GROUP BY topic;
