from django import forms
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import HttpResponseRedirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse

from users.models import User


class UserCreationForm(forms.ModelForm):
    """ This form provides two password fields to ensure that the administrator provides matching password
    before updating the password for that target user. """

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = '__all__'

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match')
        return password2

    def save(self, commit=True) -> AbstractBaseUser:
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        return user


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """ Let's use this lil slugger here as our base user class. """

    ordering = ('email',)
    change_form_template = 'admin/add_custom_buttons.html'

    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    list_display = ('username', 'email', 'first_name', 'last_name')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')
        }),
    )
    fieldsets = [
        ('General Account Information', {
            'fields': ('username', 'email', 'password'),
        }),
        ('Personal Information', {
            'fields': (('first_name', 'last_name'))
        }),
        ('Administrative Details', {
            'fields': ('date_joined', 'last_login', 'email_verified')
        }),
    ]

    def response_change(self, request: HttpRequest, obj: User) -> HttpResponse:
        """ If custom admin button is clicked, it will be caught by this and magic will happen. """

        if '_autologin' in request.POST:
            if obj.autologin_url:
                return HttpResponseRedirect(obj.autologin_url)
            else:
                messages.error(request, 'Please ask backend to set the FRONTEND_LOGIN_URL variable.')
                return HttpResponseRedirect('/admin')
        return super().response_change(request, obj)
