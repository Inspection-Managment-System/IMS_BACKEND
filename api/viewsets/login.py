import json
from datetime import datetime

from django.contrib.auth import authenticate, login
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import UserSerializer
from ims_backend.utils.jwt_token import generate_token
from ims_backend.utils.license import decrypt


class LicenseRequiredMixin:
    def validate_license(self):
        """Validate license file - checks expiration and concurrent user limit"""
        try:
            with open("license_v1.json", "rb") as file:
                encrypted_data = file.read()
                decrypted_data = decrypt(encrypted_data)
                license_data = json.loads(decrypted_data)
                
                # Check expiration date
                expiration_date_str = license_data.get("expiration_date")
                if expiration_date_str:
                    expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
                    current_date = datetime.now()
                    if current_date > expiration_date:
                        return False, "License expired", None
                else:
                    return False, "Invalid license - no expiration date", None
                
                # Check CONCURRENT user limit (active sessions)
                from users.models import ActiveSession
                
                # Cleanup old sessions first (over 24 hours)
                ActiveSession.cleanup_old_sessions()
                
                max_users = license_data.get("max_users", 0)
                active_sessions = ActiveSession.get_active_session_count()
                
                # Check if concurrent limit reached
                if active_sessions >= max_users:
                    return False, f"Concurrent user limit reached ({active_sessions}/{max_users} users currently logged in)", license_data
                
                return True, "Valid", license_data
                
        except Exception as e:
            print(f"License validation error: {str(e)}")
            return False, "License file missing or corrupted", None


class CustomLoginView(LicenseRequiredMixin, APIView):
    authentication_classes = []
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        
        # Step 1: Authenticate user credentials FIRST
        user = authenticate(username=username, password=password)
        
        # If credentials are wrong, return credential error immediately
        if user is None:
            print(f"❌ CREDENTIAL ERROR: Invalid credentials for username '{username}'")
            return Response(
                {"error": "CREDENTIAL ERROR: Invalid username or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Step 2: Check if user account is active
        if not user.is_active:
            print(f"❌ INACTIVE ACCOUNT: User '{username}' is inactive")
            return Response(
                {"error": "Your account is inactive. Please contact administrator."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        print(f"✅ CREDENTIALS VALID for '{username}' - Checking license...")
        
        # Step 3: Validate license
        from users.models import ActiveSession
        
        try:
            # Read license file
            with open("license_v1.json", "rb") as file:
                encrypted_data = file.read()
                decrypted_data = decrypt(encrypted_data)
                license_data = json.loads(decrypted_data)
            
            # Check expiration date
            expiration_date_str = license_data.get("expiration_date")
            if expiration_date_str:
                expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
                if datetime.now() > expiration_date:
                    return Response(
                        {"error": "License expired"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            
            # Cleanup old sessions (over 24 hours)
            from django.utils import timezone
            from datetime import timedelta
            cutoff_time = timezone.now() - timedelta(hours=24)
            ActiveSession.objects.filter(last_activity__lt=cutoff_time).delete()
            
            # Get max concurrent users from license
            max_users = license_data.get("max_users", 0)
            
            # End THIS user's existing sessions first (allows re-login)
            ActiveSession.objects.filter(user=user).delete()
            
            # NOW count active sessions (from OTHER users only)
            current_sessions = ActiveSession.objects.filter(is_active=True).count()
            
            # Check if limit reached (by other users)
            if current_sessions >= max_users:
                print(f"🔒 LICENSE LIMIT BLOCKED: {current_sessions}/{max_users} sessions active")
                return Response(
                    {"error": f"LICENSE LIMIT EXCEEDED: Maximum {max_users} concurrent user(s) allowed. Currently {current_sessions} user(s) logged in. Please wait for logout."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            
        except FileNotFoundError:
            return Response(
                {"error": "License file not found"},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as e:
            print(f"License error: {str(e)}")
            return Response(
                {"error": f"License validation failed: {str(e)}"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Step 4: All checks passed - Create login session
        print(f"✅ LICENSE OK - Creating session for '{username}'")
        
        login(request, user)
        token = generate_token(user)
        user_profile_data = UserSerializer(user).data
        
        # Create new active session
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        ActiveSession.objects.create(
            user=user,
            session_token=token,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True
        )
        
        active_count = ActiveSession.objects.filter(is_active=True).count()
        print(f"✅ LOGIN SUCCESS: '{username}' - Active sessions now: {active_count}")

        return Response(
            {
                "user_data": user_profile_data,
                "token": token,
            },
            status=status.HTTP_200_OK,
        )
