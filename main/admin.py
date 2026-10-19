# Register your models here.
from typing import ClassVar

from django.contrib import admin
from jalali_date.admin import ModelAdminJalaliMixin
from unfold.admin import ModelAdmin, TabularInline

from .models import BlogPost, ContactMessage, Project, ProjectImage, Testimonial


class ProjectImageInline(TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "order")


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ("title", "category")
    list_filter = ("category",)
    search_fields = ("title",)
    inlines: ClassVar[list] = [ProjectImageInline]


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdminJalaliMixin, ModelAdmin):
    list_display = (
        "name",
        "role",
        "rating",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "rating",
    )

    search_fields = (
        "name",
        "role",
        "comment",
    )

    list_editable = ("status",)

    ordering = ("-created_at",)


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdminJalaliMixin, ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")
    readonly_fields = ("created_at",)
    search_fields = ("name", "email", "subject")


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdminJalaliMixin, ModelAdmin):
    list_display = ("title", "status", "views", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "content")
    prepopulated_fields: ClassVar = {
        "slug": ("title",),
    }
