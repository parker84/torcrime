

drop table if exists stg.mci_data;
create table stg.mci_data as 
select 
    distinct
    event_unique_id 
    ,"Hood_ID" as nbhd_id
    ,"Neighbourhood" as neighbourhood
    ,"MCI" as crime_type
    ,occurrencedayofweek
    ,occurrencehour
    ,premises_type as premisetype
    ,occurrencedate
    ,occurrenceyear
    ,"Long" as long
    ,"Lat" as lat
from src.mci_data;

drop index if exists mci_event_and_crime_id_ix;
create unique index mci_event_and_crime_id_ix on stg.mci_data (event_unique_id, crime_type);