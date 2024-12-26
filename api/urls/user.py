from django.contrib.auth import views as auth_views
from django.urls import path

from api.viewsets import (CreateSuperUserView, CustomLoginView,
                          PasswordResetAPIView, SignUpView)

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("create_super_user/", CreateSuperUserView.as_view(), name="create_super_user"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("password_reset/", PasswordResetAPIView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
