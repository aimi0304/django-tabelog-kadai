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
        restaurant = self.instance.restaurant_id

        if reserved_datetime <= now() + timedelta(hours=2):
            raise ValidationError('予約は現在時刻から2時間以上先である必要があります。')
        # 定休日の確認
        weekday = reserved_datetime.weekday() + 1  # Pythonのweekdayは0が月曜日、1が火曜日... なので1を加える
        if restaurant.closed_info == weekday:
            raise ValidationError('定休日です。別の日付を選択してください。')

        # 営業時間の確認
        if not (restaurant.opening_time <= reserved_datetime.time() <= restaurant.closing_time):
            raise ValidationError('営業時間外です。別の時間を選択してください。')
        return reserved_datetime
