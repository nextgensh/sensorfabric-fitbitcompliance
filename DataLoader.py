#!/usr/bin/env python3

from pyathena import connect
from pyathena.pandas.cursor import PandasCursor
import pandas as pd

class DataLoader():
    def __init__(self,
                 aws_access_key_id : str,
                 aws_secret_access_key : str,
                 region_name : str,
                 s3_staging_dir : str,
                 work_group : str,
                 schema_name : str,
                 aws_session_token=None,
                 cache=False):

        self.cursor = connect(aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            aws_session_token=aws_session_token,
                            s3_staging_dir=s3_staging_dir,
                            region_name=region_name,
                            schema_name = schema_name,
                            work_group=work_group,
                            cursor_class=PandasCursor
                            ).cursor()
        self.cache = 3600 if cache else None

    def getSleep(self):
        query = """
        SELECT participantidentifier,
        date_format(min(startdate), '%Y-%m-%d') as start_date,
        date_format(max(enddate),'%Y-%m-%d') as end_date,
        count(DISTINCT(date_format(startdate, '%Y-%m-%d'))) as days_recorded,
        count(participantidentifier) as sleep_sessions,
        CAST(split_part(CAST(max(enddate) - min(startdate) as varchar), ' ', 1) as INT) + 1 as calendar_days
            FROM fitbitsleeplogs WHERE duration > 0
            GROUP BY participantidentifier
            ORDER BY start_date ASC
        """

        return self.cursor.execute(query, cache_expiration_time=self.cache).as_pandas()

    def getActivity(self):
        query = """
        SELECT participantidentifier,
        date_format(min(date), '%Y-%m-%d') as start_date,
        date_format(max(date), '%Y-%m-%d') as end_date,
        count(date) as days_recorded,
        CAST(split_part(CAST(max(date) - min(date) as varchar), ' ', 1) as int) + 1 as calendar_days
            FROM fitbitdailydata
            WHERE steps > 0
            GROUP BY participantidentifier
        """

        return self.cursor.execute(query, cache_expiration_time=self.cache).as_pandas()

    def getRestingHR(self):
        query = """
        SELECT participantidentifier,
        date_format(min(date), '%Y-%m-%d') as start_date,
        date_format(max(date), '%Y-%m-%d') as end_date,
        count(date) as days_recorded,
        CAST(split_part(CAST(max(date) - min(date) as varchar), ' ', 1) as int) + 1 as calendar_days,
        avg(restingheartrate) as average_resting_hr, min(restingheartrate) as min_resting_hr, max(restingheartrate) as max_resting_hr
            FROM fitbitrestingheartrates
            WHERE restingheartrate IS NOT NULL
            GROUP BY participantidentifier
        """

        return self.cursor.execute(query, cache_expiration_time=self.cache).as_pandas()

    def getHRV(self):
        query = """
        SELECT participantidentifier,
        date_format(min(date), '%Y-%m-%d') as start_date,
        date_format(max(date), '%Y-%m-%d') as end_date,
        count(date) as days_recorded,
        CAST(split_part(CAST(max(date) - min(date) as varchar), ' ', 1) as int) + 1 as calendar_days,
        avg(hrvdailyrmssd) as daily_avg_hrv, avg(hrvdeeprmssd) as deep_avg_hrv,
        min(hrvdailyrmssd) as daily_min_hrv, min(hrvdeeprmssd) as deep_min_hrv,
        max(hrvdailyrmssd) as daily_max_hrv, max(hrvdeeprmssd) as deep_max_hrv
            FROM fitbitdailydata
            WHERE hrvdailyrmssd IS NOT NULL
            GROUP BY participantidentifier
        """

        return self.cursor.execute(query, cache_expiration_time=self.cache).as_pandas()

    # TODO : Change this later to automatically pull from the enrolledParticipant table.
    def getParticipants(self):
        query = """
           SELECT DISTINCT(participantidentifier) FROM fitbitactivitylogs
        """

        return self.cursor.execute(query, cache_expiration_time=self.cache).as_pandas()
