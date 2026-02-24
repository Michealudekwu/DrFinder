from rest_framework import serializers
from .models import Doctor, Patient

class DoctorSerializer(serializers.ModelSerializer):
    Patients = serializers.SerializerMethodField()

    class Meta:
        model =Doctor
        exclude = ['user']
    
    def get_Patients(self, obj):
        patients = obj.patients.all()
        return PatientSerializer(patients, many=True).data

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model =Patient
        exclude = ['user']