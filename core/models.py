import secrets

from django_ckeditor_5.fields import CKEditor5Field
from django.db import models
from django.urls import reverse


def generate_slug():
    return secrets.token_urlsafe(8)


class Profile(models.Model):
    """The resume owner's identity/contact info. In practice a single row."""

    full_name = models.CharField(max_length=200)
    headline = models.CharField(max_length=200, blank=True, help_text="e.g. Senior Backend Engineer")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to="profile/", blank=True, null=True)
    summary = CKEditor5Field(blank=True, config_name="default", help_text="Optional short intro paragraph.")

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profile"

    def __str__(self):
        return self.full_name or "Profile"


class ProfileLink(models.Model):
    """A contact/social link shown in the header, e.g. LinkedIn, GitHub, Portfolio."""

    profile = models.ForeignKey(Profile, related_name="links", on_delete=models.CASCADE)
    label = models.CharField(max_length=50)
    url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.label}"


class Section(models.Model):
    """A top-level resume section, e.g. Employment History, Education, Skills.

    New sections can be added/configured from the portal without a code change.
    """

    LAYOUT_TIMELINE = "timeline"
    LAYOUT_SKILLS = "skills"
    LAYOUT_TEXT = "text"
    LAYOUT_CHOICES = [
        (LAYOUT_TIMELINE, "Timeline — dated entries with expandable bullets (e.g. Employment, Education)"),
        (LAYOUT_SKILLS, "Skills — categories of tags, expandable per category"),
        (LAYOUT_TEXT, "Text block — a simple rich-text blob, no entries"),
    ]

    title = models.CharField(max_length=100)
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default=LAYOUT_TIMELINE)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, help_text="Inactive sections are hidden everywhere, including the portal builder.")
    intro_text = CKEditor5Field(
        blank=True, config_name="default", help_text="Optional text shown under the section title (used by 'Text block' layout)."
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Entry(models.Model):
    """One card within a section: a job, a degree, or a skill category."""

    section = models.ForeignKey(Section, related_name="entries", on_delete=models.CASCADE)
    heading = models.CharField(max_length=200, help_text="Job title / Degree / Skill category name")
    subheading = models.CharField(max_length=200, blank=True, help_text="Company / Institution")
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    summary = models.CharField(
        max_length=300, blank=True, help_text="One-line summary shown even when the card is collapsed."
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-start_date", "id"]
        verbose_name_plural = "Entries"

    def __str__(self):
        return f"{self.heading} — {self.section.title}"

    @property
    def date_range_display(self):
        if not self.start_date:
            return ""
        start = self.start_date.strftime("%b %Y")
        if self.is_current:
            end = "Present"
        elif self.end_date:
            end = self.end_date.strftime("%b %Y")
        else:
            return start
        return f"{start} – {end}"


class DetailItem(models.Model):
    """A single bullet under an Entry: a job duty, a course, a skill tag.

    Individually selectable per PublicPage from the portal.
    """

    entry = models.ForeignKey(Entry, related_name="details", on_delete=models.CASCADE)
    content = CKEditor5Field(
        config_name="default", help_text="For Skills entries, just the skill name; formatting is ignored there."
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        from django.utils.html import strip_tags

        text = strip_tags(self.content)
        return text[:60]


class PublicPage(models.Model):
    """An employer/position-targeted rendering of the resume at a private URL."""

    slug = models.SlugField(max_length=32, unique=True, default=generate_slug, editable=False)
    employer_name = models.CharField(max_length=200)
    position_title = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True, help_text="Private notes about this application. Never shown publicly.")
    is_published = models.BooleanField(
        default=True, help_text="If off, the link 404s for the public but still works for you when logged in."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    sections = models.ManyToManyField(Section, related_name="public_pages", blank=True)
    entries = models.ManyToManyField(Entry, related_name="public_pages", blank=True)
    details = models.ManyToManyField(DetailItem, related_name="public_pages", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        label = self.employer_name
        if self.position_title:
            label += f" — {self.position_title}"
        return label

    def get_absolute_url(self):
        return reverse("sitepublic:resume", kwargs={"slug": self.slug})


class PageView(models.Model):
    """One recorded visit to a PublicPage, for the owner's own analytics."""

    page = models.ForeignKey(PublicPage, related_name="page_views", on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    referrer = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.page.employer_name} @ {self.viewed_at:%Y-%m-%d %H:%M}"
