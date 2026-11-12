SELECT COUNT(*) AS reports,
       COUNT(DISTINCT user_id) AS known_reporters,
       COUNT(DISTINCT account_id) AS accounts,
       COUNT(*) - COUNT(user_id) AS anonymous_reports,
       SUM(needs_review) AS review_queue,
       SUM(severity = 'blocking') AS predicted_blockers
FROM scoped;
