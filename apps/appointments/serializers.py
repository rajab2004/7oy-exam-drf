from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from .models import TimeSlot, Appointment
from apps.users.serializers import DoctorListSerializer, UserSerializer


class TimeSlotSerializer(serializers.ModelSerializer):
    doctor_info = serializers.SerializerMethodField()
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = (
            'id', 'doctor', 'doctor_info', 'date', 'start_time', 
            'end_time', 'is_available', 'created_at'
        )
        read_only_fields = ('is_available', 'created_at')
    
    def get_doctor_info(self, obj):
        return {
            'username': obj.doctor.username,
            'specialization': obj.doctor.doctor_profile.specialization if hasattr(obj.doctor, 'doctor_profile') else None,
            'experience_years': obj.doctor.doctor_profile.experience_years if hasattr(obj.doctor, 'doctor_profile') else 0,
        }
    
    def validate(self, attrs):
        # Check if doctor is creating their own timeslot
        request = self.context.get('request')
        if request and request.user != attrs.get('doctor'):
            raise serializers.ValidationError("You can only create timeslots for yourself.")
        
        # Check if date is in the past
        if attrs.get('date') < timezone.now().date():
            raise serializers.ValidationError("Cannot create timeslot in the past.")
        
        # Check if start_time is before end_time
        if attrs.get('start_time') >= attrs.get('end_time'):
            raise serializers.ValidationError("Start time must be before end time.")
        
        return attrs


class AvailableTimeSlotSerializer(serializers.ModelSerializer):
    doctor_info = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSlot
        fields = (
            'id', 'doctor_info', 'date', 'start_time', 
            'end_time', 'is_available'
        )
    
    def get_doctor_info(self, obj):
        return {
            'id': obj.doctor.id,
            'username': obj.doctor.username,
            'specialization': obj.doctor.doctor_profile.specialization,
            'experience_years': obj.doctor.doctor_profile.experience_years,
            'consultation_fee': obj.doctor.doctor_profile.consultation_fee,
        }


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_info = serializers.SerializerMethodField()
    patient_info = serializers.SerializerMethodField()
    timeslot_info = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = (
            'id', 'doctor', 'doctor_info', 'patient', 'patient_info',
            'timeslot', 'timeslot_info', 'status', 'notes', 'symptoms',
            'created_at', 'updated_at', 'can_cancel'
        )
        read_only_fields = ('doctor', 'patient', 'timeslot', 'created_at', 'updated_at')
    
    def get_doctor_info(self, obj):
        return {
            'username': obj.doctor.username,
            'email': obj.doctor.email,
            'phone': obj.doctor.phone,
            'specialization': obj.doctor.doctor_profile.specialization,
        }
    
    def get_patient_info(self, obj):
        return {
            'username': obj.patient.username,
            'email': obj.patient.email,
            'phone': obj.patient.phone,
        }
    
    def get_timeslot_info(self, obj):
        return {
            'date': obj.timeslot.date,
            'start_time': obj.timeslot.start_time,
            'end_time': obj.timeslot.end_time,
        }
    
    def get_can_cancel(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        
        # Check if appointment is in the future
        appointment_datetime = timezone.datetime.combine(
            obj.timeslot.date, 
            obj.timeslot.start_time
        )
        is_future = appointment_datetime > timezone.now()
        
        # Check if patient can cancel (only pending or confirmed appointments)
        can_cancel_status = obj.status in ['pending', 'confirmed']
        
        return is_future and can_cancel_status
    
    def validate(self, attrs):
        request = self.context.get('request')
        
        # For creation
        if request and request.method == 'POST':
            timeslot_id = self.initial_data.get('timeslot')
            
            if not timeslot_id:
                raise serializers.ValidationError({"timeslot": "This field is required."})
            
            try:
                timeslot = TimeSlot.objects.get(pk=timeslot_id, is_available=True)
            except TimeSlot.DoesNotExist:
                raise serializers.ValidationError({"timeslot": "Timeslot not available or does not exist."})
            
            # Set doctor and patient automatically
            attrs['doctor'] = timeslot.doctor
            attrs['patient'] = request.user
            attrs['timeslot'] = timeslot
            
            # Check if patient already has appointment with this doctor at this time
            existing_appointment = Appointment.objects.filter(
                patient=request.user,
                doctor=timeslot.doctor,
                timeslot=timeslot
            ).exists()
            
            if existing_appointment:
                raise serializers.ValidationError("You already have an appointment with this doctor at this time.")
        
        return attrs
    
    def create(self, validated_data):
        with transaction.atomic():
            appointment = Appointment.objects.create(**validated_data)
            # Timeslot availability will be updated in Appointment.save() method
            return appointment


class AppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('status',)
    
    def validate_status(self, value):
        request = self.context.get('request')
        instance = self.instance
        
        if not request:
            raise serializers.ValidationError("Request context is required.")
        
        if not request.user.is_doctor and not request.user.is_admin:
            raise serializers.ValidationError("Only doctors and admins can change appointment status.")
        
        # Check valid status transitions
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['completed', 'cancelled'],
        }
        
        if instance.status != value:
            if value not in valid_transitions.get(instance.status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from {instance.status} to {value}"
                )
        
        return value


class DoctorTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ('id', 'date', 'start_time', 'end_time', 'is_available')