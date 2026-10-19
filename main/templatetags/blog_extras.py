import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdown")
def markdown_filter(value):
    html = md.markdown(
        value or "",
        extensions=["fenced_code", "tables", "nl2br", "sane_lists"],
    )
    return mark_safe(html)