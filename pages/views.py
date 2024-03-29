from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import F
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from .models import Page
from .cuestionario import Cuestionario, CuestionarioRespuesta
from .subscription import Subscription
from .historial import Historial
from registration.models import Profile
from .forms import PageForm
from django.http import Http404, JsonResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template import loader
import threading
from datetime import datetime
from django.http import HttpResponse
import csv
from social.models import MailContacto
import pytz
from django.template.defaultfilters import date as date_format
from datetime import date
from django.db.models import Q


def CuposAgotados(request, pk):
    page = get_object_or_404(Page, pk=pk)
    usu = (
        request.user.profile.nombre + "  " + request.user.profile.apellido
        if request.user.profile.nombre is not None
        else request.user
    )

    formatted_fecha = date_format(page.fecha, "l d \d\e F")

    asunto = "Cupos agotados - " + page.title
    html_message = loader.render_to_string(
        "mail_body.html",
        {
            "user_name": usu
            + " https://wa.me/+549"
            + str(request.user.profile.whatsapp)
            + " "
            + (
                request.user.profile.perfil_ok
                if request.user.profile.perfil_ok is not None
                else ""
            ),
            "subject": "Se quiso anotar en "
            + page.title
            + " a las "
            + str(page.horaDesde)
            + ("HS  el día " + formatted_fecha if page.fecha is not None else "")
            + " pero los cupos estaban agotados.",
        },
    )
    mailContacto = MailContacto.objects.first()
    to_mail = (mailContacto,)
    from_mail = "Hillel Argentina"
    rta = send_html_mail(asunto, html_message, to_mail, from_mail)
    response = {"is_taken": rta}
    return JsonResponse(response)


# En desuso porque el servidor no acepta hilos
class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list, mail_from):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.mail_from = mail_from
        threading.Thread.__init__(self)

    def run(self):
        print("enviando mail")
        mail = send_mail(
            self.subject,
            self.html_content,
            self.mail_from,
            self.recipient_list,
            fail_silently=True,
            html_message=self.html_content,
        )
        print(mail)


def send_html_mail(subject, html_content, recipient_list, mail_from):
    # EmailThread(subject, html_content, recipient_list, mail_from).start()
    print("enviando mail")
    mail = send_mail(
        subject,
        html_content,
        mail_from,
        recipient_list,
        fail_silently=True,
        html_message=html_content,
    )


class StaffRequiredMixin(object):
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)


# Create your views here.


def Onward(request):
    return render(request, "pages/onward.html")


class PageList(ListView):
    model = Page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_anonymous:
            provincia = None
        else:
            profile = Profile.objects.get_or_create(user=self.request.user)
            if profile is None:
                provincia = None
            else:
                provincia = self.request.user.profile.provincia

        context["provincia"] = provincia
        local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
        today = datetime.now(local_tz).date()

        if provincia is not None:
            active_pages = Page.objects.filter(
                Q(modalidad=True) | Q(provincia=provincia),
                activa=True,
                cowork=False,
                fecha__gte=today,
            ).order_by("fecha", "horaDesde", "-title")
        else:
            active_pages = Page.objects.filter(
                activa=True,
                cowork=False,
                fecha__gte=today,
            ).order_by("fecha", "horaDesde", "-title")

        active_pages_map = {}
        recurrent_pages_map = {}

        for page in active_pages:
            if page.recurrent_page is None:
                if page.fecha not in active_pages_map:
                    active_pages_map[page.fecha] = []
                active_pages_map[page.fecha].append(page)
            else:
                recurrent_page_id = (
                    page.recurrent_page.id
                )  # Get the id of the recurrent_page
                if recurrent_page_id not in recurrent_pages_map:
                    if page.fecha not in active_pages_map:
                        active_pages_map[page.fecha] = []
                    active_pages_map[page.fecha].append(page)
                    recurrent_pages_map[recurrent_page_id] = True

        cowork_pages = Page.objects.filter(activa=True, cowork=True).order_by(
            "horaDesde", "-title"
        )
        context["cowork_pages"] = cowork_pages
        context["active_pages_map"] = active_pages_map
        context["cowork_pages"] = cowork_pages

        if len(self.kwargs) > 0:
            context["cowork"] = self.kwargs["modalidad"]
        else:
            context["cowork"] = 0
        context["coworkStr"] = "calendario" if context["cowork"] == 0 else "cowork"

        return context


class PageDetail(DetailView):
    model = Page

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
        current_date = datetime.now(local_tz)

        if obj.fecha < current_date.date():
            obj.activa = False
            obj.save()

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()

        cuestionario = Cuestionario.objects.find_or_create(page=self.object)
        if cuestionario is not None:
            context["cuestionario"] = cuestionario
            print(context["cuestionario"])

        if self.request.user.is_anonymous:
            return context
        subscribers = Subscription.objects.find_page(self.object)
        overlaps = Subscription.objects.overlaps(self.request.user, self.object)

        context["subscribers"] = subscribers
        context["overlaps"] = overlaps
        if subscribers is not None:
            context["usuarioAnotado"] = subscribers.filter(
                user=self.request.user
            ).exists()
        return context


class PageConfirmation(ListView):
    model = Page


@method_decorator(staff_member_required, name="dispatch")
class PageCreate(CreateView):
    model = Page
    form_class = PageForm
    # success_url = reverse_lazy('pages:pages')

    def get_success_url(self):
        return reverse_lazy("pages:pages") + "?created"


@method_decorator(staff_member_required, name="dispatch")
class PageUpdate(UpdateView):
    model = Page
    form_class = PageForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse_lazy("pages:update", args=[self.object.id]) + "?ok"

    def form_valid(self, form):
        self.object = form.save()

        if self.object.recurrent_page:
            recurrent_pages = self.object.recurrent_page.pages
            recurrent_pages.update(
                title=self.object.title,
                horaDesde=self.object.horaDesde,
                horaHasta=self.object.horaHasta,
                modalidad=self.object.modalidad,
                provincia=self.object.provincia,
                description=self.object.description,
                cupo=self.object.cupo,
                nuevo=self.object.nuevo,
                activa=self.object.activa,
                responsable=self.object.responsable,
                colaborador=self.object.colaborador,
                secreta=self.object.secreta,
                clave=self.object.clave,
                textoExtraMail=self.object.textoExtraMail,
                con_mail_personalizado=self.object.con_mail_personalizado,
                asunto_mail=self.object.asunto_mail,
                cuerpo_mail=self.object.cuerpo_mail,
            )
        return super().form_valid(form)


@method_decorator(staff_member_required, name="dispatch")
class PageDelete(DeleteView):
    model = Page
    success_url = reverse_lazy("pages:pages")


def Register(request, pk):
    if request.user.is_authenticated:
        page = get_object_or_404(Page, pk=pk)
        cuestionario = Cuestionario.objects.get(page=page)
        if cuestionario is not None:
            cuestionarioRespuesta = CuestionarioRespuesta.objects.find_or_create(
                user=request.user, page=page
            )

            if request.POST.get("respuesta1", None) is not None:
                cuestionarioRespuesta.pregunta1 = cuestionario.pregunta1
                cuestionarioRespuesta.respuesta1 = request.POST["respuesta1"]

            if request.POST.get("respuesta2", None) is not None:
                cuestionarioRespuesta.pregunta2 = cuestionario.pregunta2
                cuestionarioRespuesta.respuesta2 = request.POST["respuesta2"]

            if request.POST.get("respuesta3", None) is not None:
                cuestionarioRespuesta.pregunta3 = cuestionario.pregunta3
                cuestionarioRespuesta.respuesta3 = request.POST["respuesta3"]

            if request.POST.get("respuesta4", None) is not None:
                cuestionarioRespuesta.pregunta4 = cuestionario.pregunta4
                cuestionarioRespuesta.respuesta4 = request.POST["respuesta4"]

            if request.POST.get("respuesta5", None) is not None:
                cuestionarioRespuesta.pregunta5 = cuestionario.pregunta5
                cuestionarioRespuesta.respuesta5 = request.POST["respuesta5"]

            if request.POST.get("respuesta6", None) is not None:
                cuestionarioRespuesta.pregunta6 = cuestionario.pregunta6
                cuestionarioRespuesta.respuesta6 = request.POST["respuesta6"]

            if request.POST.get("respuesta7", None) is not None:
                cuestionarioRespuesta.pregunta7 = cuestionario.pregunta7
                cuestionarioRespuesta.respuesta7 = request.POST["respuesta7"]

            if request.POST.get("respuesta8", None) is not None:
                cuestionarioRespuesta.pregunta8 = cuestionario.pregunta8
                cuestionarioRespuesta.respuesta8 = request.POST["respuesta8"]

            if request.POST.get("respuesta9", None) is not None:
                cuestionarioRespuesta.pregunta9 = cuestionario.pregunta9
                cuestionarioRespuesta.respuesta9 = request.POST["respuesta9"]

            if request.POST.get("respuesta10", None) is not None:
                cuestionarioRespuesta.pregunta10 = cuestionario.pregunta10
                cuestionarioRespuesta.respuesta10 = request.POST["respuesta10"]

            if request.POST.get("respuesta11", None) is not None:
                cuestionarioRespuesta.pregunta11 = cuestionario.pregunta11
                cuestionarioRespuesta.respuesta11 = request.POST["respuesta11"]

            if request.POST.get("respuesta12", None) is not None:
                cuestionarioRespuesta.pregunta12 = cuestionario.pregunta12
                cuestionarioRespuesta.respuesta12 = request.POST["respuesta12"]

            if request.POST.get("respuesta13", None) is not None:
                cuestionarioRespuesta.pregunta13 = cuestionario.pregunta13
                cuestionarioRespuesta.respuesta13 = request.POST["respuesta13"]

            if request.POST.get("respuesta14", None) is not None:
                cuestionarioRespuesta.pregunta14 = cuestionario.pregunta14
                cuestionarioRespuesta.respuesta14 = request.POST["respuesta14"]

            if request.POST.get("respuesta15", None) is not None:
                cuestionarioRespuesta.pregunta15 = cuestionario.pregunta15
                cuestionarioRespuesta.respuesta15 = request.POST["respuesta15"]

            if request.POST.get("respuesta16", None) is not None:
                cuestionarioRespuesta.pregunta16 = cuestionario.pregunta16
                cuestionarioRespuesta.respuesta16 = request.POST["respuesta16"]

            if request.POST.get("respuesta17", None) is not None:
                cuestionarioRespuesta.pregunta17 = cuestionario.pregunta17
                cuestionarioRespuesta.respuesta17 = request.POST["respuesta17"]

            if request.POST.get("respuesta18", None) is not None:
                cuestionarioRespuesta.pregunta18 = cuestionario.pregunta18
                cuestionarioRespuesta.respuesta18 = request.POST["respuesta18"]

            if request.POST.get("respuesta19", None) is not None:
                cuestionarioRespuesta.pregunta19 = cuestionario.pregunta19
                cuestionarioRespuesta.respuesta19 = request.POST["respuesta19"]

            if request.POST.get("respuesta20", None) is not None:
                cuestionarioRespuesta.pregunta20 = cuestionario.pregunta20
                cuestionarioRespuesta.respuesta20 = request.POST["respuesta20"]

            cuestionarioRespuesta.save()

        # Si la page es secreta validar la clave
        if page.secreta:
            if request.POST["password"] != page.clave:
                return redirect(
                    reverse_lazy(
                        "pages:page",
                        args=[
                            page.id,
                        ],
                    )
                    + "?claveincorrecta"
                )

        # Chequear que haya cupos disponibles (No debería llegar acá)
        if page.Qanotados >= page.cupo and page.cupo != 0:
            return redirect(reverse_lazy("pages:pages") + "?agotado")

        # chequear que el perfil esté completo
        if request.user.profile.validado is not True:
            return redirect(
                reverse_lazy(
                    "profile",
                    args=[
                        page.id,
                    ],
                )
                + "?completar=si&pk="
                + str(pk)
            )

        subscription = Subscription.objects.find_or_create(request.user)

        if page.recurrent_page:
            new_pages = page.recurrent_page.pages.all()
        else:
            new_pages = [page]
        subscription.pages.add(*new_pages)

    else:
        raise Http404("Usuario no está autenticado")

    # Mail automático
    modalidad = " Online" if page.modalidad else " Presencial"
    asunto = (
        "Te esperamos en " + page.title + modalidad + "!"
        if not page.con_mail_personalizado
        else page.asunto_mail
    )
    to_mail = [request.user.email]
    from_mail = "Hillel Argentina <no_responder@domain.com>"
    host = request.get_host()
    host = host if "127.0.0.1" in host else "https://" + host
    textoExtraMail = (
        page.textoExtraMail if page.textoExtraMail is not None else page.description
    )
    if page.con_mail_personalizado:
        html_message = loader.render_to_string(
            "custom_mail_body.html",
            {
                "mail_body": page.cuerpo_mail,
            },
        )
    else:
        html_message = loader.render_to_string(
            "mail_body.html",
            {
                "user_name": "Hola " + request.user.username + "!",
                "subject": "Te anotaste en "
                + page.title
                + modalidad
                + " a las "
                + str(page.horaDesde)
                + "HS."
                + " Podés darte de baja acá: "
                + host
                + "/pages/"
                + str(page.id),
                "description": textoExtraMail,
            },
        )
    send_html_mail(asunto, html_message, to_mail, from_mail)
    return redirect(reverse_lazy("home") + "?ok")


def Unregister(request, pk):
    if request.user.is_authenticated:
        page = get_object_or_404(Page, pk=pk)
        subscription = Subscription.objects.find_or_create(request.user)
        subscription.pages.remove(page)
    else:
        raise Http404("Usuario no está autenticado")
    return redirect(reverse_lazy("home") + "?remove")


def Asistencia(request, modalidad):
    if request.user.is_authenticated:
        if request.user.groups.filter(name="BITAJON").exists() or request.user.is_staff:
            local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
            dia = datetime.now(local_tz).weekday() + 1
            pages = Page.objects.filter(activa=True, modalidad=modalidad)

            # Get the unique dates of the pages and order them
            unique_dates = (
                pages.values_list("fecha", flat=True).distinct().order_by("fecha")
            )

            # Fetch pages for each unique date and annotate with the date itself
            annotated_pages = pages.annotate(date=F("fecha"))

            return render(
                request,
                "pages/asistencia.html",
                {
                    "pages": annotated_pages,
                    "dia": dia,
                    "modalidad": modalidad,
                    "unique_dates": unique_dates,
                },
            )

        raise Http404("Usuario no es bitajon/staff")

    raise Http404("Usuario no está autenticado")


def AsistenciaDetail(request, pk, slug):
    if request.user.is_authenticated:
        page = get_object_or_404(Page, pk=pk)
        subscribers = Subscription.objects.find_page(page)
        return render(
            request,
            "pages/asistencia_detail.html",
            {"page": page, "subscribers": subscribers},
        )
    raise Http404("Usuario no está autenticado")


def AsistenciaAdd(request, pk):
    json_response = {"created": False}
    if request.user.is_authenticated:
        username = request.GET.get("user", None)
        user = User.objects.get(username=username)
        if username:
            page = get_object_or_404(Page, pk=pk)
            local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
            hoy = datetime.now(local_tz)
            historial = Historial.objects.find_or_create(page, hoy)
            historial.asistentes.add(user)

            # Se actualiza la lista de asistencias en el objeto de Historial
            subscribers = Subscription.objects.find_page(page)
            for subscripcion in subscribers:
                historial.anotados.add(subscripcion.user)

            json_response["created"] = True
            json_response["hoy"] = hoy

            return JsonResponse(json_response)
    raise Http404("Usuario no está autenticado")


def AsistenciaRemove(request, pk):
    json_response = {"created": False}
    if request.user.is_authenticated:
        username = request.GET.get("user", None)
        user = User.objects.get(username=username)
        if username:
            page = get_object_or_404(Page, pk=pk)
            local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
            hoy = datetime.now(local_tz)
            historial = Historial.objects.find_or_create(page, hoy)
            historial.asistentes.remove(user)

            json_response["created"] = True
            json_response["hoy"] = hoy

            return JsonResponse(json_response)
    raise Http404("Usuario no está autenticado")


def WriteRowAsistencias(h, writer):
    if h is None:
        return Http404("Historial no encontrado")
    if h.anotados.all() is None:
        return Http404("Historial sin anotados")
    if h.asistentes.all() is None:
        return Http404("Historial sin asistentes")

    for anotado in h.anotados.all():
        asistio = "Si" if anotado in h.asistentes.all() else "No"
        asis = 1 if asistio == "Si" else 0

        Profile.objects.get_or_create(user=anotado)

        writer.writerow(
            [
                h.page.titleSTR,
                h.page.fecha,
                h.page.horaDesde,
                anotado,
                anotado.profile.nombre,
                anotado.profile.apellido,
                anotado.profile.whatsapp,
                anotado.email,
                asistio,
                asis,
            ]
        )


def DescargarAsistencias(request, pk):
    page = get_object_or_404(Page, pk=pk)

    response = HttpResponse(content="")
    local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    response["Content-Disposition"] = (
        "attachment; filename=asistencias-"
        + page.titleSTR
        + "-"
        + str(datetime.now(local_tz))
        + ".csv"
    )
    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response, dialect="excel")
    writer.writerow(
        [
            "Actividad",
            "Dia",
            "Hora Desde",
            "Fecha",
            "Usuario anotado",
            "Nombre",
            "Apellido",
            "Celular",
            "Mail",
            "Asistio?",
            "Asis",
        ]
    )

    h = Page.historialHoy(page)

    WriteRowAsistencias(h, writer)
    return response


def DescargarHistoricoAsistenciasALLDetail(request):
    local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    response = HttpResponse(content="")
    response["Content-Disposition"] = (
        "attachment; filename=asistenciasDETALLE-"
        + "historico-"
        + str(datetime.now(local_tz))
        + ".csv"
    )
    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response, dialect="excel")
    writer.writerow(
        [
            "Actividad",
            "Fecha",
            "Hora Desde",
            "Usuario anotado",
            "Nombre",
            "Apellido",
            "Celular",
            "Mail",
            "Asistio?",
            "Asis",
        ]
    )

    historiales = Historial.objects.all()
    for h in historiales:
        h.fecha = h.fecha.strftime("%d/%m/%Y")
        WriteRowAsistencias(h, writer)
    return response


def DescargarHistoricoAsistenciasALLItem(request):
    local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    # Genera un archivo por actividad-fecha y otro por actividad-fecha-asistente
    responseB = HttpResponse(content="")
    responseB["Content-Disposition"] = (
        "attachment; filename=asistenciasITEM-"
        + "historico-"
        + str(datetime.now(local_tz))
        + ".csv"
    )
    responseB.write("\ufeff".encode("utf8"))
    writerB = csv.writer(responseB, dialect="excel")
    writerB.writerow(["Actividad", "Fecha", "Hora Desde", "Qanotados", "Qasistentes"])

    historiales = Historial.objects.all()
    for h in historiales:
        writerB.writerow(
            [
                h.page.titleSTR,
                h.page.fecha,
                h.page.horaDesde,
                h.Qanotados,
                h.Qasistentes,
            ]
        )

    return responseB


def DescargarHistoricoAsistencias(request, pk):
    page = get_object_or_404(Page, pk=pk)
    local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    response = HttpResponse(content="")
    response["Content-Disposition"] = (
        "attachment; filename=asistencias-"
        + page.titleSTR
        + "-all-"
        + str(datetime.now(local_tz))
        + ".csv"
    )
    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response, dialect="excel")
    writer.writerow(
        [
            "Actividad",
            "Fecha",
            "Hora Desde",
            "Usuario anotado",
            "Nombre",
            "Apellido",
            "Celular",
            "Asistio?",
            "Asis",
        ]
    )

    hs = Historial.objects.find_page(page=page)
    if hs is None:
        return Http404("Historial no encontrado")
    for h in hs:
        WriteRowAsistencias(h, writer)

    return response


def DescargarActividades(request):
    local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    response = HttpResponse(content="")
    response["Content-Disposition"] = (
        "attachment; filename=actividades-" + str(datetime.now(local_tz)) + ".csv"
    )

    response.write("\ufeff".encode("utf8"))

    writer = csv.writer(response, dialect="excel")

    writer.writerow(
        [
            "Titulo",
            "Fecha",
            "Hora Desde",
            "Hora Hasta",
            "Cupo",
            "Modalidad",
            "Nuevo",
            "Activa",
            "Qanotados",
            "Categorias",
            "responsable",
            "colaborador",
            "secreta",
            "clave",
        ]
    )

    pages = Page.objects.all()

    for p in pages:
        if p is None:
            return Http404("Actividad no encontrada")

        writer.writerow(
            [
                p.titleSTR,
                p.fecha,
                p.horaDesde,
                p.horaHasta,
                p.cupo,
                p.modalidadSTR,
                p.nuevo,
                p.activa,
                p.Qanotados,
                p.categoriesSTR,
                p.responsable,
                p.colaborador,
                p.secreta,
                p.clave,
            ]
        )

    return response


def DescargarPerfiles(request):
    local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    response = HttpResponse(content="")
    response["Content-Disposition"] = (
        "attachment; filename=perfiles-" + str(datetime.now(local_tz)) + ".csv"
    )
    writer = csv.writer(response, dialect="excel")
    response.write("\ufeff".encode("utf8"))
    writer.writerow(
        [
            "Usuario",
            "Mail",
            "Nombre",
            "Apellido",
            "Fecha de nacimiento",
            "Edad",
            "Celular",
            "Instagram",
            "Onward",
            "Taglit",
            "Cómo conoció Hillel",
            "Estudios",
            "Experiencia comunitaria",
            "tematicasInteres",
            "propuestasInteres",
            "observaciones",
            "Perfil Ok?",
        ]
    )

    profiles = Profile.objects.all()

    for p in profiles:
        if p is None:
            return Http404("Perfil no encontrado")
        if p.validado:
            writer.writerow(
                [
                    p,
                    p.user.email,
                    p.nombre,
                    p.apellido,
                    p.fechaNacimiento,
                    p.edad,
                    p.whatsapp,
                    p.instagram,
                    p.onward,
                    p.taglit,
                    p.comoConociste,
                    p.estudios,
                    p.experienciaComunitaria,
                    p.tematicasInteresSTR,
                    p.propuestasInteresSTR,
                    p.observaciones,
                    p.perfil_ok,
                ]
            )
    return response


def DescargarCuestionarios(request):
    local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    response = HttpResponse(content="")
    response["Content-Disposition"] = (
        "attachment; filename=Cuestionarios-" + str(datetime.now(local_tz)) + ".csv"
    )
    writer = csv.writer(response, dialect="excel")
    response.write("\ufeff".encode("utf8"))
    writer.writerow(
        [
            "Actividad",
            "Pregunta1",
            "Pregunta2",
            "Pregunta3",
            "Pregunta4",
            "Pregunta5",
            "Pregunta6",
            "Pregunta7",
            "Pregunta8",
            "Pregunta9",
            "Pregunta10",
            "Pregunta11",
            "Pregunta12",
            "Pregunta13",
            "Pregunta14",
            "Pregunta15",
            "Pregunta16",
            "Pregunta17",
            "Pregunta18",
            "Pregunta19",
            "Pregunta20",
        ]
    )

    cuestionarios = Cuestionario.objects.all()

    for c in cuestionarios:
        if c is None:
            return Http404("Cuestionario no encontrado")
        writer.writerow(
            [
                c.page.titleSTR,
                c.pregunta1,
                c.pregunta2,
                c.pregunta3,
                c.pregunta4,
                c.pregunta5,
                c.pregunta6,
                c.pregunta7,
                c.pregunta8,
                c.pregunta9,
                c.pregunta10,
                c.pregunta11,
                c.pregunta12,
                c.pregunta13,
                c.pregunta14,
                c.pregunta15,
                c.pregunta16,
                c.pregunta17,
                c.pregunta18,
                c.pregunta19,
                c.pregunta20,
            ]
        )
    return response


def DescargarCuestionariosRespuestas(request):
    local_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    response = HttpResponse(content="")
    response["Content-Disposition"] = (
        "attachment; filename=Cuestionarios-Respuestas-"
        + str(datetime.now(local_tz))
        + ".csv"
    )
    writer = csv.writer(response, dialect="excel")
    response.write("\ufeff".encode("utf8"))
    writer.writerow(
        [
            "Actividad",
            "Pregunta1",
            "Pregunta2",
            "Pregunta3",
            "Pregunta4",
            "Pregunta5",
            "Pregunta6",
            "Pregunta7",
            "Pregunta8",
            "Pregunta9",
            "Pregunta10",
            "Pregunta11",
            "Pregunta12",
            "Pregunta13",
            "Pregunta14",
            "Pregunta15",
            "Pregunta16",
            "Pregunta17",
            "Pregunta18",
            "Pregunta19",
            "Pregunta20",
            "Usuario",
            "Respuesta1",
            "Respuesta2",
            "Respuesta3",
            "Respuesta4",
            "Respuesta5",
            "Respuesta6",
            "Respuesta7",
            "Respuesta8",
            "Respuesta9",
            "Respuesta10",
            "Respuesta11",
            "Respuesta12",
            "Respuesta13",
            "Respuesta14",
            "Respuesta15",
            "Respuesta16",
            "Respuesta17",
            "Respuesta18",
            "Respuesta19",
            "Respuesta20",
            "Fecha de compleción",
        ]
    )

    cuestionariosRespuesta = CuestionarioRespuesta.objects.all()

    for c in cuestionariosRespuesta:
        if c is None:
            return Http404("Cuestionario no encontrado")
        writer.writerow(
            [
                c.page.titleSTR,
                c.pregunta1,
                c.pregunta2,
                c.pregunta3,
                c.pregunta4,
                c.pregunta5,
                c.pregunta6,
                c.pregunta7,
                c.pregunta8,
                c.pregunta9,
                c.pregunta10,
                c.pregunta11,
                c.pregunta12,
                c.pregunta13,
                c.pregunta14,
                c.pregunta15,
                c.pregunta16,
                c.pregunta17,
                c.pregunta18,
                c.pregunta19,
                c.pregunta20,
                c.user.username,
                c.respuesta1,
                c.respuesta2,
                c.respuesta3,
                c.respuesta4,
                c.respuesta5,
                c.respuesta6,
                c.respuesta7,
                c.respuesta8,
                c.respuesta9,
                c.respuesta10,
                c.respuesta11,
                c.respuesta12,
                c.respuesta13,
                c.respuesta14,
                c.respuesta15,
                c.respuesta16,
                c.respuesta17,
                c.respuesta18,
                c.respuesta19,
                c.respuesta20,
                c.updated,
            ]
        )
    return response


def Exportar(request):
    if request.user.is_authenticated:
        return render(request, "pages/exportar.html")
    raise Http404("Usuario no está autenticado")
