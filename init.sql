create table jamify.public.music
(
    music_author    varchar,
    music_energy    varchar,
    music_image_src varchar,
    music_isrc      varchar,
    music_tempo     varchar,
    music_title     varchar,
    music_id        pg_catalog.uuid default gen_random_uuid()
        constraint music_pk
            primary key
);

create index music_title_index
    on public.music (music_title);

-- Create the "tag_entity" table
create table jamify.public.tag_entity
(
    tag_label varchar,
    tag_id    bigint
        constraint tag_entity_pk
            primary key
);

-- Create the "music_tag" table
create table jamify.public.music_tag
(
    music_id pg_catalog.uuid
        constraint music_fk
            references public.music,
    tag_id   bigint
        constraint tag_fk
            references public.tag_entity,
    constraint music_tag_pk
        primary key (tag_id, music_id)
);
