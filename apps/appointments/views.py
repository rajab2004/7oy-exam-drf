from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import TimeSlot, Appointment
from .serializers import (
    TimeSlotSerializer, AvailableTimeSlotSerializer,
    AppointmentSerializer, AppointmentStatusSerializer,
    DoctorTimeSlotSerializer
)
from .permissions import (
    IsTimeslotOwner, IsAppointmentOwner, CanChangeAppointmentStatus,
    CanCancelAppointment, CanViewDoctorTimeslots, CanCreateAppointment,
    IsDoctorOrReadOnly
)
from apps.users.permissions import IsAdmin, IsDoctor, IsPatient
from apps.users.models import User, DoctorProfile


# TimeSlot Views
class TimeSlotCreateView(generics.CreateAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def perform_create(self, serializer):
        # Automatically set the doctor to the current user
        serializer.save(doctor=self.request.user)


class TimeSlotListView(generics.ListAPIView):
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['date', 'is_available']
    
    def get_queryset(self):
        # Doctors can only see their own timeslots
        return TimeSlot.objects.filter(
            doctor=self.request.user
        ).select_related('doctor').order_by('date', 'start_time')


class TimeSlotDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated, IsTimeslotOwner]
    
    def get_queryset(self):
        return TimeSlot.objects.select_related('doctor')
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if timeslot has an appointment
        if hasattr(instance, 'appointment'):
            return Response(
                {"error": "Cannot delete timeslot with an existing appointment."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# Doctor Available TimeSlots
class DoctorAvailableTimeSlotsView(generics.ListAPIView):
    serializer_class = AvailableTimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewDoctorTimeslots]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']
    
    def get_queryset(self):
        doctor_id = self.kwargs.get('doctor_id')
        doctor = get_object_or_404(User, pk=doctor_id, role='doctor')
        
        # Only show available timeslots in the future
        return TimeSlot.objects.filter(
            doctor=doctor,
            is_available=True,
            date__gte=timezone.now().date()
        ).select_related('doctor', 'doctor__doctor_profile').order_by('date', 'start_time')


# Appointment Views
class AppointmentCreateView(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, CanCreateAppointment]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class MyAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'doctor']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_doctor:
            # Doctors see appointments where they are the doctor
            return Appointment.objects.filter(
                doctor=user
            ).select_related(
                'doctor', 'patient', 'timeslot'
            ).order_by('-created_at')
        
        elif user.is_patient:
            # Patients see their own appointments
            return Appointment.objects.filter(
                patient=user
            ).select_related(
                'doctor', 'patient', 'timeslot'
            ).order_by('-created_at')
        
        elif user.is_admin:
            # Admins see all appointments
            return Appointment.objects.all().select_related(
                'doctor', 'patient', 'timeslot'
            ).order_by('-created_at')
        
        return Appointment.objects.none()


class AppointmentDetailView(generics.RetrieveAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppointmentOwner]
    
    def get_queryset(self):
        return Appointment.objects.select_related(
            'doctor', 'patient', 'timeslot'
        )


class AppointmentStatusUpdateView(generics.UpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentStatusSerializer
    permission_classes = [permissions.IsAuthenticated, CanChangeAppointmentStatus]
    http_method_names = ['patch']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Appointment.objects.all()
        elif user.is_doctor:
            return Appointment.objects.filter(doctor=user)
        return Appointment.objects.none()
    
    def perform_update(self, serializer):
        instance = serializer.save()
        
        # Send notification or log status change
        self.log_status_change(instance)
    
    def log_status_change(self, appointment):
        # Here you can add logging or notification logic
        # For example: send email, push notification, etc.
        pass


class AppointmentCancelView(generics.DestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, CanCancelAppointment]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            return Appointment.objects.all()
        elif user.is_doctor:
            return Appointment.objects.filter(doctor=user)
        elif user.is_patient:
            return Appointment.objects.filter(patient=user)
        
        return Appointment.objects.none()
    
    def perform_destroy(self, instance):
        # Only cancel if appointment is in the future
        appointment_datetime = timezone.datetime.combine(
            instance.timeslot.date, 
            instance.timeslot.start_time
        )
        
        if appointment_datetime <= timezone.now():
            raise ValidationError("Cannot cancel past appointments.")
        
        # Only allow cancellation of pending or confirmed appointments
        if instance.status not in ['pending', 'confirmed']:
            raise ValidationError(f"Cannot cancel appointment with status: {instance.status}")
        
        instance.status = 'cancelled'
        instance.save()


# Admin Views
class AllAppointmentsView(generics.ListAPIView):
    queryset = Appointment.objects.all().select_related(
        'doctor', 'patient', 'timeslot'
    ).order_by('-created_at')
    serializer_class = AppointmentSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'doctor', 'patient']
    search_fields = [
        'doctor__username', 'patient__username',
        'notes', 'symptoms'
    ]


class AllTimeSlotsView(generics.ListAPIView):
    queryset = TimeSlot.objects.all().select_related('doctor')
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['doctor', 'date', 'is_available']


# Utility Views
class AvailableDoctorsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # Get doctors who have available timeslots
        available_doctors = DoctorProfile.objects.filter(
            user__time_slots__is_available=True,
            user__time_slots__date__gte=timezone.now().date()
        ).distinct().select_related('user')
        
        from apps.users.serializers import DoctorListSerializer
        serializer = DoctorListSerializer(available_doctors, many=True)
        return Response(serializer.data)


class TodayAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        today = timezone.now().date()
        
        if user.is_doctor:
            return Appointment.objects.filter(
                doctor=user,
                timeslot__date=today,
                status__in=['pending', 'confirmed']
            ).select_related('patient', 'timeslot').order_by('timeslot__start_time')
        
        elif user.is_patient:
            return Appointment.objects.filter(
                patient=user,
                timeslot__date=today,
                status__in=['pending', 'confirmed']
            ).select_related('doctor', 'timeslot').order_by('timeslot__start_time')
        
        elif user.is_admin:
            return Appointment.objects.filter(
                timeslot__date=today
            ).select_related('doctor', 'patient', 'timeslot').order_by('timeslot__start_time')
        
        return Appointment.objects.none()