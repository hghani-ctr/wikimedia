SELECT
    DATE_FORMAT(event_timestamp, 'yyyy-MM-01') AS month,
    COUNT(*) AS mobile_edits
FROM wmf.mediawiki_history
WHERE
    (
        ARRAY_CONTAINS(revision_tags, 'mobile edit')
        OR ARRAY_CONTAINS(revision_tags, 'mobile app edit')
        OR ARRAY_CONTAINS(revision_tags, 'mobile web edit')
    )
    AND event_entity = 'revision'
    AND event_type = 'create'
    AND event_timestamp BETWEEN '{metrics_month_start}' AND '{metrics_month_end}'
    AND snapshot = '{mediawiki_history_snapshot}'
GROUP BY DATE_FORMAT(event_timestamp, 'yyyy-MM-01')
