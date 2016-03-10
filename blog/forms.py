from django.contrib.auth.models import User
from django import forms
from django.contrib.admin import widgets

from blog.models import Blog, BlogRoll,Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text','user_name','user_url','email_id','reply_to']
