from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from brownie.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("name",)}),) + tuple(
        auth_admin.UserAdmin.fieldsets
    )
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]


# DATABASE_URL=postgres://postgres:1234@localhost:5433/brownie;CELERY_BROKER_URL=localhost:6379;