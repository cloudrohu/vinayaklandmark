from django.contrib import admin
from django.utils.html import mark_safe
from import_export.admin import ImportExportModelAdmin

from .models import (
    Setting, Slider, Leadership, Why_Choose,
    About, Contact_Page, Our_Team,
    Testimonial, FAQ, ImpactMetric, Enquiry,USP
)

@admin.register(Setting)
class SettingAdmin(ImportExportModelAdmin):

    list_display = (
        "site_name",
        "status",
        "phone",
        "email",
        "logo_preview",
    )

    list_filter = ("status",)
    search_fields = ("site_name", "email", "phone")
    readonly_fields = ("logo_preview",)

    fieldsets = (

        ("🧠 Basic Branding", {
            "fields": (
                "site_name",
                "logo",
                "offer_img",
                "favicon",
                "logo_preview",
            )
        }),

        ("🎨 Theme Colors", {
            "fields": (
                "header_footer_color",
                "text_color",
                "button_color",
                "rera_color",
            )
        }),

        ("📍 Contact Details", {
            "fields": (
                "address",
                "phone",
                "whatsapp",
                "email",
                "google_map",
            )
        }),

        ("✉️ SMTP / Email Settings", {
            "fields": (
                "smtpserver",
                "smtpemail",
                "smtppassword",
                "smtpport",
            )
        }),

        ("🌐 Social Media", {
            "fields": (
                "facebook",
                "instagram",
                "twitter",
                "youtube",
            )
        }),

        ("🔍 SEO Settings", {
            "fields": (
                "meta_title",
                "meta_description",
                "meta_keywords",
            )
        }),

        ("📑 Legal Pages", {
            "fields": (
                "privacy_policy",
                "terms_conditions",
                "disclaimer",
                "cookies",
            )
        }),

        ("⚙️ Extra Settings", {
            "fields": (
                "search_bg",
                "testmonial_bg",
                "rera_number",
                "current_project_rera",
                "footer_text",
                "googletagmanager",
                "copy_right",
                "status",
            )
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(
                f'<img src="{obj.logo.url}" width="100" style="border-radius:8px;">'
            )
        return "No Logo"

    logo_preview.short_description = "Logo Preview"

@admin.register(USP)
class USPAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "order",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )

    list_editable = (
        "order",
        "is_active",
    )

    ordering = (
        "order",
    )
@admin.register(Slider)
class SliderAdmin(ImportExportModelAdmin):
    list_display = ("title1","descriptions", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("title1", "descriptions")
    list_filter = ("is_active",)
    ordering = ("order",)

@admin.register(Leadership)
class LeadershipAdmin(ImportExportModelAdmin):
    list_display = (
        "name",
        "designation",
        "display_order",
        "is_active",
    )
    list_editable = ("display_order", "is_active")
    search_fields = ("name", "designation")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("👤 Profile", {
            "fields": ("name", "designation", "image", "bio")
        }),
        ("🔗 Links", {
            "fields": ("linkedin_url", "email")
        }),
        ("⚙️ Settings", {
            "fields": (
                "display_order",
                "is_active",
                "created_at",
                "updated_at",
            )
        }),
    )
@admin.register(Why_Choose)
class WhyChooseAdmin(ImportExportModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("title",)

@admin.register(About)
class AboutAdmin(ImportExportModelAdmin):

    list_display = (
        "title",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = ("is_active",)
    search_fields = ("title", "meta_title", "meta_keywords")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (

        ("Main About", {
            "fields": (
                "title",
                "subtitle",
                "content",
                "read_legacy",
            )
        }),

        ("About Details", {
            "fields": (
                "about_title",
                "about_subtitle",
                "about_content",
            )
        }),

        ("Mission & Vision", {
            "fields": (
                "mission_title",
                "mission_content",
                "vision_title",
                "vision_content",
            )
        }),

        ("SEO Content", {
            "fields": (
                "seo_title",
                "seo_description",
            )
        }),


        ("Background & Status", {
            "fields": (
                "is_active",
                "created_at",
                "updated_at",
            )
        }),

        ("Statistics", {
            "fields": (
                "years_of_experience",
                "happy_families",
            )
        }),

          ("About Us Hero", {
            "fields": (
                "hero_title",
                "hero_highlight",
                "hero_subtitle",
                "hero_description",
                "hero_background",
                "button_one_text",
                "button_one_link",
                "button_two_text",
                "button_two_link",
            )
        }),


        ("Images", {
            "fields": (
                "right_image1",
                "right_image2",
            )
        }),

        )

@admin.register(Contact_Page)
class ContactPageAdmin(ImportExportModelAdmin):
    list_display = ("heading", "phone", "email")
    search_fields = ("heading", "phone", "email")

@admin.register(Our_Team)
class OurTeamAdmin(ImportExportModelAdmin):
    list_display = ("name", "designation")
    search_fields = ("name", "designation")

@admin.register(Testimonial)
class TestimonialAdmin(ImportExportModelAdmin):
    list_display = ("name", "designation", "rating")
    list_filter = ("rating",)
    search_fields = ("name", "designation", "message")


@admin.register(FAQ)
class FAQAdmin(ImportExportModelAdmin):
    list_display = ("question",)
    search_fields = ("question", "answer")

@admin.register(ImpactMetric)
class ImpactMetricAdmin(ImportExportModelAdmin):
    list_display = ("title", "value", "order", "created_on")
    list_editable = ("order",)
    ordering = ("order",)
    search_fields = ("title", "value")

@admin.register(Enquiry)
class EnquiryAdmin(ImportExportModelAdmin):
    list_display = ("name", "email", "phone", "message", "created_at")