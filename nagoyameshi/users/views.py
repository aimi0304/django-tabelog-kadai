from django.views.generic import (
    TemplateView, CreateView, DetailView, UpdateView, FormView,
    DeleteView, ListView, View
)
from django.urls import reverse_lazy
from .forms import (
    SignUpForm, activate_user, LoginForm,
    MyPasswordResetForm, MySetPasswordForm,
    UserUpdateForm, UserUpgradeForm, ReviewPostForm
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.http import  HttpResponseRedirect, JsonResponse
from django.shortcuts import resolve_url, get_object_or_404, render, redirect
from .models import User
from nagoyameshi.models import Favorite, Restaurant, Review, Reservations, StripeCustomer
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()


class SignupView(CreateView):
    form_class = SignUpForm
    template_name = "signup.html"
    success_url = reverse_lazy("top")


class ActivateView(TemplateView):
    template_name = "activate.html"

    def get(self, request, uid64, token, *args, **kwargs):
        result = activate_user(uid64, token)
        return super().get(request, result=result, **kwargs)


class LoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'


class LogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'top.html'


class PasswordReset(PasswordResetView):
    subject_template_name = 'subject.txt'
    email_template_name = 'message.txt'
    template_name = 'password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    template_name = 'password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    form_class = MySetPasswordForm
    success_url = reverse_lazy('password_reset_complete')
    template_name = 'password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    # ログインユーザーまたはスーパーユーザーの閲覧許可
    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class MypageView(OnlyYouMixin, DetailView):
    model = User
    template_name = 'mypage.html'


class UserUpdateView(OnlyYouMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'user_update.html'

    def get_success_url(self):
        return resolve_url('mypage', pk=self.kwargs['pk'])


# class save():
    # セーブ用のビューが必要？　→UpdateViewでPOSTされている？
    # OnlyYouMixinをloginrequiredに変更


class UserUpgradeView(OnlyYouMixin, UpdateView):
    model = User
    form_class = UserUpgradeForm
    template_name = 'user_upgrade.html'

    def get_success_url(self):
        return resolve_url('mypage', pk=self.kwargs['pk'])

    def get_initial(self):
        initial = super().get_initial()
        initial['is_premium'] = True
        return initial


class UserDeleteView(OnlyYouMixin, DeleteView):
    template_name = "user_delete.html"
    success_url = reverse_lazy("top")
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'


class FavoriteRestaurantsView(LoginRequiredMixin, ListView):
    template_name = 'favorite_restaurants.html'
    model = Favorite

    def get_queryset(self):
        # Favoriteモデルのログインユーザーのデータに関して、restaurant_idのみ抽出
        restaurant_id_list = Favorite.objects.filter(user_id=self.request.user).values_list('restaurant_id', flat=True)
        # Favoriteモデルから抽出したrestaurant_idで、Restaurantデータを抽出
        queryset = Restaurant.objects.filter(pk__in=restaurant_id_list)
        return queryset


# class ReviewPostView(LoginRequiredMixin, UpdateView):
#     model = Review
#     form_class = ReviewPostForm
#     template_name = 'review_post.html'

#     @property
#     def restaurant_id(self):
#         return self.kwargs['restaurant']

#     def get_object(self, queryset=None):
#         # restaurant_id = self.kwargs['restaurant']
#         # user_id = 
        
#         # Reviewオブジェクトを特定するためのロジック
#         # ここでは、restaurantとuserに基づいてReviewオブジェクトを取得する
#         favorite, created = Review.objects.get_or_create(
#             user_id=self.request.user.id,
#             restaurants_id=self.restaurant_id
#         )
#         return HttpResponseRedirect(self.get_success_url())
#         # return favorite
    
#     def get_success_url(self):
#         return resolve_url('restaurant_detail', pk=self.restaurant_id)
class ReviewPostView(LoginRequiredMixin, FormView):
    # レビュー投稿用のビュー
    model = Review
    form_class = ReviewPostForm
    template_name = 'review_post.html'

    def get_initial(self):
        """初期データをフォームに設定する"""
        initial = super().get_initial()
        # 既存のレビューがある場合、そのデータを初期値に設定
        review = self.get_review()
        if review:
            initial['content'] = review.content
            initial['score'] = review.score
        return initial

    def get_review(self):
        """ユーザーと店舗に関連する既存のレビューを取得"""
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs['pk'])
        review = Review.objects.filter(user_id=self.request.user, restaurants_id=restaurant).first()
        return review

    def form_valid(self, form):
        """フォームが有効な場合、レビューを保存"""
        review = self.get_review()
        if review:
            # 既存のレビューを更新
            form.instance = review
        else:
            # 新しいレビューを作成
            form.instance.user_id = self.request.user
            form.instance.restaurants_id = get_object_or_404(Restaurant, pk=self.kwargs['pk'])
        # return super().form_valid(form)

        # フォームを保存
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return resolve_url('restaurant_detail', pk=self.kwargs['pk'])

class PostedListView(LoginRequiredMixin, ListView):
    # ユーザーが投稿したレビュー一覧
    template_name = 'posted_list.html'
    model = Review

    def get_queryset(self):
        # context['store_name'] = { 店舗名: [さいぜ、おこほん] }
        # return context['store_name']
        queryset = Review.objects.filter(user_id=self.request.user)
        # for i in queryset.value():
        #     print(i)
        return queryset

    # 店舗名取得案
    # Viewのdef get()で完全オリジナルで作成
    # ※モデルの処理も自作　　　　　↓辞書化(インデックスよりキーのほうが取得しやすいため)
    # 二次元リストを作成[[content→レビュー内容, name→店舗名], [レビュー内容, 店舗名], [レビュー内容, 店舗名]]


class DeleteView(TemplateView):
    template_name = 'delete_review.html'

    def post(self, request, *args, **kwargs):
        review_id = self.kwargs['pk']
        review = get_object_or_404(Review, user_id=self.request.user, id=review_id)
        review.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return resolve_url('posted_list', pk=self.request.user.id)


class ReservedListView(LoginRequiredMixin, ListView):
    template_name = 'reserved_list.html'
    model = Reservations

    def get_queryset(self):
        queryset = Reservations.objects.filter(user_id=self.request.user)
        return queryset


class CancelReservationView(TemplateView):
    template_name = 'cancel_reservation.html'

    def post(self, request, *args, **kwargs):
        reservation_id = self.kwargs['pk']
        reservation = get_object_or_404(Reservations, user_id=self.request.user, id=reservation_id)
        reservation.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return resolve_url('reserved_list', pk=self.request.user.id)


# 設定用の処理
class StripeConfigView(View):
    def get(self, request, *args, **kwargs):
        stripe_config = {'publicKey': settings.STRIPE_PUBLIC_KEY}
        return JsonResponse(stripe_config, safe=False)


# 支払い画面に遷移させるための処理
class CreateCheckoutSessionView(View):
    def get(self, request, *args, **kwargs):
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancel/',
                payment_method_types=['card'],
                mode='subscription',
                line_items=[
                    {
                        'price': settings.STRIPE_PRICE_ID,
                        'quantity': 1,
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


# 支払いに成功した後の画面
class SuccessView(TemplateView):
    template_name = 'success.html'


# 支払いに失敗した後の画面
class CancelView(TemplateView):
    template_name = 'cancel.html'


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body.decode('utf-8')
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Webhookシークレットキー

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return JsonResponse({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({'error': 'Invalid signature'}, status=400)

        # checkout.session.completed イベントをリッスン
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            customer_id = session.get('customer')
            subscription_id = session.get('subscription')

            # ユーザーに関連付けてStripeCustomerを作成・更新
            try:
                user = User.objects.get(id=session['client_reference_id'])
                stripe_customer, created = StripeCustomer.objects.get_or_create(user_id=user)
                stripe_customer.stripe_customer_id = customer_id
                stripe_customer.stripe_subscription_id = subscription_id
                stripe_customer.save()

                return JsonResponse({'status': 'success'}, status=200)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

        return JsonResponse({'status': 'success'}, status=200)


# クレジットカード編集
class UpdateCardView(View):
    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            stripe_customer = StripeCustomer.objects.get(user_id=request.user)
            billing_portal_session = stripe.billing_portal.Session.create(
                customer=stripe_customer.stripe_customer_id,
                return_url='http://localhost:8000/mypage/'  # カード情報編集後のリダイレクトURL
            )
            return HttpResponseRedirect(billing_portal_session.url)
            # return JsonResponse({'url': billing_portal_session.url})
        except StripeCustomer.DoesNotExist:
            messages.error(request, 'Stripe customer record not found.')
            return render(request, 'update_card.html', {'message': 'Stripe customer record not found.'})
            # return JsonResponse({'error': 'Stripe customer record not found'}, status=404)
        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'update_card.html', {'message': f'Error: {str(e)}'})
            # return JsonResponse({'error': str(e)}, status=400)


# サブスクリプション解除
@method_decorator(csrf_exempt, name='dispatch')
class CancelSubscriptionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            # ユーザーのStripeカスタマーIDを取得
            stripe_customer = StripeCustomer.objects.get(user_id=request.user)
        except StripeCustomer.DoesNotExist:
            # ユーザーに対応するStripeCustomerが存在しない場合
            # return JsonResponse({'error': 'Stripe customer record not found'}, status=404)
            messages.error(request, 'Stripe customer record not found.')
            return render(request, 'cancel_subscription_result.html', {'message': 'Stripe customer record not found.'})

        customer_id = stripe_customer.stripe_customer_id
        subscription_id = stripe_customer.stripe_subscription_id

        if not subscription_id:
            # return JsonResponse({'error': 'No active subscription found'}, status=404)
            messages.error(request, 'No active subscription found.')
            return render(request, 'cancel_subscription_result.html', {'message': 'No active subscription found.'})

        try:
            # サブスクリプションをキャンセル
            stripe.Subscription.delete(subscription_id)

            # サブスクリプションIDを削除（モデルで更新）
            subscription = get_object_or_404(StripeCustomer, user_id=self.request.user, stripe_customer_id=customer_id)
            subscription.delete()

            # return JsonResponse({'message': 'Subscription canceled successfully'}, status=200)
            messages.success(request, 'Subscription canceled successfully.')
            return render(request, 'cancel_subscription_result.html', {'message': 'Subscription canceled successfully.'})

        except stripe.error.StripeError as e:
            # return JsonResponse({'error': str(e)}, status=400)
            messages.error(request, str(e))
            return render(request, 'cancel_subscription_result.html', {'message': f'Error: {str(e)}'})
