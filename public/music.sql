/*
 * Copyright (c) 2024, LAPETITTE Matthieu
 * Tous droits réservés.
 *
 * Ce fichier est soumis aux termes de la licence suivante :
 * Vous êtes autorisé à utiliser, modifier et distribuer ce code sous réserve des conditions de la licence.
 * Vous ne pouvez pas utiliser ce code à des fins commerciales sans autorisation préalable.
 *
 * Ce fichier est fourni "tel quel", sans garantie d'aucune sorte, expresse ou implicite, y compris mais sans s'y limiter,
 * les garanties implicites de qualité marchande ou d'adaptation à un usage particulier.
 *
 * Pour toute question ou demande d'autorisation, contactez LAPETITTE Matthieu à l'adresse suivante :
 * matthieu@lapetitte.fr
 */

create table public.music
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

