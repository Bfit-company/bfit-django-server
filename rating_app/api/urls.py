from django.urls import path

from .views import RatingList, RatingDetail,RatingDetailDelete,RatingDetailUpdate

urlpatterns = [
    path('rating_list/', RatingList.as_view(), name='rating_list'),
    path('rating-detail-delete/', RatingDetailDelete.as_view(), name='rating_detail_delete'),
    path('rating-detail-update/', RatingDetailUpdate.as_view(), name='rating_detail_update'),
    path('rating_detail/{id}', RatingDetail.as_view(), name='rating_detail'),
]