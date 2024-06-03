SELECT
    CONCAT(year, '-', LPAD(month, 2, '0'), '-01') AS month,
    SUM(IF(referer_class = 'internal', view_count, 0)) AS internal_view_count,
    SUM(IF(referer_class = 'none', view_count, 0)) AS none_view_count,
    SUM(IF(referer_class = 'external (search engine)', view_count, 0)) AS search_engine_view_count,
    0 AS `internal_data_loss_%`,
    0 AS `none_data_loss_%`,
    0 AS `search_engine_loss_%`,
    SUM(IF(referer_class = 'internal', view_count, 0)) AS corrected_internal_view_count,
    SUM(IF(referer_class = 'none', view_count, 0)) AS corrected_none_view_count,
    SUM(IF(referer_class = 'external (search engine)', view_count, 0)) AS corrected_search_engine_view_count
FROM
    wmf.projectview_hourly
WHERE
    year = '{metrics_year}'
    AND month = '{metrics_cur_month}'
    AND agent_type IN ('user', 'automated')
GROUP BY
    CONCAT(year, '-', LPAD(month, 2, '0'), '-01')
ORDER BY
    month
