from rest_framework import generics, permissions
from .models import DoctorProfile, TimeSlot
from .serializers import DoctorProfileSerializer, TimeSlotSerializer
from apps.users.permissions import IsDoctor

class DoctorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get_object(self):
        return self.request.user.doctorprofile

class TimeSlotCreateView(generics.CreateAPIView):
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user.doctorprofile)

class TimeSlotListView(generics.ListAPIView):
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get_queryset(self):
        return TimeSlot.objects.filter(doctor=self.request.user.doctorprofile)
