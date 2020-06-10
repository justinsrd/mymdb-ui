CREATE TABLE show (
    id BIGSERIAL,
    name text,
    imdb_id text PRIMARY KEY,
    poster_url text
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


CREATE UNIQUE INDEX IF NOT EXISTS show_pkey ON show(imdb_id);
CREATE UNIQUE INDEX IF NOT EXISTS episode_pkey ON episode(id);
