WITH active_editors_summary AS (
    SELECT
        month,
        wikimedia_region,
        SUM(
            IF(
                activity_level IN ('5 to 99', '100 or more'),
                namespace_zero_distinct_editors,
                0
            )
        ) AS active_editors
    FROM
        wmf.unique_editors_by_country_monthly uem
    LEFT JOIN
        canonical_data.countries cdc
    ON
        uem.country_code = cdc.iso_code
    WHERE
        users_are_anonymous = FALSE
        AND month = '{metrics_month}'
        AND wikimedia_region IS NOT NULL
        AND wikimedia_region != ''
    GROUP BY
        month,
        wikimedia_region
)
SELECT
    month,
    SUM(IF(wikimedia_region = 'Central & Eastern Europe & Central Asia', active_editors, 0)) AS `Central & Eastern Europe & Central Asia`,
    SUM(IF(wikimedia_region = 'East, Southeast Asia, & Pacific', active_editors, 0)) AS `East, Southeast Asia, & Pacific`,
    SUM(IF(wikimedia_region = 'Latin America & Caribbean', active_editors, 0)) AS `Latin America & Caribbean`,
    SUM(IF(wikimedia_region = 'Middle East & North Africa', active_editors, 0)) AS `Middle East & North Africa`,
    SUM(IF(wikimedia_region = 'North America', active_editors, 0)) AS `North America`,
    SUM(IF(wikimedia_region = 'Northern & Western Europe', active_editors, 0)) AS `Northern & Western Europe`,
    SUM(IF(wikimedia_region = 'South Asia', active_editors, 0)) AS `South Asia`,
    SUM(IF(wikimedia_region = 'Sub-Saharan Africa', active_editors, 0)) AS `Sub-Saharan Africa`
FROM
    active_editors_summary
GROUP BY
    month
ORDER BY
    month;
