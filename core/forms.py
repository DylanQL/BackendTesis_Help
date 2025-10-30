from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models.models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            'dni', 'email', 'nombres', 'apellidos', 'celular', 'rol', 'empresa', 'supervisor',
            'estado_contrasena', 'estado', 'is_active', 'is_staff'
        )

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            'dni', 'email', 'nombres', 'apellidos', 'celular', 'rol', 'empresa', 'supervisor',
            'estado_contrasena', 'estado', 'is_active', 'is_staff'
        )
