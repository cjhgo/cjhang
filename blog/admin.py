from django.contrib import admin
from .models import BlogMeta,Blog,Comment,BlogRoll

# Register your models here.

admin.site.register(BlogMeta)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(BlogRoll)