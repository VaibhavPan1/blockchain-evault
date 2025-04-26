from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('upload/', views.upload, name='upload'),
    path('viewfiles/', views.view_files, name='viewfiles'),
    path('download/<str:file_name>/<str:cid>/', views.retrieve_file, name="retrieve_file"),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    # path('confirm_upload/', views.confirm_upload, name='confirm_upload'),
]
