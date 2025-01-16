from django.contrib import admin
from .models import Restaurant, Review, Category, CategoryRestaurant
from django.db.models import Q

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("id", "store_name", "get_categories")
    search_fields = ("store_name", "categoryrestaurant__categories_id__category_name")

    def get_categories(self, obj):
        # Restaurantに関連するすべてのカテゴリー名を取得してカンマ区切りで表示
        categories = obj.categoryrestaurant_set.all().values_list('categories_id__category_name', flat=True)
        return ", ".join(categories)

    get_categories.short_description = 'カテゴリー'

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        # カテゴリー名で検索するためのカスタムフィルター
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