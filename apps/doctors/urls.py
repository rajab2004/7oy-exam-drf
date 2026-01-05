from django.urls import path
from .views import DoctorProfileView, TimeSlotCreateView, TimeSlotListView

urlpatterns = [
    path("profile/", DoctorProfileView.as_view()),
    path("timeslots/", TimeSlotListView.as_view()),
    path("timeslots/create/", TimeSlotCreateView.as_view()),
]

