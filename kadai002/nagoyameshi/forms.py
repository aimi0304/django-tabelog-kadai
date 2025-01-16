from django import forms
from .models import Reservations

# 予約用フォーム
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservations
        fields = ('reserved_datetime', 'number_of_people')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
