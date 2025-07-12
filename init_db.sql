CREATE TABLE IF NOT EXISTS articles (
    title_of_article TEXT UNIQUE,
    url_of_article TEXT UNIQUE,
    full_content_of_article TEXT,
    main_picture_of_article_url TEXT,
    published_utc TIMESTAMP WITH TIME ZONE,
    fetch_datetime_utc TIMESTAMP WITH TIME ZONE,
    main_category TEXT
);
CREATE INDEX IF NOT EXISTS idx_url ON articles (url_of_article);
CREATE INDEX IF NOT EXISTS idx_title ON articles (title_of_article);