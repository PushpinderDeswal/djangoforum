from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "users"
urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path("profile/", views.profile, name="profile"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path("profile/update_password/", views.update_password, name="update_password"),
]
