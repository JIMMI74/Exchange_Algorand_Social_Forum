from django.urls import path, include
from .import views

urlpatterns = [
    path('registration/', views.registration_view, name='registration_view'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path("user/<str:username>/social/", views.user_profile_view, name="user_profile_social"),
    path('list_user/', views.UserListViewCBV.as_view(), name="list_user"),
    path("users/", views.UserList.as_view(), name="users_list_social"),

]
