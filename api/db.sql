CREATE TABLE show (
    id BIGSERIAL,
    name text,
    imdb_id text PRIMARY KEY
);

CREATE TABLE episode (
    id BIGSERIAL PRIMARY KEY,
    show_id text,
    episode_id text,
    episode_title text,
    season integer,
    episode integer,
    rating real,
    votes integer
);

CREATE TABLE poster (
    id BIGSERIAL,
    show_id text PRIMARY KEY,
    poster_url text
);
