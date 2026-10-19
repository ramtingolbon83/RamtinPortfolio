from datetime import date

from django.utils import timezone

# مرورگرهای واقعی این کلمات را در User-Agent ندارند؛ ربات‌ها و پیش‌نمایش لینک‌ها (تلگرام، واتساپ و...) دارند
BOT_MARKERS = (
    "bot", "crawl", "spider", "slurp", "preview", "headless",
    "curl", "wget", "python-requests", "httpx", "go-http-client",
    "facebookexternalhit", "whatsapp", "telegram",
)
SEEN_LIMIT = 200  # حداکثر تعداد مقاله‌هایی که در session هر بازدیدکننده یادآوری می‌شود


def is_bot(request) -> bool:
    ua = request.META.get("HTTP_USER_AGENT", "").lower()
    return not ua or any(marker in ua for marker in BOT_MARKERS)


def should_count_view(request, post_pk) -> bool:
    """بازدید فقط وقتی شمرده می‌شود که: درخواست GET باشد، ربات نباشد،
    ادمین (خودت) نباشد و این بازدیدکننده قبلاً این مقاله را ندیده باشد."""
    if request.method != "GET" or is_bot(request):
        return False
    if request.user.is_authenticated and request.user.is_staff:
        return False

    seen = request.session.get("viewed_posts", [])
    if post_pk in seen:
        return False

    seen.append(post_pk)
    request.session["viewed_posts"] = seen[-SEEN_LIMIT:]
    return True


def calculate_age(birth_date: date, today: date | None = None) -> int:
    """سن کامل؛ دقیقاً در روز تولد یک سال اضافه می‌شود."""
    today = today or timezone.localdate()
    before_birthday = (today.month, today.day) < (birth_date.month, birth_date.day)
    return today.year - birth_date.year - before_birthday