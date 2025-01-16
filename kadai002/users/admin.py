from django.contrib import admin
from django.contrib.auth import get_user_model

Users = get_user_model()

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "last_name", "first_name")
    search_fields = ("last_name", "first_name",)

admin.site.register(Users, UserAdmin)
