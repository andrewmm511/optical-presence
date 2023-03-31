from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('faces/', views.faces, name='faces'),
    path('register_people/', views.register_people, name='register_people'),
    path('upload/', views.upload, name='upload'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register_people/delete/<uuid:person_id>/', views.delete_person, name='delete_person'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
