ADD_WORD = """
    DECLARE $chat_id AS Int64;
    DECLARE $word AS Utf8;
    UPSERT INTO words (
        chat_id,
        word,
        created_at,
        updated_at,
        repeat_at,
        repetition
    ) VALUES
    (
        $chat_id,
        $word,
        CurrentUtcDatetime(),
        CurrentUtcDatetime(),
        CurrentUtcDatetime(),
        0
    );
    """

UPSERT_WORD = """
    DECLARE $chat_id AS Int64;
    DECLARE $word AS Utf8;
    DECLARE $repetition AS Uint32;
    DECLARE $repeat_after AS Int32;
    UPSERT INTO words (
        chat_id,
        word,
        updated_at,
        repeat_at,
        repetition
    ) VALUES
    (
        $chat_id,
        $word,
        CurrentUtcDatetime(),
        CurrentUtcDatetime() + DateTime::IntervalFromDays($repeat_after),
        $repetition
    );
    """

DELETE_WORD = """
        DECLARE $chat_id AS Int64;
        DECLARE $word AS Utf8;
        DELETE FROM words WHERE chat_id = $chat_id and word ILIKE $word;
        """
GET_USERS = """
        SELECT
            chat_id,
        FROM users
        ;
        """


RIPE_WORDS_BY_USER = """
        DECLARE $max_repetition AS Int64;
        DECLARE $chat_id AS Int64;
        DECLARE $limit AS Uint32;
        $format = DateTime::Format("%Y-%m-%d");
        SELECT
            word,
            chat_id,
            repetition,
        FROM words
        WHERE
            repeat_at <= CurrentUtcDatetime()
            AND
            repetition < $max_repetition
            AND 
            chat_id = $chat_id
        ORDER BY
            repetition desc
        LIMIT $limit
        ;
        """

ADD_USER = """
    DECLARE $chat_id AS Int64;
    DECLARE $username AS Utf8;
    UPSERT INTO users (
        chat_id,
        username,
        created_at
    ) VALUES
    (
        $chat_id,
        $username,
        CurrentUtcDatetime()
    );
    """

GET_WORD = """
        DECLARE $chat_id AS Int64;
        DECLARE $word AS Utf8;
        SELECT
            word,
            chat_id,
            repetition,
        FROM words
        WHERE
            word ILIKE $word
            AND
            chat_id = $chat_id
        ;
        """

GET_REPEAT_WORDS_COUNT = """
        DECLARE $max_repetition AS Int64;
        DECLARE $chat_id AS Int64;
        $format = DateTime::Format("%Y-%m-%d");
        SELECT
            count(word) as words
        FROM words
        WHERE
            repeat_at <= CurrentUtcDatetime()
            AND
            repetition < $max_repetition
            AND 
            repetition > 0
            AND
            chat_id = $chat_id
        ;
        """

GET_LEARNED_WORDS_COUNT = """
        DECLARE $max_repetition AS Int64;
        DECLARE $chat_id AS Int64;
        SELECT
            count(word) as words
        FROM words
        WHERE
            repetition >= $max_repetition
            AND 
            chat_id = $chat_id
        ;
        """

GET_IN_PROGRESS_COUNT = """
        DECLARE $max_repetition AS Int64;
        DECLARE $chat_id AS Int64;
        SELECT
            count(word) as words
        FROM words
        WHERE
            repetition < $max_repetition
            AND
            repetition > 0
            AND 
            chat_id = $chat_id
        ;
        """

GET_NEW_WORDS_COUNT = """
        DECLARE $chat_id AS Int64;
        SELECT
            count(word) as words
        FROM words
        WHERE
            repetition = 0
            AND 
            chat_id = $chat_id
        ;
        """
