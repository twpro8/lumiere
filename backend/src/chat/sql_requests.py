from sqlalchemy import text

get_all_chats_sql = text("""
    SELECT DISTINCT ON (chats.id)
    chats.id,
    chats.updated_at,
    is_archived,
    description,
    owner_id,
    chats.created_at,
    chats.type,
    CASE
        WHEN chats.type = 'private' THEN u.name
        ELSE chats.name
    END AS name,
    CASE
        WHEN chats.type = 'private' THEN u.avatar_url
        ELSE chats.image_url
    END AS image_url
FROM chats
JOIN chat_members cm ON cm.chat_id = chats.id
    AND cm.user_id = :user_id
LEFT JOIN chat_members cc ON cc.chat_id = chats.id
    AND cc.user_id != :user_id
    AND chats.type = 'private'
LEFT JOIN users u ON u.id = cc.user_id
LIMIT :limit
OFFSET :offset
""")
