from django.http import Http404
from django.shortcuts import get_object_or_404, render

from core.models import PageView, PublicPage

from .rendering import build_resume_context


def resume(request, slug):
    page = get_object_or_404(PublicPage, slug=slug)

    if not page.is_published and not request.user.is_authenticated:
        raise Http404

    if not request.user.is_authenticated:
        PageView.objects.create(
            page=page,
            ip_address=_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
            referrer=request.META.get("HTTP_REFERER", "")[:300],
        )

    context = build_resume_context(page)
    context["is_preview"] = request.user.is_authenticated
    return render(request, "sitepublic/resume.html", context)


def _client_ip(request):
    # Cloudflare Tunnel sets CF-Connecting-IP; fall back to a standard proxy header.
    cf_ip = request.META.get("HTTP_CF_CONNECTING_IP")
    if cf_ip:
        return cf_ip
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
