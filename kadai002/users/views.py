from django.views.generic import (
    TemplateView, CreateView, DetailView, UpdateView, FormView,
    DeleteView, ListView, View
)
from django.urls import reverse_lazy, reverse
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
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()


class SignupView(CreateView):
    form_class = SignUpForm
    template_name = "signup.html"
    success_url = reverse_lazy('login_url')  # メール確認のページへリダイレクト

    def form_valid(self, form):
        # ユーザーを作成
        user = form.save()
        self.object = user  # 明示的にself.objectを設定

        # メール認証のリンク作成
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = f"{self.request.scheme}://{get_current_site(self.request).domain}/accounts/activate/{uid}/{token}/"

        # メールを送信
        try:
            message_template = """
                NAGOYAMESHIのご登録ありがとうございます。
                以下のURLをクリックして登録完了してください。

                """
            message = message_template + activation_link
            send_mail('本登録をお願いします', message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False,)
        except Exception as e:
            raise ValidationError(f"メール送信エラー: {e}")
        return redirect(self.get_success_url())  # 成功したらリダイレクト


class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return redirect(reverse_lazy('login'))  # 成功したらログインページにリダイレクト
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # トークンが無効な場合
        return redirect('signup')


class LoginURLView(TemplateView):
    template_name = 'login_url.html'


class LoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('top')


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


class UserUpgradeView(OnlyYouMixin, UpdateView):
    model = User
    form_class = UserUpgradeForm
    template_name = 'user_upgrade.html'

    def form_valid(self, form):
        form.instance.is_premium = True  # 明示的に is_premium を True に設定
        self.object = form.save()  # フォームデータを保存
        return super().form_valid(form)

    def get_success_url(self):
        return resolve_url('user_upgrade_success', pk=self.kwargs['pk'])


class UpdaUserUpgradeSuccess(LoginRequiredMixin, TemplateView):
    template_name = "user_upgrade_success.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ユーザーオブジェクトを取得
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        context['user'] = user
        return context


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
            initial['purpose'] = review.purpose
            initial['number_of_people'] = review.number_of_people
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
            form.instance.content = form.cleaned_data.get('content')
            form.instance.score = form.cleaned_data.get('score')
            form.instance.purpose = form.cleaned_data.get('purpose')
            form.instance.number_of_people = form.cleaned_data.get('number_of_people')

        else:
            # 新しいレビューを作成
            form.instance.user_id = self.request.user
            form.instance.restaurants_id = get_object_or_404(Restaurant, pk=self.kwargs['pk'])

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
        queryset = Review.objects.filter(user_id=self.request.user)

        return queryset


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
        domain_url = 'https://suzuki-nagoyameshi-3cf72cebd974.herokuapp.com/'
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
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

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
@method_decorator(csrf_exempt, name='dispatch')
class UpdateCardView(View):
    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            logger.debug(f"User ID: {request.user.id}")
            stripe_customer = StripeCustomer.objects.get(user_id=request.user)
            
            # 動的にユーザーIDを含むURLを生成
            return_url = request.build_absolute_uri(
                reverse('mypage', kwargs={'pk': request.user.id})
            )
            
            billing_portal_session = stripe.billing_portal.Session.create(
                customer=stripe_customer.stripe_customer_id,
                return_url=return_url  # 動的に生成したURLを使用
            )
            return HttpResponseRedirect(billing_portal_session.url)
        except StripeCustomer.DoesNotExist:
            logger.error(f"StripeCustomer.DoesNotExist for user: {request.user.id}")
            messages.error(request, 'Stripe customer record not found.')
            return render(request, 'update_card.html', {'message': 'Stripe customer record not found.'})
        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            messages.error(request, str(e))
            return render(request, 'update_card.html', {'message': f'Error: {str(e)}'})



# サブスクリプション解除
@method_decorator(csrf_exempt, name='dispatch')
class CancelSubscriptionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            stripe_customer = StripeCustomer.objects.get(user_id=request.user)
        except StripeCustomer.DoesNotExist:
            messages.error(request, 'Stripe customer record not found.')
            return redirect('cancel_subscription_result')

        subscription_id = stripe_customer.stripe_subscription_id
        if not subscription_id:
            messages.error(request, 'No active subscription found.')
            return redirect('cancel_subscription_result')

        try:
            # サブスクリプションをキャンセル
            stripe.Subscription.delete(subscription_id)

            # StripeCustomer レコードを削除
            stripe_customer.delete()

            # ユーザーの無料会員化
            user = request.user
            user.is_premium = False  # フィールド名に合わせて変更
            user.save()

            messages.success(request, '有料会員を解除しました。引き続き無料会員としてNAGOYAMESHIをご利用ください。')
        except stripe.error.StripeError as e:
            messages.error(request, f'Subscription cancelation failed: {str(e)}')

        return redirect('cancel_subscription_result')


class CancelSubscriptionResultView(TemplateView):
    template_name = 'cancel_subscription_result.html'
