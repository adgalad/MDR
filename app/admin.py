from django import forms
from django.contrib import admin
from django.contrib.auth import password_validation
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.utils.translation import gettext, gettext_lazy as _
from .models import User
import app.models as models
# Register your models here.

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=("Enter the same password as before, for verification."),
    )


    class Meta:
        model = User
        fields = ('username', 'is_staff', 'is_active', )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(BaseUserChangeForm):
    """
    Override as needed
    """

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username',  'is_superuser', 'is_staff', 'is_active', 'created_at', 'updated_at', 'last_login')
    # list_filter = ('email',)

    readonly_fields=('created_at', 'updated_at',)
    fieldsets = (
        (None                , {'fields': ('username','email', 'wallet_address', 'password')}),
        (('Permissions')    , {'fields': ('is_active', 'is_staff', 'is_superuser', 'can_sign', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
        ),
    )
    search_fields = ('username',)
    ordering = ('username',)
    # filter_horizontal = ()


admin.site.register(User, UserAdmin)



class Transaction(admin.ModelAdmin):
    pass
class Raffle(admin.ModelAdmin):
    pass
class AddressGenerated(admin.ModelAdmin):
    pass

admin.site.register(models.Transaction, Transaction)
admin.site.register(models.Raffle, Raffle)
admin.site.register(models.AddressGenerated, AddressGenerated)
