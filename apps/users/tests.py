from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import DoctorProfile, PatientProfile

User = get_user_model()


class UserModelTests(TestCase):
    """User model testlari"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='testpass123',
            email='admin@test.com',
            role='admin'
        )
        
        self.doctor_user = User.objects.create_user(
            username='doctor_user',
            password='testpass123',
            email='doctor@test.com',
            role='doctor',
            phone='+998901234567'
        )
        
        self.patient_user = User.objects.create_user(
            username='patient_user',
            password='testpass123',
            email='patient@test.com',
            role='patient',
            phone='+998901234568'
        )
    
    def test_user_creation(self):
        """User yaratish testi"""
        self.assertEqual(self.admin_user.username, 'admin_user')
        self.assertEqual(self.admin_user.role, 'admin')
        self.assertTrue(self.admin_user.is_admin)
        self.assertFalse(self.admin_user.is_doctor)
        self.assertFalse(self.admin_user.is_patient)
        
        self.assertEqual(self.doctor_user.username, 'doctor_user')
        self.assertEqual(self.doctor_user.role, 'doctor')
        self.assertTrue(self.doctor_user.is_doctor)
        
        self.assertEqual(self.patient_user.username, 'patient_user')
        self.assertEqual(self.patient_user.role, 'patient')
        self.assertTrue(self.patient_user.is_patient)
    
    def test_user_str_method(self):
        """__str__ method testi"""
        self.assertEqual(str(self.admin_user), 'admin_user (admin)')
        self.assertEqual(str(self.doctor_user), 'doctor_user (doctor)')
        self.assertEqual(str(self.patient_user), 'patient_user (patient)')
    
    def test_user_manager_create_user(self):
        """Custom user manager testi"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com',
            role='patient'
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'patient')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_create_superuser(self):
        """Superuser yaratish testi"""
        superuser = User.objects.create_superuser(
            username='superuser',
            password='superpass123',
            email='super@test.com'
        )
        
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_active)
        self.assertEqual(superuser.role, 'admin')


class DoctorProfileModelTests(TestCase):
    """DoctorProfile model testlari"""
    
    def setUp(self):
        self.doctor_user = User.objects.create_user(
            username='test_doctor',
            password='testpass123',
            email='doctor@test.com',
            role='doctor'
        )
        
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='cardiology',
            experience_years=5,
            gender='male',
            bio='Experienced cardiologist',
            consultation_fee=50.00
        )
    
    def test_doctor_profile_creation(self):
        """DoctorProfile yaratish testi"""
        self.assertEqual(self.doctor_profile.user, self.doctor_user)
        self.assertEqual(self.doctor_profile.specialization, 'cardiology')
        self.assertEqual(self.doctor_profile.experience_years, 5)
        self.assertEqual(self.doctor_profile.gender, 'male')
        self.assertEqual(self.doctor_profile.consultation_fee, 50.00)
    
    def test_doctor_profile_str_method(self):
        """DoctorProfile __str__ method testi"""
        self.doctor_user.first_name = 'John'
        self.doctor_user.last_name = 'Doe'
        self.doctor_user.save()
        
        expected_str = f"Dr. John Doe - cardiology"
        self.assertEqual(str(self.doctor_profile), expected_str)
        
        # Agar ism bo'lmasa
        self.doctor_user.first_name = ''
        self.doctor_user.last_name = ''
        self.doctor_user.save()
        self.doctor_profile.refresh_from_db()
        
        expected_str = f"Dr. test_doctor - cardiology"
        self.assertEqual(str(self.doctor_profile), expected_str)


class PatientProfileModelTests(TestCase):
    """PatientProfile model testlari"""
    
    def setUp(self):
        self.patient_user = User.objects.create_user(
            username='test_patient',
            password='testpass123',
            email='patient@test.com',
            role='patient'
        )
        
        self.patient_profile = PatientProfile.objects.create(
            user=self.patient_user,
            date_of_birth='1990-01-01',
            gender='female',
            address='123 Test Street',
            emergency_contact='+998901234569',
            blood_type='A+',
            allergies='Penicillin'
        )
    
    def test_patient_profile_creation(self):
        """PatientProfile yaratish testi"""
        self.assertEqual(self.patient_profile.user, self.patient_user)
        self.assertEqual(str(self.patient_profile.date_of_birth), '1990-01-01')
        self.assertEqual(self.patient_profile.gender, 'female')
        self.assertEqual(self.patient_profile.address, '123 Test Street')
        self.assertEqual(self.patient_profile.blood_type, 'A+')
    
    def test_patient_profile_age_property(self):
        """PatientProfile age property testi"""
        # Bu test yilga qarab natija berishi mumkin
        # Faqat property ishlashini tekshiramiz
        age = self.patient_profile.age
        self.assertIsInstance(age, int)
        self.assertGreater(age, 20)  # 1990 yilda tug'ilgan
    
    def test_patient_profile_str_method(self):
        """PatientProfile __str__ method testi"""
        self.patient_user.first_name = 'Jane'
        self.patient_user.last_name = 'Smith'
        self.patient_user.save()
        
        expected_str = 'Jane Smith'
        self.assertEqual(str(self.patient_profile), expected_str)
        
        # Agar ism bo'lmasa
        self.patient_user.first_name = ''
        self.patient_user.last_name = ''
        self.patient_user.save()
        self.patient_profile.refresh_from_db()
        
        expected_str = 'test_patient'
        self.assertEqual(str(self.patient_profile), expected_str)


class AuthenticationAPITests(APITestCase):
    """Authentication API testlari"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.refresh_url = reverse('token_refresh')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('user_profile')
        
        self.patient_data = {
            'username': 'new_patient',
            'password': 'testpass123',
            'password2': 'testpass123',
            'email': 'newpatient@test.com',
            'role': 'patient',
            'phone': '+998901234567',
            'date_of_birth': '1995-05-15',
            'patient_gender': 'male'
        }
        
        self.doctor_data = {
            'username': 'new_doctor',
            'password': 'testpass123',
            'password2': 'testpass123',
            'email': 'newdoctor@test.com',
            'role': 'doctor',
            'phone': '+998901234568',
            'specialization': 'cardiology',
            'experience_years': 5,
            'doctor_gender': 'female',
            'bio': 'Experienced doctor',
            'consultation_fee': 75.00
        }
        
        self.login_data = {
            'username': 'new_patient',
            'password': 'testpass123'
        }
    
    def test_register_patient_success(self):
        """Patient ro'yxatdan o'tish testi"""
        response = self.client.post(self.register_url, self.patient_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'new_patient')
        self.assertEqual(user_data['role'], 'patient')
        
        # PatientProfile yaratilganligini tekshirish
        user = User.objects.get(username='new_patient')
        self.assertTrue(hasattr(user, 'patient_profile'))
        self.assertEqual(user.patient_profile.gender, 'male')
    
    def test_register_doctor_success(self):
        """Doctor ro'yxatdan o'tish testi"""
        response = self.client.post(self.register_url, self.doctor_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # DoctorProfile yaratilganligini tekshirish
        user = User.objects.get(username='new_doctor')
        self.assertTrue(hasattr(user, 'doctor_profile'))
        self.assertEqual(user.doctor_profile.specialization, 'cardiology')
        self.assertEqual(user.doctor_profile.experience_years, 5)
    
    def test_register_with_missing_fields(self):
        """Majburiy maydonlar bo'lmasa register testi"""
        invalid_data = {
            'username': 'testuser',
            'password': 'test123',
            'password2': 'test123',
            'email': 'test@test.com',
            'role': 'patient'
            # date_of_birth va gender yo'q
        }
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date_of_birth', response.data)
        self.assertIn('patient_gender', response.data)
    
    def test_register_password_mismatch(self):
        """Noto'g'ri parol tasdiqlash testi"""
        invalid_data = self.patient_data.copy()
        invalid_data['password2'] = 'differentpassword'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_login_success(self):
        """Login muvaffaqiyatli testi"""
        # Avval ro'yxatdan o'tamiz
        self.client.post(self.register_url, self.patient_data, format='json')
        
        # Endi login qilamiz
        response = self.client.post(self.login_url, self.login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Noto'g'ri login testi"""
        invalid_data = {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_token_refresh(self):
        """Token refresh testi"""
        # Ro'yxatdan o'tish va login
        self.client.post(self.register_url, self.patient_data, format='json')
        login_response = self.client.post(self.login_url, self.login_data, format='json')
        
        refresh_token = login_response.data['refresh']
        
        # Token yangilash
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_get_profile_authenticated(self):
        """Autentifikatsiyadan o'tgan foydalanuvchi profili testi"""
        # Ro'yxatdan o'tish va login
        self.client.post(self.register_url, self.patient_data, format='json')
        login_response = self.client.post(self.login_url, self.login_data, format='json')
        
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'new_patient')
    
    def test_get_profile_unauthenticated(self):
        """Autentifikatsiyadan o'tmagan foydalanuvchi profili testi"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DoctorProfileAPITests(APITestCase):
    """DoctorProfile API testlari"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Doctor yaratish
        self.doctor_user = User.objects.create_user(
            username='doctor_user',
            password='testpass123',
            email='doctor@test.com',
            role='doctor'
        )
        
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='cardiology',
            experience_years=5,
            gender='male',
            bio='Test bio',
            consultation_fee=50.00
        )
        
        # Patient yaratish (boshqa roldagi foydalanuvchi)
        self.patient_user = User.objects.create_user(
            username='patient_user',
            password='testpass123',
            email='patient@test.com',
            role='patient'
        )
        
        # URLlar
        self.doctor_profile_url = reverse('doctor_profile')
        self.doctor_list_url = reverse('doctor_list')
        self.doctor_detail_url = reverse('doctor_detail', args=[self.doctor_profile.id])
        
        # Doctor uchun token
        refresh = RefreshToken.for_user(self.doctor_user)
        self.doctor_access_token = str(refresh.access_token)
        
        # Patient uchun token
        refresh = RefreshToken.for_user(self.patient_user)
        self.patient_access_token = str(refresh.access_token)
    
    def test_get_doctor_profile_authenticated_doctor(self):
        """Doctor o'z profilini ko'ra olishi testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.doctor_access_token}')
        
        response = self.client.get(self.doctor_profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['specialization'], 'cardiology')
        self.assertEqual(response.data['experience_years'], 5)
    
    def test_get_doctor_profile_unauthenticated(self):
        """Autentifikatsiyadan o'tmagan foydalanuvchi doctor profilini ko'ra olmasligi"""
        response = self.client.get(self.doctor_profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_doctor_profile_as_patient(self):
        """Patient doctor profilini ko'ra olmasligi testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_access_token}')
        
        response = self.client.get(self.doctor_profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_doctor_profile(self):
        """Doctor o'z profilini yangilashi testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.doctor_access_token}')
        
        update_data = {
            'bio': 'Updated bio',
            'consultation_fee': 75.00
        }
        
        response = self.client.patch(self.doctor_profile_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio')
        self.assertEqual(response.data['consultation_fee'], '75.00')
        
        # Database da yangilanganligini tekshirish
        self.doctor_profile.refresh_from_db()
        self.assertEqual(self.doctor_profile.bio, 'Updated bio')
        self.assertEqual(self.doctor_profile.consultation_fee, 75.00)
    
    def test_doctor_list_accessible_to_all_authenticated(self):
        """Doctorlar ro'yxati barcha autentifikatsiyadan o'tganlarga ochiq testi"""
        # Patient sifatida
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_access_token}')
        response = self.client.get(self.doctor_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        # Doctor sifatida
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.doctor_access_token}')
        response = self.client.get(self.doctor_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_doctor_list_search_filter(self):
        """Doctorlar ro'yxatida qidiruv va filtr testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_access_token}')
        
        # Qidiruv testi
        response = self.client.get(f'{self.doctor_list_url}?search=cardiology')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Filtr testi
        response = self.client.get(f'{self.doctor_list_url}?specialization=cardiology')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_doctor_detail_view(self):
        """Doctor detail ko'rish testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_access_token}')
        
        response = self.client.get(self.doctor_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.doctor_profile.id)
        self.assertEqual(response.data['specialization'], 'cardiology')


class PatientProfileAPITests(APITestCase):
    """PatientProfile API testlari"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Patient yaratish
        self.patient_user = User.objects.create_user(
            username='patient_user',
            password='testpass123',
            email='patient@test.com',
            role='patient'
        )
        
        self.patient_profile = PatientProfile.objects.create(
            user=self.patient_user,
            date_of_birth='1990-01-01',
            gender='female',
            address='123 Test Street',
            emergency_contact='+998901234569',
            blood_type='A+',
            allergies='Penicillin'
        )
        
        # Doctor yaratish (boshqa roldagi foydalanuvchi)
        self.doctor_user = User.objects.create_user(
            username='doctor_user',
            password='testpass123',
            email='doctor@test.com',
            role='doctor'
        )
        
        # URL
        self.patient_profile_url = reverse('patient_profile')
        
        # Patient uchun token
        refresh = RefreshToken.for_user(self.patient_user)
        self.patient_access_token = str(refresh.access_token)
        
        # Doctor uchun token
        refresh = RefreshToken.for_user(self.doctor_user)
        self.doctor_access_token = str(refresh.access_token)
    
    def test_get_patient_profile_authenticated_patient(self):
        """Patient o'z profilini ko'ra olishi testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_access_token}')
        
        response = self.client.get(self.patient_profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['gender'], 'female')
        self.assertEqual(response.data['blood_type'], 'A+')
        self.assertIn('age', response.data)  # Computed field
    
    def test_get_patient_profile_as_doctor(self):
        """Doctor patient profilini ko'ra olmasligi testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.doctor_access_token}')
        
        response = self.client.get(self.patient_profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_patient_profile(self):
        """Patient o'z profilini yangilashi testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_access_token}')
        
        update_data = {
            'address': '456 New Street',
            'emergency_contact': '+998901234570',
            'allergies': 'Aspirin, Penicillin'
        }
        
        response = self.client.patch(self.patient_profile_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['address'], '456 New Street')
        self.assertEqual(response.data['allergies'], 'Aspirin, Penicillin')
        
        # Database da yangilanganligini tekshirish
        self.patient_profile.refresh_from_db()
        self.assertEqual(self.patient_profile.address, '456 New Street')
        self.assertEqual(self.patient_profile.allergies, 'Aspirin, Penicillin')


class AdminUserAPITests(APITestCase):
    """Admin user API testlari"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Admin yaratish
        self.admin_user = User.objects.create_superuser(
            username='admin_user',
            password='adminpass123',
            email='admin@test.com'
        )
        
        # Doctor yaratish
        self.doctor_user = User.objects.create_user(
            username='doctor_user',
            password='testpass123',
            email='doctor@test.com',
            role='doctor'
        )
        
        # Patient yaratish
        self.patient_user = User.objects.create_user(
            username='patient_user',
            password='testpass123',
            email='patient@test.com',
            role='patient'
        )
        
        # URLlar
        self.user_list_url = reverse('user_list')
        self.user_detail_url = reverse('user_detail', args=[self.doctor_user.id])
        
        # Admin uchun token
        refresh = RefreshToken.for_user(self.admin_user)
        self.admin_access_token = str(refresh.access_token)
        
        # Doctor uchun token
        refresh = RefreshToken.for_user(self.doctor_user)
        self.doctor_access_token = str(refresh.access_token)
    
    def test_admin_can_view_all_users(self):
        """Admin barcha foydalanuvchilarni ko'ra olishi testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_access_token}')
        
        response = self.client.get(self.user_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_doctor_cannot_view_all_users(self):
        """Doctor barcha foydalanuvchilarni ko'ra olmasligi testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.doctor_access_token}')
        
        response = self.client.get(self.user_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_view_user_detail(self):
        """Admin foydalanuvchi detallarini ko'ra olishi testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_access_token}')
        
        response = self.client.get(self.user_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'doctor_user')
    
    def test_admin_can_update_user(self):
        """Admin foydalanuvchini yangilashi testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_access_token}')
        
        update_data = {
            'email': 'updated@test.com',
            'phone': '+998901234571'
        }
        
        response = self.client.patch(self.user_detail_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'updated@test.com')
        
        # Database da yangilanganligini tekshirish
        self.doctor_user.refresh_from_db()
        self.assertEqual(self.doctor_user.email, 'updated@test.com')
    
    def test_admin_can_delete_user(self):
        """Admin foydalanuvchini o'chirishi testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_access_token}')
        
        # Yangi foydalanuvchi yaratish o'chirish uchun
        new_user = User.objects.create_user(
            username='todelete',
            password='testpass123',
            email='delete@test.com',
            role='patient'
        )
        
        delete_url = reverse('user_detail', args=[new_user.id])
        response = self.client.delete(delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Foydalanuvchi database dan o'chganligini tekshirish
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='todelete')
    
    def test_user_list_filter_search(self):
        """Userlar ro'yxatida filtr va qidiruv testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_access_token}')
        
        # Role bo'yicha filtr
        response = self.client.get(f'{self.user_list_url}?role=doctor')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Qidiruv
        response = self.client.get(f'{self.user_list_url}?search=doctor')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PermissionTests(APITestCase):
    """Permission testlari"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Turli rollardagi foydalanuvchilar yaratish
        self.admin_user = User.objects.create_superuser(
            username='admin_user',
            password='adminpass123',
            email='admin@test.com'
        )
        
        self.doctor_user = User.objects.create_user(
            username='doctor_user',
            password='testpass123',
            email='doctor@test.com',
            role='doctor'
        )
        
        self.patient_user = User.objects.create_user(
            username='patient_user',
            password='testpass123',
            email='patient@test.com',
            role='patient'
        )
        
        # Tokenlar
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.doctor_token = str(RefreshToken.for_user(self.doctor_user).access_token)
        self.patient_token = str(RefreshToken.for_user(self.patient_user).access_token)
    
    def test_is_admin_permission(self):
        """IsAdmin permission testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.doctor_token}')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_token}')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_is_doctor_permission(self):
        """IsDoctor permission testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.doctor_token}')
        response = self.client.get(reverse('doctor_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_token}')
        response = self.client.get(reverse('doctor_profile'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_is_patient_permission(self):
        """IsPatient permission testi"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_token}')
        response = self.client.get(reverse('patient_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.doctor_token}')
        response = self.client.get(reverse('patient_profile'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ValidationTests(TestCase):
    """Validation testlari"""
    
    def test_phone_validation(self):
        """Telefon raqami validatsiyasi testi"""
        # To'g'ri format
        user = User(username='testuser', email='test@test.com', role='patient')
        user.phone = '+998901234567'
        user.full_clean()  # Validation o'tishi kerak
        
        # Noto'g'ri format
        user.phone = '12345'
        with self.assertRaises(Exception):
            user.full_clean()
    
    def test_email_required(self):
        """Email majburiy maydon testi"""
        user = User(username='testuser', role='patient')
        with self.assertRaises(Exception):
            user.full_clean()  # Email bo'lmasa xato



class IntegrationTests(APITestCase):
    """Integration testlari"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Doctor yaratish
        self.doctor_user = User.objects.create_user(
            username='integration_doctor',
            password='testpass123',
            email='doctor@integration.com',
            role='doctor'
        )
        
        DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='neurology',
            experience_years=8,
            gender='male'
        )
        
        # Patient yaratish
        self.patient_user = User.objects.create_user(
            username='integration_patient',
            password='testpass123',
            email='patient@integration.com',
            role='patient'
        )
        
        PatientProfile.objects.create(
            user=self.patient_user,
            date_of_birth='1992-03-15',
            gender='female'
        )
        
        # Tokenlar
        self.doctor_token = str(RefreshToken.for_user(self.doctor_user).access_token)
        self.patient_token = str(RefreshToken.for_user(self.patient_user).access_token)
    
    def test_complete_user_workflow(self):
        """To'liq user workflow testi"""
        # 1. Patient doctorlar ro'yxatini ko'radi
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.patient_token}')
        response = self.client.get(reverse('doctor_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. Patient o'z profilini ko'radi
        response = self.client.get(reverse('patient_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Doctor o'z profilini ko'radi
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.doctor_token}')
        response = self.client.get(reverse('doctor_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Doctor o'z profilini yangilaydi
        update_data = {'bio': 'Integration test bio'}
        response = self.client.patch(reverse('doctor_profile'), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Integration test bio')