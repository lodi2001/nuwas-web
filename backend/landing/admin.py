from django.contrib import admin
from .models import (
    SiteSettings,
    HeroSection,
    StatItem,
    SectionHeader,
    LearnCard,
    ServiceCard,
    Product,
    NavLink,
    FooterLink,
    ContactSubmission,
    VideoBanner,
)


class SingletonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = [
        ("Identity", {"fields": ("site_name_ar", "site_name_en", "logo")}),
        ("Contact", {"fields": ("email", "phone", "address_ar", "address_en")}),
        ("Social", {"fields": ("linkedin_url", "twitter_url", "instagram_url")}),
        ("Footer", {"fields": ("footer_description_ar", "footer_description_en", "copyright_text_ar", "copyright_text_en")}),
    ]


@admin.register(HeroSection)
class HeroSectionAdmin(SingletonAdmin):
    fieldsets = [
        ("Heading", {"fields": ("heading_ar", "heading_en")}),
        ("Subheading", {"fields": ("subheading_ar", "subheading_en")}),
        ("Primary CTA", {"fields": ("cta_primary_text_ar", "cta_primary_text_en", "cta_primary_link")}),
        ("Secondary CTA", {"fields": ("cta_secondary_text_ar", "cta_secondary_text_en", "cta_secondary_link")}),
        ("Visual", {"fields": ("background_image",)}),
    ]


@admin.register(StatItem)
class StatItemAdmin(admin.ModelAdmin):
    list_display = ["number", "label_ar", "order"]
    list_editable = ["order"]


@admin.register(SectionHeader)
class SectionHeaderAdmin(admin.ModelAdmin):
    list_display = ["section", "title_ar"]


@admin.register(LearnCard)
class LearnCardAdmin(admin.ModelAdmin):
    list_display = ["title_ar", "icon_class", "order"]
    list_editable = ["order"]


@admin.register(ServiceCard)
class ServiceCardAdmin(admin.ModelAdmin):
    list_display = ["title_ar", "icon_class", "order"]
    list_editable = ["order"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "logo", "order"]
    list_editable = ["order"]


@admin.register(NavLink)
class NavLinkAdmin(admin.ModelAdmin):
    list_display = ["label_ar", "href", "order"]
    list_editable = ["order"]


@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display = ["label_ar", "href", "order"]
    list_editable = ["order"]


@admin.register(VideoBanner)
class VideoBannerAdmin(SingletonAdmin):
    fieldsets = [
        ("Video", {"fields": ("video", "is_active")}),
        ("Marketing Phrase", {"fields": ("phrase_ar", "phrase_en")}),
    ]


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "service_type", "is_read", "created_at"]
    list_filter = ["service_type", "is_read", "created_at"]
    search_fields = ["full_name", "email"]
    readonly_fields = [
        "full_name", "email", "phone", "organization",
        "service_type", "project_description", "created_at",
    ]
    actions = ["mark_as_read", "mark_as_unread"]

    def has_add_permission(self, request):
        return False

    @admin.action(description="Mark selected as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected as unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
