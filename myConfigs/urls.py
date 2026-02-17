from django.urls import path
from . import views

urlpatterns = [
    path('', views.running, name='running'),
    path('login/', views.login, name='login'),
    path('doctor/register_doc/', views.register_doctor, name='register_doctor'),
    path('patient/register_patient/', views.register_patient, name='register_patient'),
    path('records/', views.get_records, name='get_records'),
    path('doctor/profile', views.get_my_doc_profile, name='get_my_doc_profile'),
    path('doctor/patients', views.get_doc_patients, name='get_doc_patients'),
    path('patient/profile', views.get_my_patient_profile, name='get_my_patient_profile'),
    path('doctors/', views.get_doctors, name='get_doctors'),
    path('docotor/<int:id>/update/', views.update_doc, name='update_doc'),
    path('patient/<int:id>/update/', views.update_patient, name='update_patient'),
    path('doctor/<int:id>/delete/', views.delete_doc, name='delete_doc'),
    path('patient/<int:id>/delete/', views.delete_patient, name='delete_patient'),
]