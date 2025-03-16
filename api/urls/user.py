from django.contrib.auth import views as auth_views
from django.urls import path

from api.viewsets import (CreateSuperUserView, CustomLoginView,
                          PasswordChangeAPIView, PasswordResetAPIView,
                          ReadEmiratesId, SignUpView)

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("read_emirates_id", ReadEmiratesId.as_view(), name="read_emirates_id"),
    path("create_super_user/", CreateSuperUserView.as_view(), name="create_super_user"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("password_reset/", PasswordResetAPIView.as_view(), name="password_reset"),
    path("password_change/", PasswordChangeAPIView.as_view(), name="password_change"),
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
