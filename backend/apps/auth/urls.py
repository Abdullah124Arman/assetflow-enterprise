from django.urls import path
from .views import SignupView, LoginView, RefreshView, ForgotPasswordView

urlpatterns = [
    path('signup', SignupView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
    path('refresh', RefreshView.as_view(), name='refresh'),
    path('forgot-password', ForgotPasswordView.as_view(), name='forgot-password'),
]
