from django.contrib import admin
from .models import Restaurant, Review, Category

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("store_name",)
    search_fields = ("store_name",)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_name",)
    search_fields = ("category_name",)


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Review)
admin.site.register(Category, CategoryAdmin)