from django.contrib import admin
from .models import User, ContentMail

class UserAdmin(admin.ModelAdmin):
    list_display = ('useId', 'count')

class ContentAdmin(admin.ModelAdmin):
    list_display = ('mailId', 'name', 'content')

admin.site.register(User, UserAdmin)
admin.site.register(ContentMail, ContentAdmin)