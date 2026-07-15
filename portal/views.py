from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from core.models import Profile, PublicPage, Section
from sitepublic.rendering import build_resume_context

from .forms import PublicPageForm


@login_required
def dashboard(request):
    profile = Profile.objects.first()
    pages = PublicPage.objects.all()[:5]
    return render(
        request,
        "portal/dashboard.html",
        {
            "profile": profile,
            "pages": pages,
            "page_count": PublicPage.objects.count(),
            "section_count": Section.objects.filter(is_active=True).count(),
        },
    )


@login_required
def page_list(request):
    pages = PublicPage.objects.annotate(view_total=Count("page_views"))
    return render(request, "portal/page_list.html", {"pages": pages})


@login_required
def page_create(request):
    if request.method == "POST":
        form = PublicPageForm(request.POST)
        if form.is_valid():
            page = form.save()
            return redirect("portal:page_builder", pk=page.pk)
    else:
        form = PublicPageForm()
    return render(request, "portal/page_form.html", {"form": form})


@login_required
def page_builder(request, pk):
    page = get_object_or_404(PublicPage, pk=pk)

    if request.method == "POST":
        form = PublicPageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            page.sections.set(request.POST.getlist("sections"))
            page.entries.set(request.POST.getlist("entries"))
            page.details.set(request.POST.getlist("details"))
            return redirect("portal:page_builder", pk=page.pk)
    else:
        form = PublicPageForm(instance=page)

    sections = Section.objects.filter(is_active=True).prefetch_related("entries__details")

    return render(
        request,
        "portal/page_builder.html",
        {
            "page": page,
            "form": form,
            "sections": sections,
            "selected_sections": set(page.sections.values_list("id", flat=True)),
            "selected_entries": set(page.entries.values_list("id", flat=True)),
            "selected_details": set(page.details.values_list("id", flat=True)),
        },
    )


@login_required
@require_http_methods(["POST"])
def page_delete(request, pk):
    page = get_object_or_404(PublicPage, pk=pk)
    page.delete()
    return redirect("portal:page_list")


@login_required
def page_pdf(request, pk):
    from weasyprint import HTML

    page = get_object_or_404(PublicPage, pk=pk)
    context = build_resume_context(page)
    # Embed the photo as a data URI so PDF rendering never needs to fetch a
    # URL back from this same server (which can deadlock a single-threaded
    # dev server mid-request).
    context["photo_data_uri"] = _photo_data_uri(context["profile"])
    html_string = render_to_string("sitepublic/resume_pdf.html", context)
    pdf_bytes = HTML(string=html_string).write_pdf()

    filename = "resume-{}.pdf".format(page.employer_name or page.slug).replace(" ", "-")
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _photo_data_uri(profile):
    if not profile or not profile.photo:
        return None
    import base64

    try:
        with profile.photo.open("rb") as f:
            data = f.read()
    except (OSError, ValueError):
        return None
    ext = profile.photo.name.rsplit(".", 1)[-1].lower()
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}.get(ext, "jpeg")
    return f"data:image/{mime};base64,{base64.b64encode(data).decode('ascii')}"


@login_required
def analytics_list(request):
    pages = PublicPage.objects.annotate(view_total=Count("page_views")).order_by("-view_total")
    return render(request, "portal/analytics_list.html", {"pages": pages})


@login_required
def analytics_detail(request, pk):
    page = get_object_or_404(PublicPage, pk=pk)
    views = page.page_views.all()[:100]
    return render(
        request,
        "portal/analytics_detail.html",
        {"page": page, "views": views, "total": page.page_views.count()},
    )
