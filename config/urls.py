from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('faces/', views.faces, name='faces'),
    path('test/', views.test, name='test'),
    path('register_people/', views.register_people, name='register_people'),
    path('upload/', views.upload, name='upload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
