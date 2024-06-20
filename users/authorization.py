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
                user, token = auth.authenticate(request)
                payload = token.payload
                user_role = payload.get("role", None)

                if user_role is None or user_role not in allowed_roles:
                    return JsonResponse({"detail": "Unauthorized"}, status=403)
            except (InvalidToken, TokenError) as e:
                return JsonResponse({"detail": "Invalid token"}, status=401)

            return func(request, *args, **kwargs)

        return wrapped

    return decorator
