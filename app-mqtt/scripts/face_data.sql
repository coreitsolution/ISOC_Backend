-- Table: center.face_data

-- DROP TABLE IF EXISTS center.face_data;

CREATE TABLE IF NOT EXISTS face_data
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    alarm_code text COLLATE pg_catalog."default",
    channel_id text COLLATE pg_catalog."default",
    appear_times integer,
    begin_time timestamp with time zone,
    end_time timestamp with time zone NOT NULL,
    age integer,
    hited text COLLATE pg_catalog."default",
    beard text COLLATE pg_catalog."default",
    emotion text COLLATE pg_catalog."default",
    eye text COLLATE pg_catalog."default",
    fringe text COLLATE pg_catalog."default",
    gender text COLLATE pg_catalog."default",
    glasses text COLLATE pg_catalog."default",
    mask text COLLATE pg_catalog."default",
    mount text COLLATE pg_catalog."default",
 face_image_url text,
 picture_url text,
    service_code text COLLATE pg_catalog."default",
    similar_faces jsonb DEFAULT '[]'::jsonb,
    is_watchlist boolean DEFAULT false,
    watchlist_uids uuid[],
    method text COLLATE pg_catalog."default",
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT face_data_pkey PRIMARY KEY (id, end_time)
) PARTITION BY RANGE (end_time);

ALTER TABLE IF EXISTS face_data
    OWNER to postgres;

COMMENT ON TABLE face_data
    IS 'Logs for face recognition events, range-partitioned by end_time.';

COMMENT ON COLUMN face_data.similar_faces
    IS 'JSON array containing metadata of matching faces found in the database.';

COMMENT ON COLUMN face_data.is_watchlist
    IS 'Flag indicating if the face belongs to a restricted/monitored person.';

COMMENT ON COLUMN center.face_data.watchlist_uids
    IS 'Array of UUIDs representing specific watchlists this face triggered.';
-- Index: idx_face_data_channel

-- DROP INDEX IF EXISTS center.idx_face_data_channel;

CREATE INDEX IF NOT EXISTS idx_face_data_channel
    ON center.face_data USING btree
    (channel_id COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_face_data_end_time

-- DROP INDEX IF EXISTS center.idx_face_data_end_time;

CREATE INDEX IF NOT EXISTS idx_face_data_end_time
    ON center.face_data USING btree
    (end_time DESC NULLS FIRST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default;
-- Index: idx_face_data_similar_faces

-- DROP INDEX IF EXISTS center.idx_face_data_similar_faces;

CREATE INDEX IF NOT EXISTS idx_face_data_similar_faces
    ON center.face_data USING gin
    (similar_faces)
    WITH (fastupdate=True, gin_pending_list_limit=4194304)
    TABLESPACE pg_default;
-- Index: idx_face_data_watchlist

-- DROP INDEX IF EXISTS center.idx_face_data_watchlist;

CREATE INDEX IF NOT EXISTS idx_face_data_watchlist
    ON center.face_data USING btree
    (is_watchlist ASC NULLS LAST)
    WITH (fillfactor=100, deduplicate_items=True)
    TABLESPACE pg_default
    WHERE is_watchlist IS TRUE;

-- Partitions SQL

CREATE TABLE center.face_data_2026_02 PARTITION OF center.face_data
    FOR VALUES FROM ('2026-02-01 00:00:00+00') TO ('2026-03-01 00:00:00+00')
TABLESPACE pg_default;

ALTER TABLE IF EXISTS center.face_data_2026_02
    OWNER to postgres;