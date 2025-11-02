"""
Logout ViewSet - Handles user logout and session cleanup
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from users.models import ActiveSession


class LogoutView(APIView):
    """
    Handle user logout and end active session
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        POST /api/auth/logout/
        Ends user's active session(s)
        """
        try:
            print(f"🚪 LOGOUT REQUEST from user: {request.user.username if request.user.is_authenticated else 'Unknown'}")
            
            # Get token from request header
            token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
            
            if token:
                # End session by token
                deleted_count = ActiveSession.objects.filter(
                    session_token=token,
                    is_active=True
                ).update(is_active=False)
                
                print(f"✅ LOGOUT SUCCESS: Deleted {deleted_count} session(s)")
            
            # Also end all sessions for this user
            if request.user.is_authenticated:
                ActiveSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
            
            active_count = ActiveSession.objects.filter(is_active=True).count()
            print(f"📊 Active sessions remaining: {active_count}")
            
            return Response(
                {"message": "Logged out successfully"},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            print(f"❌ LOGOUT ERROR: {str(e)}")
            return Response(
                {"error": f"Logout failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

