from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from .models import User
from nagoyameshi.models import Review
from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

User = get_user_model()

# 認証用メールのタイトルと本文のテンプレート
subject = "登録確認"
message_template = """
ご登録ありがとうございます。
以下のURLをクリックして登録完了してください。

"""

# URL定義
def get_activate_url(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return settings.FRONTED_URL + "activate/{}/{}/".format(uid, token) 

# サインアップフォーム
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'last_name', 'first_name')

    # メール認証するまでDBに格納しない
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        # メール認証するまでログイン不可
        user.is_active = False

        if commit:
            user.save()
            activate_url = get_activate_url(user)
            message = message_template + activate_url
            user.email_user(subject, message)
        return user

# ユーザーの有効化
def activate_user(uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        return False

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return True

    return False

# ログインフォーム
class LoginForm(AuthenticationForm):
    class Meta:
        model = User

# パスワード忘れ用フォーム
class MyPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

# パスワード再設定フォーム
class MySetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

# ユーザー情報更新フォーム
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('last_name', 'first_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

# 有料会員登録フォーム
class UserUpgradeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('birthday', 'gender', 'is_premium')
        widgets = {'is_premium':forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

# レビュー投稿用フォーム
class ReviewPostForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('content', 'score', 'number_of_people', 'purpose')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
