from typing import ClassVar

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# =====================================================================
# ۱. مدل نمونه کارها (نمایش پروژه‌هایی مثل ربات تلگرام، مینی‌اپ، ابزارهای امنیتی)
# =====================================================================
class Project(models.Model):
    CATEGORY_CHOICES : ClassVar= [
        ('telegram_bot', 'ساخت ربات تلگرام'),
        ('web_design', 'طراحی اپلیکیشن/وب'),
        ('security', 'ابزارهای هک/امنیت'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="عنوان پروژه")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="دسته‌بندی")
    image = models.ImageField(upload_to='projects/', verbose_name="تصویر نمونه کار")
    link = models.URLField(blank=True, null=True, verbose_name="لینک پروژه (گیت‌هاب/سایت)")

    class Meta:
        verbose_name = "نمونه کار"
        verbose_name_plural = "نمونه کارها"

    def __str__(self):
        return self.title


# =====================================================================
# ۲. مدل نظرات مشتریان (فیدبک‌هایی که از کارفرماها یا بقیه در فرانت‌اند نشان می‌دهی)
# =====================================================================
class Testimonial(models.Model):

    STATUS_CHOICES = (
        ("pending", "در انتظار تایید"),
        ("approved", "تایید شده"),
    )

    name = models.CharField(max_length=150, verbose_name="نام شخص")

    role = models.CharField(
        max_length=150,
        verbose_name="سمت / شرکت"
    )

    avatar = models.ImageField(
        upload_to="testimonials/",
        blank=True,
        null=True,
        verbose_name="عکس پروفایل"
    )

    comment = models.TextField(
        verbose_name="متن نظر"
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        verbose_name="امتیاز"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="وضعیت"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "نظر مشتری"
        verbose_name_plural = "نظرات مشتریان"

    def __str__(self):
        return self.name

# =====================================================================
# ۳. مدل تماس با ما / ثبت ایده‌ها (دیتایی که بدون لاگین از کاربر مهمان دریافت و ذخیره می‌شود)
# =====================================================================
class ContactMessage(models.Model):
    name = models.CharField(max_length=150, verbose_name="نام فرستنده")
    email = models.EmailField(verbose_name="ایمیل")
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    message = models.TextField(verbose_name="متن پیام / ایده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    class Meta:
        verbose_name = "پیام دریافتی"
        verbose_name_plural = "پیام‌های دریافتی"

    def __str__(self):
        return f"پیام از {self.name} - {self.subject}"


# =====================================================================
# ۴. مدل وبلاگ (مقالات و اخباری که خودت منتشر می‌کنی و بقیه بدون لاگین می‌خوانند)
# =====================================================================
class BlogPost(models.Model):
    CATEGORY_CHOICES : ClassVar = [
        ('django', 'جنگو'),
        ('python', 'پایتون'),
        ('security', 'امنیت'),
        ('telegram', 'تلگرام'),
        ('linux', 'لینوکس'),
        ('general', 'عمومی'),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        verbose_name="دسته‌بندی"
    )
    STATUS_CHOICES : ClassVar = [
        ('draft', 'پیش‌نویس'),
        ('published', 'منتشر شده'),
    ]

    title = models.CharField(max_length=250, verbose_name="عنوان مقاله")
    slug = models.SlugField(unique=True, allow_unicode=True, verbose_name="اسلاگ (برای لینک URL)")
    content = models.TextField(verbose_name="متن مقاله")
    image = models.ImageField(upload_to='blog/', verbose_name="تصویر اصلی مقاله")
    views = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="وضعیت انتشار")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ آخرین به‌روزرسانی")

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات و اخبار"
        ordering = ('-created_at',) 
    def __str__(self):
        return self.title