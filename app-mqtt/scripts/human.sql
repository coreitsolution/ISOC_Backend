CREATE TABLE IF NOT EXISTS center.human_detections
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    age integer, 
    gender text COLLATE pg_catalog."default",
 
    capture_time timestamp with time zone,
    channel_id text COLLATE pg_catalog."default",
 
    detect_mode text COLLATE pg_catalog."default",
    direction text COLLATE pg_catalog."default",
 
    emotion text COLLATE pg_catalog."default", 
    glasses text COLLATE pg_catalog."default",
    hat text COLLATE pg_catalog."default",
    hat_type text COLLATE pg_catalog."default",
    beard text COLLATE pg_catalog."default",
    mask text COLLATE pg_catalog."default",
 
    bag text COLLATE pg_catalog."default",
    bag_type text COLLATE pg_catalog."default",
    coat text COLLATE pg_catalog."default",
    coat_color text COLLATE pg_catalog."default",
    trousers text COLLATE pg_catalog."default",
    trousers_color text COLLATE pg_catalog."default",
 
    face_image_top integer,
    face_image_right integer,
    face_image_left integer,
    face_image_bottom integer,
 
    face_image_url text COLLATE pg_catalog."default",
    picture_url text COLLATE pg_catalog."default",
 
    method text COLLATE pg_catalog."default",
 
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
 
    CONSTRAINT human_detection_pkey PRIMARY KEY (id, capture_time)
) PARTITION BY RANGE (capture_time);
