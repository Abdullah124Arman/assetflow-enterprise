import hashlib
import uuid
from django.utils import timezone
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User, RefreshTokenModel, PasswordResetToken
from apps.org.models import Department
from apps.org.views import log_activity
from .serializers import SignupSerializer, LoginSerializer, RefreshSerializer, ForgotPasswordSerializer

def _hash_token(token_str):
    return hashlib.sha256(token_str.encode('utf-8')).hexdigest()

def _generate_auth_response(user):
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    
    # Store refresh token hash in DB
    RefreshTokenModel.objects.create(
        user=user,
        token_hash=_hash_token(str(refresh)),
        expires_at=timezone.datetime.fromtimestamp(refresh['exp'], tz=timezone.utc)
    )
    
    return Response({
        'data': {
            'auth': {
                'access_token': str(access),
                'refresh_token': str(refresh),
                'expires_in': access.lifetime.total_seconds()
            }
        }
    })

class SignupView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        if User.objects.filter(email=data['email']).exists():
            return Response({'error': {'code': 'EMAIL_EXISTS', 'message': 'Email already registered'}}, status=status.HTTP_409_CONFLICT)
            
        dept = None
        if data.get('department_id'):
            try:
                dept = Department.objects.get(id=data['department_id'])
            except Department.DoesNotExist:
                return Response({'error': {'code': 'INVALID_DEPT', 'message': 'Department not found'}}, status=status.HTTP_400_BAD_REQUEST)
                
        # Role is explicitly hardcoded to employee
        user = User.objects.create_user(
            email=data['email'],
            name=data['name'],
            password=data['password'],
            role='employee',
            department=dept
        )
        
        log_activity(user, "auth.signup", "user", user.id)
        return _generate_auth_response(user)

class LoginView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': {'code': 'AUTH_FAILED', 'message': 'Invalid credentials'}}, status=status.HTTP_401_UNAUTHORIZED)
            
        if not user.check_password(password):
            return Response({'error': {'code': 'AUTH_FAILED', 'message': 'Invalid credentials'}}, status=status.HTTP_401_UNAUTHORIZED)
            
        if user.status != 'active':
            return Response({'error': {'code': 'ACCOUNT_INACTIVE', 'message': 'Account is inactive'}}, status=status.HTTP_403_FORBIDDEN)
            
        log_activity(user, "auth.login", "user", user.id)
        return _generate_auth_response(user)

class RefreshView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token_str = serializer.validated_data['refresh_token']
        token_hash = _hash_token(token_str)
        
        try:
            token_record = RefreshTokenModel.objects.select_related('user').get(token_hash=token_hash)
        except RefreshTokenModel.DoesNotExist:
            return Response({'error': {'code': 'INVALID_TOKEN', 'message': 'Token not found'}}, status=status.HTTP_401_UNAUTHORIZED)
            
        if token_record.revoked or token_record.expires_at < timezone.now():
            return Response({'error': {'code': 'INVALID_TOKEN', 'message': 'Token expired or revoked'}}, status=status.HTTP_401_UNAUTHORIZED)
            
        if token_record.user.status != 'active':
            return Response({'error': {'code': 'ACCOUNT_INACTIVE', 'message': 'Account is inactive'}}, status=status.HTTP_403_FORBIDDEN)
            
        # Verify jwt validity
        try:
            old_refresh = RefreshToken(token_str)
        except TokenError:
            return Response({'error': {'code': 'INVALID_TOKEN', 'message': 'Token is invalid'}}, status=status.HTTP_401_UNAUTHORIZED)
            
        # Revoke old token
        token_record.revoked = True
        token_record.save()
        
        log_activity(token_record.user, "auth.refresh", "user", token_record.user.id)
        
        # Generate new token pair
        return _generate_auth_response(token_record.user)

class ForgotPasswordView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            if user.status == 'active':
                token = uuid.uuid4().hex
                PasswordResetToken.objects.create(
                    user=user,
                    token_hash=_hash_token(token),
                    expires_at=timezone.now() + timezone.timedelta(hours=1)
                )
                log_activity(user, "auth.forgot_password", "user", user.id)
                # In real env, we'd send email here. Log stub is fine.
        except User.DoesNotExist:
            pass # Silent fail for security
            
        return Response({'data': {'message': 'If an account exists, a reset link has been sent'}})
