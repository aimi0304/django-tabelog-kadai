from django.contrib import admin
from .models import Restaurant, Review, Category, CategoryRestaurant
from django.db.models import Q
from django.forms import ChoiceField, ModelForm

WEEKDAY_CHOICES = [
    (1, '月曜日'),
    (2, '火曜日'),
    (3, '水曜日'),
    (4, '木曜日'),
    (5, '金曜日'),
    (6, '土曜日'),
    (7, '日曜日'),
]

class RestaurantAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 定休日のフィールドにカスタムウィジェットを適用
        self.fields['closed_info'] = ChoiceField(choices=WEEKDAY_CHOICES, label='定休日')

class RestaurantAdmin(admin.ModelAdmin):
    form = RestaurantAdminForm
    list_display = ("id", "store_name", "get_closed_info_display", "get_categories")
    search_fields = ("store_name", "categoryrestaurant__categories_id__category_name")

    def get_closed_info_display(self, obj):
        WEEKDAY_DISPLAY = dict(WEEKDAY_CHOICES)
        return WEEKDAY_DISPLAY.get(obj.closed_info, '未設定')
    get_closed_info_display.short_description = '定休日'

    def get_categories(self, obj):
        categories = obj.categoryrestaurant_set.all().values_list('categories_id__category_name', flat=True)
        return ", ".join(categories)
    get_categories.short_description = 'カテゴリー'

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset |= self.model.objects.filter(
                Q(categoryrestaurant__categories_id__category_name__icontains=search_term)
            )
        return queryset, use_distinct


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id","category_name",)
    search_fields = ("category_name",)

class CategoryRestaurantAdmin(admin.ModelAdmin):
    list_display = ("id", "get_restaurant_name", "get_category_name", "created_at", "updated_at")
    search_fields = ("restaurants_id__store_name", "categories_id__category_name")

    def get_restaurant_name(self, obj):
        return obj.restaurants_id.store_name
    get_restaurant_name.short_description = '店舗名'

    def get_category_name(self, obj):
        return obj.categories_id.category_name
    get_category_name.short_description = 'カテゴリー名'


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Review)
admin.site.register(CategoryRestaurant, CategoryRestaurantAdmin)
admin.site.register(Category, CategoryAdmin)