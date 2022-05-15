from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class RegisterForm(forms.Form):
    username = forms.CharField(
        label="Tên Đăng Nhập",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Mật Khẩu",
        max_length=50,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}) # `PasswordInput` = <form type="password">
    )
    confirm_password = forms.CharField(
        label="Nhập Lại Mật Khẩu",
        max_length=50,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}) # `PasswordInput` = <form type="password">
    )
    email = forms.CharField(
        label="Địa Chỉ Email",
        max_length=50,
        widget=forms.EmailInput(attrs={'class': 'form-control'}) # `EmailInput` = <form type="email"> Format email
    )
    first_name = forms.CharField(
        label="Tên",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="Họ",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    # Cũng cần phải tạo cái clean_<field>
    def clean_username(self):
        # Validate username không trùng nahu
        try:
            username = self.cleaned_data['username']
            User.objects.get(username = username)
            # Văng lỗi trùng
            raise ValidationError(f"{username} đã tồn tại. Vui lòng chọn tên khác.")
        except User.DoesNotExist:
            return username


    def clean_email(self):
        # Validate email không trùng nahu
        try:
            email = self.cleaned_data['email']
            User.objects.get(email = email)
            # Văng lỗi trùng
            raise ValidationError(f"{email} đã tồn tại. Vui lòng chọn eamil khác.")
        except User.DoesNotExist:
            return email

    # Validate cho confirm_password. Để có password
    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password == confirm_password:
            # OK
            return confirm_password
        raise ValidationError(f"Mật khẩu không. Vui lòng kiểm tra lại")

    def save_user(self):
        # .create -> lưu trữ dạng raw data password không bị encryt
        return User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )