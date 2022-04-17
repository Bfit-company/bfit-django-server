from django.db.models import Q


class Utils:

    @staticmethod
    def get_detail_by_list_id(table, query_list_id, attribute):

        my_filter_qs = Q()
        for query in query_list_id:
            my_filter_qs = my_filter_qs | Q(id=query[attribute])

        return table.objects.filter(my_filter_qs)
