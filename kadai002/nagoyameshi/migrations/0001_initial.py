# Generated by Django 5.1.4 on 2025-01-15 05:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(default='', max_length=20, verbose_name='カテゴリー名')),
                ('created_at', models.DateTimeField(auto_now=True, null=True, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='更新日')),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('store_name', models.CharField(max_length=50, verbose_name='店舗名')),
                ('store_image', models.ImageField(blank=True, default='noImage.png', upload_to='', verbose_name='店舗写真')),
                ('store_description', models.TextField(max_length=200, verbose_name='店舗説明')),
                ('lowest_price', models.PositiveSmallIntegerField(verbose_name='最低価格')),
                ('hightest_price', models.PositiveSmallIntegerField(verbose_name='最高価格')),
                ('postal_code', models.CharField(max_length=8, verbose_name='郵便番号')),
                ('access', models.CharField(blank=True, max_length=100, null=True, verbose_name='アクセス')),
                ('opening_time', models.TimeField(default='09:00:00', verbose_name='開店時間')),
                ('closing_time', models.TimeField(default='21:00:00', verbose_name='閉店時間')),
                ('closed_info', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='定休日')),
                ('seating_capacity', models.CharField(max_length=50, verbose_name='座席数')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(auto_now_add=True, verbose_name='更新日')),
            ],
        ),
        migrations.CreateModel(
            name='Reservations',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('reserved_datetime', models.DateTimeField(verbose_name='予約日時')),
                ('number_of_people', models.PositiveSmallIntegerField(verbose_name='人数')),
                ('created_at', models.DateTimeField(auto_now=True, null=True, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='更新日')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザーID')),
                ('restaurant_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Reservations_restaurant_id', to='nagoyameshi.restaurant', verbose_name='店舗ID')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryRestaurant',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True, null=True, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='更新日')),
                ('categories_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories_id', to='nagoyameshi.category', verbose_name='カテゴリーID')),
                ('restaurants_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nagoyameshi.restaurant', verbose_name='店舗ID')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=200, verbose_name='口コミ')),
                ('score', models.PositiveSmallIntegerField(verbose_name='評価')),
                ('number_of_people', models.PositiveSmallIntegerField(verbose_name='来店人数')),
                ('purpose', models.CharField(max_length=50, verbose_name='来店目的')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(auto_now_add=True, verbose_name='更新日')),
                ('restaurants_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurants_id', to='nagoyameshi.restaurant', verbose_name='店舗ID')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザーID')),
            ],
        ),
        migrations.CreateModel(
            name='StripeCustomer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_customer_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='カスタマーID')),
                ('stripe_subscription_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='サブスクID')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザーID')),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True, null=True, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='更新日')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザーID')),
                ('restaurant_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Favorite_restaurant_id', to='nagoyameshi.restaurant', verbose_name='店舗ID')),
            ],
            options={
                'unique_together': {('user_id', 'restaurant_id')},
            },
        ),
    ]
