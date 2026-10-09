from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('api/v1/posts/', include('apps.main.urls')),
    path('admin/', admin.site.urls),
]
