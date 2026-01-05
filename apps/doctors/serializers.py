from rest_framework import serializers
from .models import DoctorProfile, TimeSlot
from apps.users.serializers import UserSerializer

class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = "__all__"

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = "__all__"

    def validate(self, data):
        # Overlap check
        doctor = data["doctor"]
        date = data["date"]
        start = data["start_time"]
        end = data["end_time"]
        overlapping = TimeSlot.objects.filter(
            doctor=doctor, date=date,
            start_time__lt=end, end_time__gt=start
        )
        if overlapping.exists():
            raise serializers.ValidationError("TimeSlot overlaps with existing slot")
        return data
