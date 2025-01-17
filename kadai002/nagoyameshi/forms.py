from django import forms
from .models import Reservations
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta

# 予約用フォーム
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservations
        fields = ('reserved_datetime', 'number_of_people')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_reserved_datetime(self):
        reserved_datetime = self.cleaned_data['reserved_datetime']
        if reserved_datetime <= now() + timedelta(hours=2):
            raise ValidationError('予約は現在時刻から2時間以上先である必要があります。')
        return reserved_datetime