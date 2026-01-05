from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView

from .views import (
    RegisterView, LoginView, CustomTokenRefreshView, UserProfileView,
    DoctorProfileView, PatientProfileView, DoctorListView, DoctorDetailView,
    UserListView, UserDetailView
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='logout'),
    
    # Profile
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('doctor/profile/', DoctorProfileView.as_view(), name='doctor_profile'),
    path('patient/profile/', PatientProfileView.as_view(), name='patient_profile'),
    
    # Doctors
    path('doctors/', DoctorListView.as_view(), name='doctor_list'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'),
    
    # Admin only
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
]