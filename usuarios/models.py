from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from django.contrib.auth import get_user_model


class Usuario(AbstractUser):
     correo = models.EmailField(unique=True)
     documento_identidad = models.FileField(upload_to='documentos_identidad/', blank=True, null=True)
     documento_verificado = models.BooleanField(default=False)  # Para saber si ya fue validado
     rol = models.CharField(
        max_length=20, 
        choices=[("admin", "Administrador"), ("usuario", "Usuario"), ("funcionario", "Funcionario")], 
        default="usuario"
    )
     
     class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


class Empresa(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='empresas')
    nombre = models.CharField(max_length=255, unique=True)
    rfc = models.CharField(max_length=13, unique=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(unique=True)
    representante = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    documento_constitutiva = models.FileField(upload_to="documentos/constitutiva/", blank=True, null=True)
    documento_identificacion = models.FileField(upload_to="documentos/identificacion/", blank=True, null=True)
    documento_rfc = models.FileField(upload_to="documentos/rfc/", blank=True, null=True)
    validado = models.BooleanField(default=False)
    notificacion_validado = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nombre
    

class EmpresaForm(forms.ModelForm):
    class Meta:
        model    = Empresa
        fields = '__all__'


class Notificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.mensaje[:40]}"


class Producto(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"
    
    
class Servicio(models.Model):
    empresa = models.ForeignKey(Empresa, related_name='servicios', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio_aproximado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    validado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


class DocumentoEmpresa(models.Model):
    TIPO_CHOICES = [
        ('rfc', 'RFC / SAT'),
        ('domicilio', 'Comprobante de domicilio'),
        ('acta', 'Acta constitutiva'),
        ('licencia', 'Licencia / Permiso'),
        ('otro', 'Otro'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    archivo = models.FileField(upload_to='documentos_empresas/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.empresa.nombre} - {self.get_tipo_display()}"

#--------------------------------------------------------------------------------------
User = get_user_model()

class HistorialEmpresa(models.Model):
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.fecha} - {self.accion} - {self.empresa.nombre}"
