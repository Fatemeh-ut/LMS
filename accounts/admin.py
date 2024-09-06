from django.contrib import admin
from .models import Users
# Register your models here.

class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password', 'email', 'first_name', 'last_name', 'role', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'role')


admin.site.register(Users, UsersAdmin)