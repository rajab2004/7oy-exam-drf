from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, DoctorProfile, PatientProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'phone', 'is_active', 'created_at')
        read_only_fields = ('id', 'is_active', 'created_at')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)
    
    # Patient specific fields
    date_of_birth = serializers.DateField(write_only=True, required=False)
    patient_gender = serializers.CharField(write_only=True, required=False)
    
    # Doctor specific fields
    specialization = serializers.CharField(write_only=True, required=False)
    experience_years = serializers.IntegerField(write_only=True, required=False)
    doctor_gender = serializers.CharField(write_only=True, required=False)
    bio = serializers.CharField(write_only=True, required=False)
    consultation_fee = serializers.DecimalField(write_only=True, max_digits=10, decimal_places=2, required=False)
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password2', 'role', 'phone',
            'date_of_birth', 'patient_gender', 'specialization', 'experience_years',
            'doctor_gender', 'bio', 'consultation_fee'
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        
        role = attrs.get('role')
        
        if role == 'patient':
            if not attrs.get('date_of_birth'):
                raise serializers.ValidationError({"date_of_birth": "Date of birth is required for patients."})
            if not attrs.get('patient_gender'):
                raise serializers.ValidationError({"patient_gender": "Gender is required for patients."})
        
        elif role == 'doctor':
            if not attrs.get('specialization'):
                raise serializers.ValidationError({"specialization": "Specialization is required for doctors."})
            if not attrs.get('doctor_gender'):
                raise serializers.ValidationError({"doctor_gender": "Gender is required for doctors."})
        
        return attrs
    
    def create(self, validated_data):
        # Remove extra fields
        password = validated_data.pop('password')
        validated_data.pop('password2')
        
        date_of_birth = validated_data.pop('date_of_birth', None)
        patient_gender = validated_data.pop('patient_gender', None)
        
        specialization = validated_data.pop('specialization', None)
        experience_years = validated_data.pop('experience_years', 0)
        doctor_gender = validated_data.pop('doctor_gender', None)
        bio = validated_data.pop('bio', '')
        consultation_fee = validated_data.pop('consultation_fee', 0)
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data['role'],
            phone=validated_data.get('phone', ''),
            password=password
        )
        
        # Create profile based on role
        if user.is_patient and date_of_birth and patient_gender:
            PatientProfile.objects.create(
                user=user,
                date_of_birth=date_of_birth,
                gender=patient_gender
            )
        
        elif user.is_doctor and specialization and doctor_gender:
            DoctorProfile.objects.create(
                user=user,
                specialization=specialization,
                experience_years=experience_years,
                gender=doctor_gender,
                bio=bio,
                consultation_fee=consultation_fee
            )
        
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "username" and "password"')


class DoctorProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    
    class Meta:
        model = DoctorProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class PatientProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PatientProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class DoctorListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = DoctorProfile
        fields = ('id', 'user', 'specialization', 'experience_years', 'gender', 'bio', 'consultation_fee')