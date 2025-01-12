"""
URL configuration for nagoyameshi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from nagoyameshi import views as nagoya_views
from users import views as users_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', nagoya_views.TopView.as_view(), name="top"),
    path('login/', users_views.LoginView.as_view(), name="login"),
    path('logout/', users_views.LogoutView.as_view(), name="logout"),
    path('nagoyameshi/', nagoya_views.RestaulantSearchView.as_view(), name="search_result"),
    path('signup/', users_views.SignupView.as_view(), name="signup"),
    path('activate/<uid64>/<token>/', users_views.ActivateView.as_view(), name="activate"),
    path('password_reset/', users_views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', users_views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', users_views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', users_views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('mypage/<int:pk>/', users_views.MypageView.as_view(), name="mypage"),
    path('user_update/<int:pk>/', users_views.UserUpdateView.as_view(), name='user_update'),
    path('user_upgrade/<int:pk>/', users_views.UserUpgradeView.as_view(), name='user_upgrade'),
    path('user_delete/<int:pk>/', users_views.UserDeleteView.as_view(), name='user_delete'),
    path('nagoyameshi/detail/<int:pk>/', nagoya_views.RestaurantDetail.as_view(), name='restaurant_detail'),
    path('favorite_restaurants/<int:pk>/', users_views.FavoriteRestaurantsView.as_view(), name='favorite_restaurants'),
    path('review_post/<int:pk>/', users_views.ReviewPostView.as_view(), name="review_post"),
    path('posted_list/<int:pk>/', users_views.PostedListView.as_view(), name="posted_list"),
    path('delete_review/<int:pk>/', users_views.DeleteView.as_view(), name="delete_review"),
    path('reservation/<int:pk>/', nagoya_views.ReservationView.as_view(), name="reservation"),
    path('reservation/completed/', nagoya_views.ReservationCompleted.as_view(), name='reservation_completed'),
    path('reserved_list/<int:pk>/', users_views.ReservedListView.as_view(), name='reserved_list'),
    path('cancel_reservation/<int:pk>/', users_views.CancelReservationView.as_view(), name="cancel_reservation"),
    path('config/', users_views.StripeConfigView.as_view(), name="config"),
    path('create-checkout-session/', users_views.CreateCheckoutSessionView.as_view(), name="checkout"),
    path('success/', users_views.SuccessView.as_view(), name="success"),
    path('cancel/', users_views.CancelView.as_view(), name="cancel"),
    path('cancel-subscription/', users_views.CancelSubscriptionView.as_view(), name='cancel_subscription'),
    path('webhook/', users_views.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('update_card/', users_views.UpdateCardView.as_view(), name='update_card'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
