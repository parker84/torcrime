
drop table if exists stg.nbhd_data;
create table stg.nbhd_data as 
select 
    "Hood_ID" as nbhd_id
    ,"Neighbourhood" as neighbourhood
    ,"Shape__Area" as sq_metres
    ,"F2020_Population_Projection" as population
from src.nbhd_data;

drop index if exists nbhd_id_ix;
create unique index nbhd_id_ix on stg.nbhd_data (nbhd_id);