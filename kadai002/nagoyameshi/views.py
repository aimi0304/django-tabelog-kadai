from django.shortcuts import render, get_object_or_404
from .models import Restaurant, Favorite, Reservations
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import resolve_url
from django.http import  HttpResponseRedirect
from .forms import ReservationForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin



class TopView(TemplateView):
    template_name = "top.html"


class RestaulantSearchView(ListView):
    template_name = 'nagoyameshi/restaurant_list.html'
    model = Restaurant
    pagenate_by = 10

    def get_queryset(self):
        queryset = Restaurant.objects.order_by('-id')
        keyword = self.request.GET.get('keyword')

        if keyword:
            queryset = queryset.filter(
                            Q(store_name__icontains=keyword)
            )
            messages.success(self.request, '「{}」の検索結果'.format(keyword))

        return queryset


class RestaurantDetail(DetailView):
    template_name = 'nagoyameshi/restaurant_detail.html'
    model = Restaurant

    @property
    def restaurant(self):
        return self.get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # レビュー表示
        context['reviews'] = self.object.restaurants_id.all()
        context['is_login'] = user.is_authenticated

        if user.is_authenticated:
            # ログイン状態

            # お気に入り登録の有無
            context['is_favorite'] = Favorite.objects.filter(
                user_id=self.user, restaurant_id=self.restaurant).exists()

            # プレミアムユーザーかどうか
            context['is_premium'] = self.user.is_premium

        else:
            context['is_favorite'] = False
            context['is_premium'] = False

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # お気に入りの削除または登録
        favorite, created = Favorite.objects.get_or_create(
            user_id=self.user,
            restaurant_id=self.object
        )

        if created:
            message = "お気に入りに登録しました。"
        else:
            favorite.delete()
            message = "お気に入りから削除しました。"

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return resolve_url('restaurant_detail', pk=self.kwargs['pk'])  # 詳細ページにリダイレクト


class ReservationView(LoginRequiredMixin, CreateView):
    model = Reservations
    form_class = ReservationForm
    template_name = 'nagoyameshi/reservation.html'
    success_url = reverse_lazy('reservation_completed')

    def form_valid(self, form):
        # ログイン中のユーザーをuser_idに設定
        form.instance.user_id = self.request.user
        
        # restaurant_idには適切なRestaurantインスタンスを設定（例としてURLパラメータから取得）
        # ここでは`restaurant_id`がURLパラメータにあると仮定しています
        restaurant_id = self.kwargs.get('pk')  # URLからレストランIDを取得
        form.instance.restaurant_id = get_object_or_404(Restaurant, pk=restaurant_id)

        # フォームを保存
        return super().form_valid(form)


class ReservationCompleted(LoginRequiredMixin, TemplateView):
    template_name = 'nagoyameshi/reservation_completed.html'
