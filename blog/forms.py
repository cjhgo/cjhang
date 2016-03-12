from django.contrib.auth.models import User
from django import forms
from django.contrib.admin import widgets

from blog.models import BlogMeta,Blog,Comment

class BlogForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(BlogForm,self).__init__(*args,**kwargs)
        # self.fields['publish_date'].widget = widgets.AdminSplitDateTime()
        # self.fields['publish_date'].input_formats = ['%Y-%m-%d %H:%M:%S',]
    class Meta:
        model = Blog
        exclude = ['slug','summary','is_published']
class CommentForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(CommentForm,self).__init__(*args,**kwargs)
        reply_to_list = [temp.pk for temp in Comment.objects.filter(comment_for=self.instance.pk)]
        self.fields['reply_to'].queryset = Comment.default.filter(pk__in=reply_to_list)
    class Meta:
        model = Comment
        fields = ['text','user_name','user_url','email_id','reply_to']

class BlogMetaForm(forms.ModelForm):
    class Meta:
        model = BlogMeta
        exclude = []