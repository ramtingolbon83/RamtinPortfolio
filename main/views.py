#!/usr/bin/env python3
import time

from django.conf import settings
from django.contrib import messages
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm
from .models import BlogPost, Project, Testimonial
from .utils import calculate_age, should_count_view

THROTTLE_SECONDS = 30


def home(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        last = request.session.get("last_contact", 0)

        if time.time() - last < THROTTLE_SECONDS:
            messages.error(request, "لطفاً چند لحظه صبر کنید و دوباره تلاش کنید")
        elif form.is_valid():
            # اگر honeypot پر باشد، ربات است: بی‌صدا نادیده می‌گیریم
            if not form.cleaned_data["website"]:
                form.save()
            request.session["last_contact"] = time.time()
            messages.success(request, "پیام شما با موفقیت ارسال شد")
            return redirect("home")
        else:
            messages.error(request, "لطفاً فرم را درست پر کنید")
    else:
        form = ContactForm()

    context = {
        "projects": Project.objects.prefetch_related("extra_images"),
        "testimonials": Testimonial.objects.filter(status="approved"),
        "blogs": BlogPost.objects.filter(status="published"),
        "form": form,
        "age": calculate_age(settings.BIRTH_DATE) if settings.BIRTH_DATE else None,
    }
    return render(request, "index.html", context)


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status="published")

    if should_count_view(request, post.pk):
        BlogPost.objects.filter(pk=post.pk).update(views=F("views") + 1)
        post.refresh_from_db(fields=["views"])

    return render(request, "detail.html", {"post": post})
