# from django.contrib import admin
# from user_app.models import UserDB
# from django.contrib.auth.admin import UserAdmin
#
# # Register your models here.
# # admin.site.register(UserDB)
#
#
# class UserAdmin(UserAdmin):
#     list_display = ('email', 'date_joined', 'last_login', 'is_admin', 'is_staff')
#     search_fields = ('email',)
#     readonly_fields = ('date_joined', 'last_login')
#
#     filter_horizontal = ()
#     list_filter = ()
#     fieldsets = ()
#
#
# admin.site.register(UserDB, UserAdmin)

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# from .forms import UserAdminCreationForm, UserAdminChangeForm

User = get_user_model()

# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # form = UserAdminChangeForm
    # add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'date_joined', 'last_login', 'is_admin', 'is_staff')
    list_filter = ()
    fieldsets = (

    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

    search_fields = ['email']
    ordering = ['email']
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
