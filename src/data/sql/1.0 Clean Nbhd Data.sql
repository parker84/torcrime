
drop table if exists stg.nbhd_data;
create table stg.nbhd_data as 
select 
    "Hood_ID" as nbhd_id
    ,"Neighbourhood" as neighbourhood
    ,"Shape__Area" as sq_feet
    ,"Population" as population
from src.nbhd_data