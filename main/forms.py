from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # honeypot: کاربر واقعی این فیلد را نمی‌بیند، ربات‌ها پرش می‌کنند
    website = forms.CharField(required=False)

    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "message")

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise forms.ValidationError("پیام خیلی کوتاه است")
        if len(message) > 3000:
            raise forms.ValidationError("پیام خیلی طولانی است")
        return message