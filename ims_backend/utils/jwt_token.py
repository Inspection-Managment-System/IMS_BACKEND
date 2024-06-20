from datetime import timedelta

from rest_framework_simplejwt.tokens import RefreshToken


def generate_token(user):
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    access_token["email"] = user.email
    access_token["role"] = user.userprofile.role.name if user.userprofile.role else None
    access_token["data_group"] = (
        user.userprofile.data_group.name if user.userprofile.data_group else None
    )

    return {
        "access_token": str(access_token),
        "refresh_token": str(refresh),
    }
