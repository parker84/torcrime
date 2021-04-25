
drop table if exists stg.crime_data;
create table stg.crime_data as 
select
    mci.nbhd_id
    ,mci.event_unique_id
    ,mci.neighbourhood
    ,mci.crime_type
    ,mci.occurrencehour
    ,mci.occurrenceyear
    ,mci.premisetype
    ,mci.occurrencedayofweek
    ,mci.lat
    ,mci.long
    ,nbhd.sq_metres
    ,nbhd.population
    ,nbhd.nbhd_id as nbhd_nbhd_id
from stg.mci_data as mci
full outer join stg.nbhd_data as nbhd on
    cast(mci.nbhd_id as text) = cast(nbhd.nbhd_id as text)
where cast(mci.occurrenceyear as int) > 2013;
    

drop index if exists crime_event_and_type_ix;
create unique index crime_event_and_type_ix on stg.crime_data (event_unique_id, crime_type);