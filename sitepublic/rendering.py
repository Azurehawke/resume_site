from core.models import Profile


def build_resume_context(page):
    """Shared context builder for the public resume page and its PDF export.

    Filters every section/entry/detail down to only what's been checked off
    for this specific PublicPage.
    """
    profile = Profile.objects.prefetch_related("links").first()

    sections = []
    for section in page.sections.filter(is_active=True).order_by("order", "id"):
        entries = []
        for entry in section.entries.filter(public_pages=page).order_by("order", "-start_date", "id"):
            details = list(entry.details.filter(public_pages=page).order_by("order", "id"))
            entries.append({"entry": entry, "details": details})
        sections.append({"section": section, "entries": entries})

    return {
        "profile": profile,
        "sections": sections,
        "page": page,
    }
