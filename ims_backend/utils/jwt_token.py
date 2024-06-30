from rest_framework_simplejwt.tokens import RefreshToken


def generate_token(user):
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    access_token["email"] = user.email
    access_token["role"] = user.userprofile.role.name if user.userprofile.role else None

    data_groups = (
        user.userprofile.data_groups.all() if hasattr(user, "userprofile") else []
    )
    data_group_names = [data_group.name for data_group in data_groups]
    access_token["data_groups"] = data_group_names if data_group_names else None

    return {
        "access_token": str(access_token),
        "refresh_token": str(refresh),
    }
