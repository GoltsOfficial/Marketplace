from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("create/", views.PostCreateView.as_view(), name="post_create"),
]
