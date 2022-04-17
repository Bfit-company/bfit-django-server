from django.urls import path, re_path
from post_app.api.views import (
    post_list,
    PostDetail,
    GetPostsDetailByPostList
    # get_posts_detail_by_post_list
    # post_detail
)

urlpatterns = [
    path('post_list/', post_list, name='post_list'),
    path('post_detail/<int:pk>/', PostDetail.as_view(), name='post_detail'),
    # path('get_posts_detail_by_post_list/', get_posts_detail_by_post_list, name='get_posts_detail_by_post_list'),
    path('get_posts_detail_by_post_list/', GetPostsDetailByPostList.as_view(), name='get_posts_detail_by_post_list'),
]
