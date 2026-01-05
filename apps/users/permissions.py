from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_doctor
    
    def has_object_permission(self, request, view, obj):
        # Doktor faqat o'ziga tegishli ma'lumotlarni o'zgartira oladi
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'doctor'):
            return obj.doctor == request.user
        return False


class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_patient
    
    def has_object_permission(self, request, view, obj):
        # Patient faqat o'ziga tegishli ma'lumotlarni o'zgartira oladi
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'patient'):
            return obj.patient == request.user
        return False


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Object user bilan bog'langan bo'lsa
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Object doctor bilan bog'langan bo'lsa
        if hasattr(obj, 'doctor'):
            return obj.doctor == request.user
        # Object patient bilan bog'langan bo'lsa
        if hasattr(obj, 'patient'):
            return obj.patient == request.user
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'doctor'):
            return obj.doctor == request.user
        if hasattr(obj, 'patient'):
            return obj.patient == request.user
        return False


class IsAdminOrDoctorReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated and (request.user.is_admin or request.user.is_doctor)
        return request.user.is_authenticated and request.user.is_admin