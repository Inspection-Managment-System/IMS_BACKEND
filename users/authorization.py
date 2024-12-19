from functools import wraps

from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapped(request, *args, **kwargs):
            try:
                auth = JWTAuthentication()
                try:
                    user, token = auth.authenticate(request)
                except:
                    return JsonResponse(
                        {"detail": "Access token not present or is invalid"}, status=400
                    )
                payload = token.payload
                user_role = payload.get("role", None)

                if user_role is None or user_role not in allowed_roles:
                    return JsonResponse(
                        ["You are unauthorized for this action."],
                        status=403,
                        safe=False,
                    )
            except (InvalidToken, TokenError) as e:
                return JsonResponse({"detail": "Invalid token"}, status=401)

            return func(request, *args, **kwargs)

        return wrapped

    return decorator
