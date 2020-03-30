WITH
user_list AS (
    SELECT m.id member_id, m.created
    FROM jstaff.members m
        LEFT JOIN jl_ad.hellowork_members hm ON m.id = hm.member_id
    WHERE m.created BETWEEN CURRENT_DATE - 90 AND CURRENT_DATE - 3
        AND m.media_id = 8
        AND hm.member_id IS NULL
    GROUP BY m.id, m.created
),

landing_path AS (
    SELECT u.media_user_id member_id, s.landing_page_type
    FROM jl.sessions s
        INNER JOIN jl.users u ON s.master_user_id = u.master_user_id
    WHERE s.session_num = 1
        AND u.media_user_id IN (SELECT member_id FROM user_list)
    GROUP BY u.media_user_id, s.landing_page_type
),

member_os AS (
    SELECT
        ul.member_id,
        MAX(CASE
            WHEN al.user_agent ~ 'Android.*Mobile' OR al.os = 'iPhone' THEN 'smartphone'
            WHEN al.user_agent ~ 'Android' THEN 'AndroidTablet'
            WHEN al.os ~* 'windows' THEN 'windows'
            ELSE os
        END) os
    FROM user_list ul
        INNER JOIN jl.access_logs al ON ul.member_id = al.media_user_id
    WHERE visit_num = 1
    GROUP BY ul.member_id
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
    ul.member_id,
    lp.landing_page_type,
    os.os,
    mp.pref_id,
    mo.occupation_id,
    DATE_DIFF('year', m.birthday, m.created) age,
    ms.mail_domain_type
FROM
    user_list ul
    INNER JOIN jstaff.members m ON ul.member_id = m.id
    LEFT JOIN landing_path lp ON ul.member_id = lp.member_id
    LEFT JOIN member_os os ON ul.member_id = os.member_id
    LEFT JOIN (
        SELECT member_id, pref_id, RANK() OVER(PARTITION BY member_id ORDER BY id ASC) rank
        FROM jstaff.member_locations
    ) mp ON mp.member_id = ul.member_id AND mp.rank = 1
    LEFT JOIN jstaff.member_occupations mo ON ul.member_id = mo.member_id AND mo.rank = 1
    LEFT JOIN member_states ms ON ul.member_id = ms.member_id
;
