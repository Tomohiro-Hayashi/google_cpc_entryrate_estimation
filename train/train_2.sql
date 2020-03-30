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
),

landing_path AS (
    SELECT u.media_user_id member_id, s.landing_page_type
    FROM jl.sessions s
        INNER JOIN jl.users u ON s.master_user_id = u.master_user_id
    WHERE s.session_num = 1
        AND u.media_user_id IN (SELECT member_id FROM entry_list)
    GROUP BY u.media_user_id, s.landing_page_type
),

member_os AS (
    SELECT
        el.member_id,
        MAX(CASE
            WHEN al.user_agent ~ 'Android.*Mobile' OR al.os = 'iPhone' THEN 'smartphone'
            WHEN al.user_agent ~ 'Android' THEN 'AndroidTablet'
            WHEN al.os ~* 'windows' THEN 'windows'
            ELSE os
        END) os
    FROM entry_list el
        INNER JOIN jl.access_logs al ON el.member_id = al.media_user_id
    WHERE visit_num = 1
    GROUP BY el.member_id
),

member_states AS (
    SELECT member_id,
        CASE
            WHEN mail_domain LIKE '%gmail%' THEN 'gmail'
            WHEN mail_domain LIKE '%yahoo%' THEN 'yahoo'
            WHEN mail_domain LIKE '%ezweb%' THEN 'ezweb'
            WHEN mail_domain LIKE '%icloud%' THEN 'icloud'
            WHEN mail_domain LIKE '%softbank%' THEN 'softbank'
            WHEN mail_domain LIKE '%docomo%' THEN 'docomo'
            ELSE 'other'
        END mail_domain_type
    FROM jl_ad.member_states
)

SELECT
    el.member_id, el.entry_flg,
    lp.landing_page_type,
    os.os,
    mp.pref_id,
    mo.occupation_id,
    DATE_DIFF('year', m.birthday, m.created) age,
    ms.mail_domain_type
FROM
    entry_list el
    INNER JOIN jstaff.members m ON el.member_id = m.id
    LEFT JOIN landing_path lp ON el.member_id = lp.member_id
    LEFT JOIN member_os os ON el.member_id = os.member_id
    LEFT JOIN (
        SELECT member_id, pref_id, RANK() OVER(PARTITION BY member_id ORDER BY id ASC) rank
        FROM jstaff.member_locations
    ) mp ON mp.member_id = el.member_id AND mp.rank = 1
    LEFT JOIN jstaff.member_occupations mo ON el.member_id = mo.member_id AND mo.rank = 1
    LEFT JOIN member_states ms ON el.member_id = ms.member_id
;
