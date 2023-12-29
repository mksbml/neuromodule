CREATE TABLE request (
    id bigserial primary key not null unique,
    is_worked boolean default False,
    is_message_required boolean default False,
    created_at timestamp default now(),
    soil_background int,
    work_type int,
    lat float,
    lon float,
    plot_size float,
    pmin int,
    pmax int,
    stock int,
    leasing varchar,
    fueltype varchar,
    wmin int,
    wmax int,
    condition varchar,
    mdelivery int,
    drivetype varchar,
    ans_limit int,
    push_history json,
);

CREATE TABLE response (
    id int not null,
    ans json default '[]'::json,
    status varchar
);

CREATE TABLE notify (
    created_at timestamp default now(),
    request_id int not null,
    item_id int not null
);

-- Таблица с хранимым обрудованием
CREATE TABLE item (
    id bigint not null unique,
    data json not null
);

CREATE TABLE models (
    mark varchar not null,
    model varchar not null,
    section varchar not null,
    data json not null
);
