from django.urls import path

from .views import RatingList, RatingDetail, RatingDetailDelete, RatingDetailUpdate, GetAllCoachRating

urlpatterns = [
    path('rating_list/', RatingList.as_view(), name='rating_list'),
    path('rating-detail-delete/', RatingDetailDelete.as_view(), name='rating_detail_delete'),
    path('rating-detail-update/', RatingDetailUpdate.as_view(), name='rating_detail_update'),
    path('rating_detail/<int:pk>/', RatingDetail.as_view(), name='rating_detail'),
    path('get_all_coach_rating/<int:coach_id>/', GetAllCoachRating.as_view(), name='get_all_coach_rating'),
]
