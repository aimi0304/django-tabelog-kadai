from django.db import models
from django.core.validators import RegexValidator
from users.models import User


class Restaurant(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    store_name = models.CharField(max_length=50, verbose_name='店舗名')
    store_image = models.ImageField(blank=True, default='noImage.png', verbose_name='店舗写真')
    store_description = models.TextField(max_length=200, verbose_name='店舗説明')
    lowest_price = models.PositiveSmallIntegerField(verbose_name='最低価格')
    hightest_price = models.PositiveSmallIntegerField(verbose_name='最高価格')
    postal_code = models.CharField(max_length=8, verbose_name='郵便番号')
    access = models.CharField(blank=True, null=True, max_length=100, verbose_name='アクセス')
    opening_time = models.TimeField(default="09:00:00", verbose_name='開店時間')
    closing_time = models.TimeField(default="21:00:00", verbose_name="閉店時間")
    closed_info = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='定休日')
    seating_capacity = models.CharField(max_length=50, verbose_name='座席数')
    created_at = models.DateTimeField(auto_now=True, verbose_name="作成日")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="更新日")


class Review(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザーID')
    restaurants_id = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='店舗ID', related_name="restaurants_id")
    content = models.TextField(max_length=200, verbose_name='口コミ')
    score = models.PositiveSmallIntegerField(verbose_name='評価')
    number_of_people = models.PositiveSmallIntegerField(verbose_name='来店人数')
    purpose = models.CharField(max_length=50, verbose_name='来店目的')
    created_at = models.DateTimeField(auto_now=True, verbose_name="作成日")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="更新日")


class Category(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    category_name = models.CharField(max_length=20, default='', verbose_name='カテゴリー名')
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="作成日")
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="更新日")


class CategoryRestaurant(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    restaurants_id = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='店舗ID')
    categories_id = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='カテゴリーID', related_name="categories_id")
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="作成日")
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="更新日")


class Favorite(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザーID')
    restaurant_id = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='店舗ID', related_name="Favorite_restaurant_id")
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="作成日")
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="更新日")

    class Meta:
        unique_together = ('user_id', 'restaurant_id')


class Reservations(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザーID')
    restaurant_id = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='店舗ID', related_name="Reservations_restaurant_id")
    reserved_datetime = models.DateTimeField(verbose_name="予約日時")
    number_of_people = models.PositiveSmallIntegerField(verbose_name='人数')
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="作成日")
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="更新日")

class StripeCustomer(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザーID')
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='カスタマーID')
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='サブスクID')
