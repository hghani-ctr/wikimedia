WITH quality_articles_aggregated_genders AS (
    SELECT
        content_gap,
        CASE
            -- Leave non-gender categories untouched
            WHEN (content_gap != 'gender') THEN category
            -- Aggregate gender categories
            WHEN category IN ('male', 'cisgender male') THEN 'males'
            WHEN category IN ('female', 'cisgender female') THEN 'females'
            ELSE 'gender_diverse'
        END AS category,
        TO_DATE(time_bucket) AS month,
        metrics.standard_quality_count AS quality_articles
    FROM content_gap_metrics.by_category_all_wikis
    WHERE 
        time_bucket = '{metrics_month}'
        AND content_gap IN ('gender', 'geography_wmf_region')
)
SELECT 
    category,
    month,
    SUM(quality_articles) AS quality_articles
FROM quality_articles_aggregated_genders
GROUP BY
    category,
    month
ORDER BY
    category,
    month
