from django.contrib import admin

from .models import DetailItem, Entry, PageView, Profile, ProfileLink, PublicPage, Section


class ProfileLinkInline(admin.TabularInline):
    model = ProfileLink
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [ProfileLinkInline]
    list_display = ("full_name", "headline", "email")

    def has_add_permission(self, request):
        # Keep this a singleton — everything hangs off one Profile record.
        if Profile.objects.exists():
            return False
        return super().has_add_permission(request)


class EntryInline(admin.TabularInline):
    model = Entry
    extra = 0
    fields = ("heading", "subheading", "location", "start_date", "end_date", "is_current", "order")
    show_change_link = True
    ordering = ("order",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "layout", "order", "is_active")
    list_editable = ("order", "is_active")
    inlines = [EntryInline]


class DetailItemInline(admin.StackedInline):
    model = DetailItem
    extra = 1
    fields = ("content", "order")


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ("heading", "section", "subheading", "date_range_display", "order")
    list_filter = ("section",)
    inlines = [DetailItemInline]


@admin.register(PublicPage)
class PublicPageAdmin(admin.ModelAdmin):
    list_display = ("employer_name", "position_title", "slug", "is_published", "view_count", "created_at")
    readonly_fields = ("slug", "created_at", "updated_at")
    filter_horizontal = ("sections", "entries", "details")
    search_fields = ("employer_name", "position_title", "slug")

    @admin.display(description="Views")
    def view_count(self, obj):
        return obj.page_views.count()


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("page", "viewed_at", "ip_address")
    list_filter = ("page",)
    readonly_fields = ("page", "viewed_at", "ip_address", "user_agent", "referrer")

    def has_add_permission(self, request):
        return False
