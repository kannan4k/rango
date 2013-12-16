from django.contrib import admin
from rango.models import Category, Page, UserProfile 
from django.contrib.auth.models import User

admin.site.register(Category)
admin.site.register(Page)
admin.site.register(UserProfile)