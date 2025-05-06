from django.urls import path, include
from . import views 
from django.contrib import admin
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from usuarios.views import vista_protegida
from django.conf import settings
from django.conf.urls.static import static
from .views import custom_logout

urlpatterns = [
    path('', views.inicio, name='inicio'),  # Página principal
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/protegido/', vista_protegida, name='vista_protegida'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('registro/', views.registro, name='registro'),
    #path('verificar_2fa/', GenerarCodigo2FA.as_view(), name='verificar_2fa'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('registrar_empresa/', views.registrar_empresa, name="registrar_empresa"),
    path('empresas/', views.lista_empresas, name= "lista_empresas"),
    path("editar-empresa/<int:empresa_id>/", views.editar_empresa, name="editar_empresa"),
    path("eliminar-empresa/<int:empresa_id>/", views.eliminar_empresa, name="eliminar_empresa"),
    path("validar-empresa/<int:empresa_id>/", views.validar_empresa, name="validar_empresa"),
    path('descargar-constancia/<int:empresa_id>/', views.descargar_constancia, name='descargar_constancia'),
    path('consulta-publica/', views.consulta_publica_empresas, name='consulta_publica'),
    path('empresa/<int:empresa_id>/registrar-producto/', views.registrar_producto, name='registrar_producto'),
    path('empresa/<int:empresa_id>/productos/', views.productos_empresa, name='productos_empresa'),
    path('producto/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('producto/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('usuarios/empresa/<int:empresa_id>/servicios/', views.servicios_empresa, name='servicios_empresa'),
    path('empresa/<int:empresa_id>/registrar-servicio/', views.registrar_servicio, name='registrar_servicio'),
    path('servicio/<int:servicio_id>/validar/', views.validar_servicio, name='validar_servicio'),
    path('servicios/', views.lista_todos_servicios, name='lista_todos_servicios'),
    path('mis_documentos/', views.subir_documento_empresa, name='subir_documento_empresa'),
    path('documentos/', views.documentos_admin, name='documentos_admin'),
    path('historial-empresa/<int:empresa_id>/', views.historial_empresa, name='historial_empresa'),

    path('logout/', custom_logout, name='logout'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

