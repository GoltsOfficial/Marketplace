from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]

# API
urlpatterns += [
    path('api/v1/posts/', include('apps.posts.urls')),
    path('api/v1/accounts/', include('apps.accounts.urls')),
]
