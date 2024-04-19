WITH wikipedia_dbs AS (
    SELECT database_code
    FROM canonical_data.wikis
    WHERE database_group = 'wikipedia'
),
quality_articles_aggregated_genders AS (
    SELECT
        c.wiki_db,
        c.content_gap,
        CASE
            -- Leave non-gender categories untouched
            WHEN (c.content_gap != 'gender') THEN c.category
            -- Aggregate gender categories
            WHEN c.category IN ('male', 'cisgender male') THEN 'males'
            WHEN c.category IN ('female', 'cisgender female') THEN 'females'
            ELSE 'gender_diverse'
        END AS category,
        TO_DATE(c.time_bucket) AS month,
        c.metrics.standard_quality_count AS quality_articles
    FROM content_gap_metrics.by_category c
    INNER JOIN wikipedia_dbs w ON c.wiki_db = w.database_code
    WHERE 
        c.time_bucket = '{metrics_month}'
        AND c.content_gap IN ('gender', 'geography_wmf_region')
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