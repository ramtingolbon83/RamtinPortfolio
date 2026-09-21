#!/usr/bin/env python3
from django.db.models import F
from django.shortcuts import get_object_or_404, render

from .models import BlogPost, ContactMessage, Project, Testimonial

# Create your views here.


def home(request):
    success_message = None
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            subject=request.POST.get("subject"),
            message=request.POST.get("message"),
        )
        success_message = "پیام شما با موفقیت ارسال شد"
    projects = Project.objects.all()
    testimonials = Testimonial.objects.filter(status="approved")
    blogs = BlogPost.objects.filter(status="published")

    context = {
        "projects": projects,
        "testimonials": testimonials,
        "blogs": blogs,
        "success": success_message,
    }

    return render(request, "index.html", context)


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status="published")

    post.views = F("views") + 1
    post.save(update_fields=["views"])
    post.refresh_from_db(fields=["views"])

    return render(request, "detail.html", {"post": post})
