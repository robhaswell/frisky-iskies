use `frisky-iskies`;

drop table if exists transactions;

create table transactions (
    `id` bigint not null,
    `region_id` int not null,
    `system_id` int not null,
    `station_id` int not null,
    `type_id` int not null,
    `buy` tinyint not null,
    `price` float(16,2) not null,
    `minvolume` int not null,
    `volremain` int not null,
    `volenter` int not null,
    `created` datetime not null,
    `duration` smallint not null,
    `range` int not null,
    `reported_by` tinyint not null,
    `reported` datetime not null,
    index (station_id),
    index (type_id),
    index (buy),
    index (price)
) ENGINE=MyISAM
