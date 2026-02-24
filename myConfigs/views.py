from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from rest_framework import status
from .serializers import DoctorSerializer, PatientSerializer
from .models import Doctor, Patient
from django.db.models import Q
from django.contrib import messages

@api_view(['POST'])
@permission_classes([AllowAny])
def register_doctor(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    name = request.data.get('name')
    speciality = request.data.get('speciality')
    country = request.data.get('country')
    city = request.data.get('city')
    state = request.data.get('state')
    phone_number = request.data.get('phone_number')
    postal_code = request.data.get('postal_code')
    gender = request.data.get('gender')
    description = request.data.get('description')

    if User.objects.filter(username = username).exists():
        return Response({'error' : 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(
        username=username,
        password=password, #Auto hashes
        email = email
    )

    doctor = Doctor.objects.create(
        user = user,
        name = name,
        speciality = speciality,
        country = country,
        state = state,
        city = city,
        phone_number = phone_number,
        postal_code = postal_code,
        gender = gender,
        description = description
    )

    token = Token.objects.create(user=user)

    return Response({
        'token': token.key,
        'user_type': 'doctor',
        'profile': DoctorSerializer(doctor).data
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_patient(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    name = request.data.get('name')
    country = request.data.get('country')
    city = request.data.get('city')
    state = request.data.get('state')
    phone_number = request.data.get('phone_number')
    postal_code = request.data.get('postal_code')
    gender = request.data.get('gender')
    age = request.data.get('age')

    if User.objects.filter(username = username).exists():
        return Response({'error' : 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(
        username=username,
        password=password, #Auto hashes
        email = email
    )

    patient = Patient.objects.create(
        user = user,
        name = name,
        country = country,
        state = state,
        city = city,
        phone_number = phone_number,
        postal_code = postal_code,
        gender = gender,
        age = age
    )

    token = Token.objects.create(user=user)
    return Response({
        'token': token.key,
        'user_type': 'patient',
        'profile': PatientSerializer(patient).data
    }, status=status.HTTP_201_CREATED)


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(username, password)

        user = authenticate(username=username, password=password)
        if user:
            print("Authenticated")
            auth_login(request, user)    
            return redirect('get_doctors')
        else:
            messages.error(request, 'Invalid Credentials or User not found')
            return redirect('login')

    return render(request, 'myConfigs/login.html', {'messages': messages.get_messages(request)})


def logout(request):
    auth_logout(request)
    return redirect('login')

@api_view(['GET'])
def running(request):
    return Response("API is Running")

@api_view(['GET'])
def get_records(request):
    doctors = Doctor.objects.all()
    # Patient = Patient.objects.all()
    docsSrializer = DoctorSerializer(doctors, many=True)
    # patSerializer = PatientSerializer(Patient, many=True)

    return Response({
        'doctors': docsSrializer.data,
    })

# Doctor Functions
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_doc_profile(request):
    try:
        doc = request.user.doctor_profile
        docSerializer = DoctorSerializer(doc)
        return Response(docSerializer.data) 
    except :
        return Response({'error': 'Not a doctor account'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doc_patients(request):
    try:
        doc = request.user.doctor_profile
        patient = Patient.objects.filter(doctor=doc)
        patSerializer = PatientSerializer(patient, many=True)
        return Response(patSerializer.data)
    except :
        return Response({'error': 'Not a doctor account'}, status=status.HTTP_404_NOT_FOUND)
    
#Patient Functions
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_patient_profile(request):
    try: 
        patient = request.user.patient_profile
        patSerializer=PatientSerializer(patient)
        return Response(patSerializer.data)
    except:
        return Response({'error':'Not a patient account'}, status=status.HTTP_403_FORBIDDEN)
    


@login_required
def get_doctors(request):
    search = request.GET.get('search', '').strip()
    location = request.GET.get('location', '').strip()

    print("Search:", search)
    print("Location:", location)

    doctors = Doctor.objects.all()

    if search:
        doctors = doctors.filter(
            Q(name__icontains=search) |
            Q(speciality__icontains=search)
        )

    if location:
        if ',' in location:
            city, state = [x.strip() for x in location.split(',', 1)]
            doctors = doctors.filter(
                Q(city__icontains=city) |
                Q(state__icontains=state)
            )
        else:
            doctors = doctors.filter(
                Q(city__icontains=location) |
                Q(state__icontains=location)
            )

    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Not a patient account')
        return redirect('login')

    docSerializer = DoctorSerializer(doctors, many=True)
    patient_profile = PatientSerializer(patient)

    return render(request, 'myConfigs/patientland.html', {
        'doctors': docSerializer.data, 
        'patient': patient_profile.data,
    })


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_doc(request, id):
    try:
        doc = Doctor.objects.get(id=id)

        my_profile = (request.user == doc.user)
        is_admin = request.user.is_staff 

        if not(is_admin or my_profile):
            return Response({'error': "Can't make the change"}, status=status.HTTP_403_FORBIDDEN)

        docSerializer = DoctorSerializer(doc, data=request.data, partial=True)

        if docSerializer.is_valid():
            docSerializer.save()
            return Response(docSerializer.data)
        return Response(docSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Doctor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_patient(request, id):
    try:
        patient = Patient.objects.get(id=id)

        my_profile = (patient.user == request.user)
        is_admin = request.user.is_staff

        if not (is_admin or my_profile):
            return Response({'error': "Can't make the change"}, status=status.HTTP_403_FORBIDDEN)

        
        patSerializer = PatientSerializer(patient, data=request.data, partial=True)
        if patSerializer.is_valid():
            patSerializer.save()
            return Response(patSerializer.data)
        return Response(patSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Patient.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_doc(request, id):
    try:
        doc = Doctor.objects.get(id=id)

        doc.delete()
        return Response({'message' : 'Doctor deleted'},status=status.HTTP_204_NO_CONTENT)
    except Doctor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_patient(request, id):
    try:
        patient = Patient.objects.get(id=id)
        patient.delete()
        return Response({'message' : 'Doctor deleted'},status=status.HTTP_204_NO_CONTENT)
    except Patient.DoesNotExist:
        return Response(status.HTTP_404_NOT_FOUND)

