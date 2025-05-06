from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistroForm, EmpresaForm, ProductoForm, ServicioForm, DocumentoEmpresaForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from usuarios.models  import Usuario, Empresa
from django.contrib import messages
from .models import Empresa, Notificacion, Producto, Servicio, DocumentoEmpresa, HistorialEmpresa
from reportlab.pdfgen import canvas
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib.auth import logout



def inicio(request):
    return render(request, 'usuarios/inicio.html')

def custom_logout(request):
    logout(request)  # Cierra la sesión
    return redirect('inicio')  # Redirige a la página de inicio

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vista_protegida(request):
    return Response({"mensaje": "¡Accediste con éxito usando JWT!"})

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            print(form.errors)  # 👈 Esto imprime los errores en consola
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def profile_view(request):
    empresa = Empresa.objects.filter(usuario=request.user).first()
    empresas = request.user.empresas.all()
    notificaciones = request.user.notificaciones.order_by('-fecha')  # relacionadas al usuario
    print(f"Notificaciones: {notificaciones}")
    return render(request, 'usuarios/profile.html', {
        'empresas': empresas,
        'notificaciones': notificaciones
    })


@login_required
def registrar_empresa(request):
    if request.method == "POST":
        form = EmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            empresa = form.save(commit = False)
            empresa.usuario = request.user
            empresa.save()

            messages.success(request, "✅ Tu empresa ha sido registrada exitosamente. Espera validación por parte del administrador.")

            if request.user.is_staff:
               return redirect('lista_empresas')
            else:
               return redirect('profile')

    else:
        form = EmpresaForm()
    return render(request, "usuarios/registrar_empresa.html", {"form": form})

@login_required
def dashboard(request):
    if not request.user.is_superuser and not request.user.groups.filter(name="Administradores").exists():
        messages.error(request, "No tienes permisos para acceder al panel de administración.")
        return redirect('profile')

    total_usuarios = Usuario.objects.count()
    usuarios_activos = Usuario.objects.filter(is_active=True).count()
    usuarios_inactivos = Usuario.objects.filter(is_active=False).count()
    empresas = Empresa.objects.all()

    contexto = {
        "total_usuarios": total_usuarios,
        "usuarios_activos": usuarios_activos,
        "usuarios_inactivos": usuarios_inactivos,
        "empresas" : empresas,
    }
    
    return render(request, "admin/dashboard.html", contexto)

@login_required
def lista_empresas(request):
    empresas = Empresa.objects.all()
    return render(request, "admin/lista_empresas.html", {"empresas" : empresas})

@login_required
def editar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa,  id=empresa_id)
    
    if request.method == "POST":
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            return redirect("lista_empresas")  # Redirige a la lista de empresas
    else:
        form = EmpresaForm(instance=empresa)
    
    return render(request, "admin/editar_empresa.html", {"form": form})

@login_required
def eliminar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    empresa.delete()
    return redirect("lista_empresas")


@login_required
def validar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    empresa.validado = True
    empresa.save()

    mensaje = f"Tu empresa '{empresa.nombre}' ha sido validada exitosamente."
    Notificacion.objects.create(usuario=empresa.usuario, mensaje=mensaje)

    return redirect('lista_empresas')  # ✅ Aquí debe terminar tu vista


@login_required
def descargar_constancia(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)

    if empresa.usuario != request.user and not request.user.is_staff:
        messages.error(request, "No tienes permiso para generar esta constancia.")
        return redirect('profile')

    if not empresa.validado:
        messages.error(request, "La empresa aún no ha sido validada.")
        return redirect('profile')

    # Crear PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="constancia_{empresa.nombre}.pdf"'

    pdf = canvas.Canvas(response)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, 800, "Constancia de Registro de Empresa")
    
    pdf.drawString(100, 600, "Se le consigna una constancia donde acreditara su empresa")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 770, f"Nombre: {empresa.nombre}")
    pdf.drawString(100, 750, f"RFC: {empresa.rfc}")
    pdf.drawString(100, 730, f"Representante: {empresa.representante}")
    pdf.drawString(100, 710, f"Correo: {empresa.correo}")
    pdf.drawString(100, 690, f"Fecha de Registro: {empresa.fecha_registro.strftime('%d/%m/%Y')}")

    pdf.drawString(100, 650, "La presente constancia acredita que la empresa ha sido registrada y validada.")
    
    pdf.showPage()
    pdf.save()

    return response


def consulta_publica_empresas(request):
    query = request.GET.get('q')
    empresas = Empresa.objects.filter(validado=True)

    if query:
        empresas = empresas.filter(
            Q(nombre__icontains=query) |
            Q(rfc__icontains=query) |
            Q(representante__icontains=query)
        )

    return render(request, "usuarios/consulta_publica.html", {"empresas": empresas, "query": query})

@login_required
def consulta_empresas(request):
    empresas_list = Empresa.objects.filter(validado=True)

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        empresas_list = empresas_list.filter(fecha_registro__gte=parse_date(fecha_inicio))
    if fecha_fin:
        empresas_list = empresas_list.filter(fecha_registro__lte=parse_date(fecha_fin))

    paginator = Paginator(empresas_list.order_by('-fecha_registro'), 10)
    page_number = request.GET.get('page')
    empresas = paginator.get_page(page_number)

    return render(request, 'consulta/consulta_empresas.html', {
        'empresas': empresas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    })

@login_required
def registrar_producto(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)

    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.empresa = empresa
            producto.save()
            messages.success(request, "✅ Producto registrado exitosamente.")
            return redirect('productos_empresa', empresa_id=empresa.id)
    else:
        form = ProductoForm()

    return render(request, 'usuarios/registrar_producto.html', {'form': form, 'empresa': empresa})

@login_required
def productos_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)

    # Verifica que el usuario sea dueño o admin
    if request.user != empresa.usuario and not request.user.is_staff:
        messages.error(request, "No tienes permisos para ver los productos de esta empresa.")
        return redirect('profile')

    productos = empresa.productos.all()

    return render(request, 'usuarios/listado_productos.html', {
        'empresa': empresa,
        'productos': productos
    })

@login_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Permitir solo al dueño de la empresa o al staff
    if request.user != producto.empresa.usuario and not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto actualizado correctamente.")
            return redirect('productos_empresa', empresa_id=producto.empresa.id)
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'usuarios/editar_producto.html', {'form': form})


@login_required
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Permitir solo al dueño de la empresa o al staff
    if request.user != producto.empresa.usuario and not request.user.is_staff:
        raise PermissionDenied

    empresa_id = producto.empresa.id
    producto.delete()
    messages.success(request, "❌ Producto eliminado correctamente.")
    return redirect('productos_empresa', empresa_id=empresa_id)


@login_required
def registrar_servicio(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)

    if request.user != empresa.usuario:
        messages.error(request, "No tienes permisos para registrar servicios en esta empresa.")
        return redirect('profile')

    if request.method == "POST":
        form = ServicioForm(request.POST)
        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.empresa = empresa
            servicio.save()
            messages.success(request, "✅ Servicio registrado con éxito.")
            return redirect('servicios_empresa', empresa_id=empresa.id)
    else:
        form = ServicioForm()

    return render(request, 'usuarios/registrar_servicio.html', {'form': form, 'empresa': empresa})

@login_required
def servicios_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)

    if request.user != empresa.usuario and not request.user.is_staff:
        messages.error(request, "No puedes ver los servicios de esta empresa.")
        return redirect('profile')

    servicios = empresa.servicios.all()
    return render(request, 'usuarios/listado_servicios.html', {'empresa': empresa, 'servicios': servicios})

@staff_member_required
def validar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    servicio.validado = True
    servicio.save()
    messages.success(request, "✅ Servicio validado correctamente.")
    return redirect('servicios_empresa', empresa_id=servicio.empresa.id)

@staff_member_required
def lista_todos_servicios(request):
    servicios = Servicio.objects.select_related('empresa').all()
    return render(request, "admin/servicios_todos.html", {"servicios": servicios})

@login_required
def subir_documento_empresa(request):
    empresa = Empresa.objects.filter(usuario=request.user).first()
    if not empresa:
        messages.error(request, 'Aún no tienes una empresa registrada. Regístrala primero para poder subir documentos.')
        return redirect('registrar_empresa')

    if request.method == 'POST':
        form = DocumentoEmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.empresa = empresa
            documento.save()
            messages.success(request, 'Documento subido correctamente.')
            return redirect('subir_documento_empresa')  # mejor redirigir aquí de nuevo

    else:
        form = DocumentoEmpresaForm()

    documentos = empresa.documentos.all()
    return render(request, 'usuarios/subir_documento.html', {'form': form, 'documentos': documentos})

@staff_member_required
def documentos_admin(request):
   documentos = DocumentoEmpresa.objects.all()
   return render(request, 'admin/documentos_admin.html', {'documentos': documentos})


@login_required
def historial_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)

    if request.user != empresa.usuario and not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para ver este historial.")

    historial = HistorialEmpresa.objects.filter(empresa=empresa).order_by('-fecha')

    return render(request, "usuarios/historial_empresa.html", {"empresa": empresa, "historial": historial})

