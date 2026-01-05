from django.urls import path
from .views import (
    # TimeSlot Views
    TimeSlotCreateView, TimeSlotListView, TimeSlotDetailView,
    
    # Appointment Views
    AppointmentCreateView, MyAppointmentsView, AppointmentDetailView,
    AppointmentStatusUpdateView, AppointmentCancelView,
    
    # Doctor TimeSlots
    DoctorAvailableTimeSlotsView,
    
    # Admin Views
    AllAppointmentsView, AllTimeSlotsView,
    
    # Utility Views
    AvailableDoctorsView, TodayAppointmentsView,
)

urlpatterns = [
    # TimeSlots
    path('timeslots/', TimeSlotCreateView.as_view(), name='timeslot_create'),
    path('timeslots/my/', TimeSlotListView.as_view(), name='my_timeslots'),
    path('timeslots/<int:pk>/', TimeSlotDetailView.as_view(), name='timeslot_detail'),
    
    # Doctor Available TimeSlots
    path('doctors/<int:doctor_id>/timeslots/', 
         DoctorAvailableTimeSlotsView.as_view(), 
         name='doctor_timeslots'),
    
    # Appointments
    path('appointments/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointments/me/', MyAppointmentsView.as_view(), name='my_appointments'),
    path('appointments/today/', TodayAppointmentsView.as_view(), name='today_appointments'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<int:pk>/status/', 
         AppointmentStatusUpdateView.as_view(), 
         name='appointment_status_update'),
    path('appointments/<int:pk>/cancel/', 
         AppointmentCancelView.as_view(), 
         name='appointment_cancel'),
    
    # Available Doctors
    path('doctors/available/', AvailableDoctorsView.as_view(), name='available_doctors'),
    
    # Admin only endpoints
    path('admin/appointments/', AllAppointmentsView.as_view(), name='all_appointments'),
    path('admin/timeslots/', AllTimeSlotsView.as_view(), name='all_timeslots'),
]