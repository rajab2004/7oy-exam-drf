from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.users.models import User


class TimeSlot(models.Model):
    doctor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='time_slots',
        limit_choices_to={'role': 'doctor'}
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['doctor', 'date', 'start_time', 'end_time']
    
    def __str__(self):
        return f"{self.doctor.username} - {self.date} {self.start_time}-{self.end_time}"
    
    def clean(self):
        # Check if start_time is before end_time
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")
        
        # Check if date is in the past
        if self.date < timezone.now().date():
            raise ValidationError("Cannot create time slot in the past.")
        
        # Check for overlapping time slots for the same doctor
        overlapping_slots = TimeSlot.objects.filter(
            doctor=self.doctor,
            date=self.date,
            is_available=True
        ).exclude(pk=self.pk)  # Exclude self when updating
        
        for slot in overlapping_slots:
            if (self.start_time < slot.end_time and self.end_time > slot.start_time):
                raise ValidationError(
                    f"Time slot overlaps with existing slot: "
                    f"{slot.start_time}-{slot.end_time}"
                )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'
    
    doctor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='doctor_appointments',
        limit_choices_to={'role': 'doctor'}
    )
    patient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='patient_appointments',
        limit_choices_to={'role': 'patient'}
    )
    timeslot = models.OneToOneField(
        TimeSlot, 
        on_delete=models.CASCADE, 
        related_name='appointment'
    )
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )
    notes = models.TextField(blank=True)
    symptoms = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['doctor', 'patient', 'timeslot']
    
    def __str__(self):
        return f"Appointment #{self.id} - {self.patient.username} with Dr. {self.doctor.username}"
    
    def clean(self):
        # Prevent doctor from booking appointment with themselves
        if self.doctor == self.patient:
            raise ValidationError("Doctors cannot book appointments with themselves.")
        
        # Check if timeslot belongs to the doctor
        if self.timeslot.doctor != self.doctor:
            raise ValidationError("Timeslot does not belong to the selected doctor.")
        
        # Check if timeslot is available
        if not self.timeslot.is_available and not self.pk:
            raise ValidationError("This timeslot is already booked.")
        
        # Check if appointment is in the past
        appointment_datetime = timezone.datetime.combine(
            self.timeslot.date, 
            self.timeslot.start_time
        )
        if appointment_datetime < timezone.now():
            raise ValidationError("Cannot book appointment in the past.")
        
        # Status validation rules
        if self.pk:  # Only for updates
            old_appointment = Appointment.objects.get(pk=self.pk)
            
            # Only allow specific status transitions
            allowed_transitions = {
                'pending': ['confirmed', 'cancelled'],
                'confirmed': ['completed', 'cancelled'],
                'cancelled': [],  # Cannot change from cancelled
                'completed': [],  # Cannot change from completed
            }
            
            if old_appointment.status != self.status:
                if self.status not in allowed_transitions.get(old_appointment.status, []):
                    raise ValidationError(
                        f"Cannot change status from {old_appointment.status} to {self.status}"
                    )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = self.pk is None
        
        # If appointment is being created, mark timeslot as unavailable
        if is_new:
            self.timeslot.is_available = False
            self.timeslot.save()
        
        # If appointment is cancelled, mark timeslot as available
        elif self.status == 'cancelled':
            old_appointment = Appointment.objects.get(pk=self.pk)
            if old_appointment.status != 'cancelled':
                self.timeslot.is_available = True
                self.timeslot.save()
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # When deleting appointment, mark timeslot as available
        self.timeslot.is_available = True
        self.timeslot.save()
        super().delete(*args, **kwargs)