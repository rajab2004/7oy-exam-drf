from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        DOCTOR = 'doctor', 'Doctor'
        PATIENT = 'patient', 'Patient'
    
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PATIENT)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR
    
    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT


class DoctorProfile(models.Model):
    class Specialization(models.TextChoices):
        CARDIOLOGY = 'cardiology', 'Cardiology'
        DERMATOLOGY = 'dermatology', 'Dermatology'
        NEUROLOGY = 'neurology', 'Neurology'
        PEDIATRICS = 'pediatrics', 'Pediatrics'
        ORTHOPEDICS = 'orthopedics', 'Orthopedics'
        GYNECOLOGY = 'gynecology', 'Gynecology'
        DENTISTRY = 'dentistry', 'Dentistry'
        PSYCHIATRY = 'psychiatry', 'Psychiatry'
    
    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='doctor_profile'
    )
    specialization = models.CharField(
        max_length=20, 
        choices=Specialization.choices,
        default=Specialization.CARDIOLOGY
    )
    experience_years = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    bio = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialization}"
    
    class Meta:
        ordering = ['-created_at']


class PatientProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='patient_profile'
    )
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=Gender.choices)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=17, blank=True)
    blood_type = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    class Meta:
        ordering = ['-created_at']