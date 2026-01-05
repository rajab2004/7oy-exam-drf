# 🏥 FINAL EXAM PROJECT

## **Clinic Appointment Booking API**

### ⏱ Muddati: **24 soat**

### 🎯 Maqsad:

Talabaning **real backend loyiha** ustida ishlash ko‘nikmalarini baholash:

* REST API dizayn
* Authentication & Authorization (JWT, Permission)
* Business Logic & Validation
* Performance (ORM optimizatsiya)
* API hujjatlashtirish

---

## 1️⃣ TEXNOLOGIYALAR (MAJBURIY)

Talaba quyidagi texnologiyalarni **to‘liq va to‘g‘ri** ishlatishi shart:

* Python 3.x
* Django
* Django Rest Framework (DRF)
* JWT Authentication (`djangorestframework-simplejwt`)
* PostgreSQL
* Swagger / Redoc (`drf-spectacular`)
* `.env` (environment variables)
* Git + GitHub (public repository)

❗ *Kod sifati, commitlar va project structure baholanadi.*

---

## 2️⃣ FOYDALANUVCHI ROLLARI

| Role        | Tavsif                                             |
| ----------- | -------------------------------------------------- |
| **Admin**   | Tizimdagi barcha ma’lumotlarni boshqaradi          |
| **Doctor**  | O‘z ish jadvali va appointmentlarini boshqaradi    |
| **Patient** | Doctor qabuliga yoziladi (appointment bron qiladi) |

---

## 3️⃣ MA’LUMOTLAR MODELLARI

### 👤 User (Custom User)

```text
id
username
password
role (admin / doctor / patient)
is_active
created_at
```

---

### 👨‍⚕️ DoctorProfile

```text
id
user (OneToOne → User)
specialization
experience_years
gender
```

---

### 🧑‍🦱 PatientProfile

```text
id
user (OneToOne → User)
phone
date_of_birth
gender
```

---

### ⏰ TimeSlot - doktor har kuni ish boshlashdan oldin kunlik timeslot lar yaratadi, bemorlar shu slot larni tanlaydi.

![](https://docs.cronofy.com/developers/ui-elements/date-time-picker/date-time-picker-preview.2466cce51cf6287df2db9c1820b14cc44f2737220729527de2fce66035016f68.png)

```text
id
doctor (ForeignKey → User/DoctorProfile)
date
start_time
end_time
is_available
```

📌 *Doctor qabul uchun ochgan vaqt oralig‘i.*

---

### 📅 Appointment

```text
id
doctor (FK)
patient (FK)
timeslot (OneToOne)
status (pending / confirmed / cancelled)
created_at
```

---

## 4️⃣ FUNKSIONAL TALABLAR

### 🔐 Authentication & Authorization

* User register (role bilan)
* Login
* JWT access & refresh token
* Role-based permission

---

### 🧑‍⚕️ Doctor imkoniyatlari

* O‘ziga tegishli **TimeSlot** yaratish
* Faqat **o‘z appointmentlarini** ko‘rish
* Appointment statusini o‘zgartirish:

  * `pending → confirmed`
  * `pending → cancelled`

❌ Boshqa doctor ma’lumotlariga kirish taqiqlanadi

---

### 🧑‍🦱 Patient imkoniyatlari

* Doctorlar ro‘yxatini ko‘rish
* Doctor bo‘yicha bo‘sh TimeSlotlarni ko‘rish
* Appointment bron qilish
* O‘z appointmentini bekor qilish

❌ Boshqa patient appointmentlarini ko‘ra olmaydi

---

### 🛡 Admin imkoniyatlari

* Doctor va Patient CRUD
* Barcha appointmentlarni ko‘rish
* Tizim ustidan to‘liq nazorat

---

## 5️⃣ BUSINESS LOGIC (ASOSIY BAHOLANADIGAN QISM)

Quyidagi **validation va mantiqiy shartlar** majburiy:

### ✅ Validation Rules

* ❌ Doctor uchun TimeSlot’lar **bir-birini qoplamasligi** kerak (overlap)
* ❌ Bitta TimeSlot faqat **1 ta appointment** bilan bog‘lanadi
* ❌ O‘tmishdagi vaqtga appointment bron qilish mumkin emas
* ✅ Appointment `cancelled` bo‘lsa → TimeSlot yana `is_available = true`
* ❌ Doctor o‘ziga appointment bron qila olmaydi

---

## 6️⃣ PERMISSION TALABLARI

Quyidagi custom permission’lar bo‘lishi shart:

* `IsAdmin`
* `IsDoctor`
* `IsPatient`
* `IsOwner`

📌 Misollar:

* Doctor → faqat **o‘z appointmentlari**
* Patient → faqat **o‘z appointmentlari**
* Admin → hammasi

---

## 7️⃣ API ENDPOINTLAR (MINIMUM REQUIREMENT)

```http
POST   /auth/register/
POST   /auth/login/
POST   /auth/token/refresh/

GET    /doctors/
GET    /doctors/{id}/timeslots/

POST   /timeslots/              (Doctor)
POST   /appointments/           (Patient)
GET    /appointments/me/
PATCH  /appointments/{id}/
DELETE /appointments/{id}/
```

---

## 8️⃣ QO‘SHIMCHA TALABLAR (PLUS BALL)

* Pagination
* Filtering:

  * doctor
  * date
  * status
* Search:

  * doctor name
  * specialization
* Serializer level validation
* `select_related` / `prefetch_related` ishlatilgan bo‘lishi shart
* Clean architecture (views, serializers, permissions ajratilgan)

---

## 9️⃣ SWAGGER & README (MAJBURIY)

### Swagger:

* Barcha endpointlar hujjatlashtirilgan
* Request / Response example’lar

### README ichida bo‘lishi shart:

* Project setup (local ishga tushirish)
* `.env.example`
* Migration & superuser yaratish
* API’dan foydalanish tartibi
* Role’lar va ularning imkoniyatlari

---

```
clinic_api/
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── permissions.py
│   ├── doctors/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   ├── appointments/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
├── core/
│   ├── settings.py
│   ├── urls.py
├── .env.example
├── requirements.txt
├── README.md
```

## 📌 ALL ENDPOINTS (FULL LIST)

**Base URL**

```text
/api
```

**Authentication**

```http
Authorization: Bearer <access_token>
```

---

## 🔐 AUTHENTICATION & USER

| Method | Endpoint               | Description                                      | Access |
| ------ | ---------------------- | ------------------------------------------------ | ------ |
| POST   | `/auth/register/`      | Yangi user (doctor/patient) ro‘yxatdan o‘tkazish | Public |
| POST   | `/auth/login/`         | Login va JWT token olish                         | Public |
| POST   | `/auth/token/refresh/` | Access tokenni yangilash                         | Auth   |
| GET    | `/auth/me/`            | Joriy user ma’lumotlari                          | Auth   |

---

## 👤 USERS (ADMIN)

| Method | Endpoint       | Description             | Access |
| ------ | -------------- | ----------------------- | ------ |
| GET    | `/users/`      | Barcha userlar ro‘yxati | Admin  |
| GET    | `/users/{id}/` | User detail             | Admin  |
| PATCH  | `/users/{id}/` | Userni yangilash        | Admin  |
| DELETE | `/users/{id}/` | Userni o‘chirish        | Admin  |

---

## 👨‍⚕️ DOCTORS

| Method | Endpoint                   | Description                   | Access         |
| ------ | -------------------------- | ----------------------------- | -------------- |
| GET    | `/doctors/`                | Doctorlar ro‘yxati            | Patient, Admin |
| GET    | `/doctors/{id}/`           | Doctor detail                 | Patient, Admin |
| GET    | `/doctors/{id}/timeslots/` | Doctorning bo‘sh TimeSlotlari | Patient, Admin |

🔍 Search & filter:

```text
/doctors/?search=cardio
```

---

## 🧑‍⚕️ DOCTOR PROFILE

| Method | Endpoint           | Description        | Access |
| ------ | ------------------ | ------------------ | ------ |
| GET    | `/doctor/profile/` | O‘z doctor profili | Doctor |
| PATCH  | `/doctor/profile/` | Profilni yangilash | Doctor |

---

## 🧑‍🦱 PATIENT PROFILE

| Method | Endpoint            | Description         | Access  |
| ------ | ------------------- | ------------------- | ------- |
| GET    | `/patient/profile/` | O‘z patient profili | Patient |
| PATCH  | `/patient/profile/` | Profilni yangilash  | Patient |

---

## ⏰ TIMESLOTS (DOCTOR SCHEDULE)

| Method | Endpoint           | Description          | Access |
| ------ | ------------------ | -------------------- | ------ |
| POST   | `/timeslots/`      | TimeSlot yaratish    | Doctor |
| GET    | `/timeslots/`      | O‘z TimeSlotlari     | Doctor |
| GET    | `/timeslots/{id}/` | TimeSlot detail      | Doctor |
| DELETE | `/timeslots/{id}/` | TimeSlotni o‘chirish | Doctor |

📌 Qoidalar:

* Faqat o‘z TimeSlotlari
* Band qilingan TimeSlot o‘chirilmaydi

---

## 📅 APPOINTMENTS

### Appointment CRUD

| Method | Endpoint              | Description                | Access          |
| ------ | --------------------- | -------------------------- | --------------- |
| POST   | `/appointments/`      | Appointment bron qilish    | Patient         |
| GET    | `/appointments/me/`   | Mening appointmentlarim    | Doctor, Patient |
| GET    | `/appointments/`      | Barcha appointmentlar      | Admin           |
| GET    | `/appointments/{id}/` | Appointment detail         | Owner, Admin    |
| PATCH  | `/appointments/{id}/` | Statusni o‘zgartirish      | Doctor, Admin   |
| DELETE | `/appointments/{id}/` | Appointmentni bekor qilish | Patient, Admin  |

---

## 📊 FILTER & QUERY PARAMS

### Appointments

```text
/appointments/me/?status=pending
/appointments/me/?date=2026-01-10
/appointments/?doctor=1
```

### TimeSlots

```text
/timeslots/?date=2026-01-10
/doctors/1/timeslots/?date=2026-01-10
```

---

## 🛡 ROLE–ENDPOINT MATRIX (QISQA)

| Endpoint                  | Admin | Doctor | Patient |
| ------------------------- | ----- | ------ | ------- |
| Auth (login/register)     | ✅     | ✅      | ✅       |
| Users CRUD                | ✅     | ❌      | ❌       |
| Doctors list              | ✅     | ❌      | ✅       |
| Doctor profile            | ❌     | ✅      | ❌       |
| Patient profile           | ❌     | ❌      | ✅       |
| Create TimeSlot           | ✅     | ✅      | ❌       |
| View own TimeSlots        | ❌     | ✅      | ❌       |
| Create Appointment        | ✅     | ❌      | ✅       |
| My Appointments           | ✅     | ✅      | ✅       |
| Change Appointment Status | ✅     | ✅      | ❌       |
| Cancel Appointment        | ✅     | ❌      | ✅       |

