from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from .serializers import DoctorSerializer, PatientSerializer
from .models import Doctor, Patient

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
        gender = gender
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
    gender = request.get('gender')

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
        gender = gender
    )

    token = Token.objects.create(user=user)
    return Response({
        'token': token.key,
        'user_type': 'patient',
        'profile': PatientSerializer(patient).data
    }, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def login(request):
    if request.method == 'GET':
        return render(request, 'myConfigs/login.html')

    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(email=email, password=password)
    if user:
        token,_ = Token.objects.get_or_create(user=user)

        user_type = None
        profile_data = None

        if hasattr(user, "doctor_profile"):
            user_type = "doctor"
            profile_data = DoctorSerializer(user.doctor_profile).data
        elif hasattr(user, "patient_profile"):
            user_type = "patient"
            profile_data = PatientSerializer(user.patient_profile).data

        return Response({
            'token': token.key,
            'username': user.username,
            'user_type': user_type,
            'profile': profile_data
        })
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def running(request):
    return Response("API is Running")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctors(request):
    doctors = Doctor.objects.all()
    docSerializer = DoctorSerializer(doctors, many=True)
    return Response(docSerializer.data)


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

