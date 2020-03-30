WITH
entry_list AS (
    SELECT m.id member_id, m.created,
        MAX(CASE WHEN a.id IS NOT NULL THEN 1 ELSE 0 END) entry_flg
    FROM jstaff.members m
        LEFT JOIN jstaff.applications a ON a.member_id = m.id
        LEFT JOIN jl_ad.hellowork_members hm ON m.id = hm.member_id
            AND DATE_DIFF('DAY', m.created, a.created) <= 90
    WHERE m.created BETWEEN '2017-04-01' AND CURRENT_DATE - 90
        AND m.media_id = 8
        AND hm.member_id IS NULL
    GROUP BY m.id, m.created
)

SELECT
    member_id, page_type,
    COUNT(DISTINCT access_id) hit,
    SUM(max_py) trajectory,
    SUM(stay_seconds) stay
FROM
    (
        SELECT el.member_id, el.entry_flg,
            CASE
                --使用カラム選択--
                WHEN al.page_type IN ('detail','entry', 'voice_compa', 'search_other', 'search_user','search_city', 'search_pref', 'search_multi','search_hello', 'login','register') THEN al.page_type
                --分割--
                WHEN al.page_type = 'edit' AND al.url LIKE '%resume%' THEN 'edit_resume'
                WHEN al.page_type = 'edit' AND al.url LIKE '%scout%' THEN 'edit_scout'
                WHEN al.page_type = 'edit' AND al.url LIKE '%hope%' THEN 'edit_hope'
                -- WHEN al.page_type = 'contents' AND al.url LIKE '%syokureki_sample%' THEN 'contents_syokureki'
                WHEN al.page_type = 'mypage' AND al.url LIKE '%consider%' THEN 'mypage_consider'
                -- WHEN al.page_type = 'mypage' AND al.url LIKE '%config%' THEN 'mypage_config'
                WHEN al.page_type = 'mypage' AND al.url LIKE '%scout%' THEN 'mypage_scout'
                WHEN al.page_type = 'mypage' AND al.url LIKE '%index%' THEN 'mypage_index'
                -- WHEN al.page_type = 'mypage' THEN 'mypage_else'
                ELSE 'else'
            END page_type,
            al.access_id,
            ess.max_py,
            LAG(al.hit_time) OVER(ORDER BY al.hit_time ASC) lag_hit_time,
            DATE_DIFF('SECOND', lag_hit_time, al.hit_time) stay_seconds
        FROM entry_list el
            INNER JOIN jl.users u ON el.member_id = u.media_user_id
            INNER JOIN jl.access_logs al ON al.user_id = u.user_id
            INNER JOIN jl.event_scroll_summaries ess ON ess.access_id = al.access_id
        WHERE DATE_DIFF('hour', el.created, al.hit_time) <= 72
        GROUP BY al.access_id, el.member_id, el.entry_flg, al.page_type, al.url, ess.max_py, al.hit_time
    )
GROUP BY member_id, entry_flg, page_type

;
