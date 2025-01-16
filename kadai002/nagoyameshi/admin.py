from django.contrib import admin
from .models import Restaurant, Review, Category, CategoryRestaurant
from django.db.models import Q

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("id","store_name",)
    search_fields = ("store_name",)

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
    list_display = ("id",)
    search_fields = ("restaurants_id", "categories_id")


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Review)
admin.site.register(CategoryRestaurant, CategoryRestaurantAdmin)
admin.site.register(Category, CategoryAdmin)