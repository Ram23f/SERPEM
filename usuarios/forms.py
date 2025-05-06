from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Empresa, Producto, Servicio, DocumentoEmpresa


class RegistroForm(UserCreationForm):
    correo = forms.EmailField()

    class Meta:
        model = Usuario
        fields = ['username', 'correo', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.correo = self.cleaned_data['correo']
        if commit:
            user.save()
        return user


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'rfc', 'direccion', 'telefono', 'correo','documento_rfc', 'documento_identificacion', 'documento_constitutiva']


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'disponible']


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio_aproximado']


class DocumentoEmpresaForm(forms.ModelForm):
    class Meta:
        model = DocumentoEmpresa
        fields = ['tipo', 'archivo', 'observaciones']
