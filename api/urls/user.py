from django.urls import path

from api.viewsets import CreateSuperUserView, CustomLoginView, SignUpView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("create_super_user/", CreateSuperUserView.as_view(), name="create_super_user"),
    path("login/", CustomLoginView.as_view(), name="login"),
]
