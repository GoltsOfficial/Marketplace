from django.urls import path

from . import views


app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("<slug:slug>/", views.post_by_slug, name="by_slug"),
    path("create/", views.PostCreateView.as_view(), name="post_create"),
]
