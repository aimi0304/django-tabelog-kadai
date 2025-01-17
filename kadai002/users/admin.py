from django.contrib import admin
from django.contrib.auth import get_user_model
from django.forms import ChoiceField, ModelForm

Users = get_user_model()

GENDER_CHOICES = [
    (1, '男性'),
    (2, '女性'),
]

class UserAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 定休日のフィールドにカスタムウィジェットを適用
        self.fields['gender'] = ChoiceField(choices=GENDER_CHOICES, label='定休日')


class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = ("username", "email", "last_name", "first_name")
    search_fields = ("username", "last_name", "first_name",)

admin.site.register(Users, UserAdmin)
