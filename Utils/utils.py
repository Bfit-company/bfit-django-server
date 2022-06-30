from django.db.models import Q
from datetime import datetime, timezone


class Utils:

    @staticmethod
    def get_detail_by_list_id(table, query_list_id, attribute):
        my_filter_qs = Q()
        for query in query_list_id:
            my_filter_qs = my_filter_qs | Q(id=query[attribute])

        return table.objects.filter(my_filter_qs)

    @staticmethod
    def get_now_as_timestamp():
        return int(datetime.now().timestamp())

    @staticmethod
    def get_day_ts(ts):
        x = datetime.fromtimestamp(ts, tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        return int(datetime.timestamp(x))

    @staticmethod
    def get_ts_today():
        ts_now = int(datetime.timestamp(datetime.now()))
        return Utils.get_day_ts(ts_now)
