from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User

from django.db import models
from datetime import datetime, timedelta
from django.template.defaultfilters import slugify
from taggit.managers import TaggableManager
from markupfield.fields import MarkupField
from markupfield.markup import DEFAULT_MARKUP_TYPES

from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
# Create your models here.

class BlogMetaManager(models.Manager):
    def get_blogmeta(self):
        blogs = self.all()
        if blogs:
            return blogs[0]
        return None
class BlogMeta(models.Model):
    title = models.CharField(max_length=100)
    tag_line = models.CharField(max_length=100)
    entries_per_page = models.IntegerField(default=10)
    recents = models.IntegerField(default=5)
    recent_comments = models.IntegerField(default=5)

    objects = BlogMetaManager()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):

        """There should not be more than one Blog object"""
        if Blog.objects.count() == 1 and not self.id:
            raise Exception("Only one blogmeta object allowed.")
        # Call the "real" save() method.
        super(BlogMeta, self).save(*args, **kwargs)
class BlogManager(models.Manager):
    def get_queryset(self):
        return super(BlogManager, self).get_queryset().filter(
            is_published=True,
            publish_date__lte=datetime.now())
    def get_blog(self):
        blogs = self.all()
        if blogs:
            return blogs[0]
        return None
class Blog(models.Model):
    """
    
    """
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    text = MarkupField(default_markup_type=getattr(settings,
                                                   'DEFAULT_MARKUP_TYPE',
                                                   'plain'),
                       markup_choices=getattr(settings, "MARKUP_RENDERERS",
                                              DEFAULT_MARKUP_TYPES))
    summary = models.TextField()
    created_on = models.DateTimeField(default=datetime.max, editable=False)
    created_by = models.ForeignKey(User, unique=False)
    # is_page = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    publish_date = models.DateTimeField(null=True)
    comments_allowed = models.BooleanField(default=True)
    is_rte = models.BooleanField(default=False)

    meta_keywords = models.TextField(blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    tags = TaggableManager()

    default = models.Manager()
    objects = BlogManager()

    def __unicode__(self):
        return self.title
    def __str__(self):
        return self.title

    def save(self,*args,**kwargs):
        if self.title is None or self.title == '':
            self.title = _infer_title_or_slug(self.text.raw)
        
        if self.slug is None or self.slug == '':
            self.slug = slugify(self.title)
        i = 1
        while True:
            created_slug = self.create_slug(self.slug,i)
            slug_count = Blog.objects.filter(slug__exact=created_slug).exclude(pk=self.pk)
            if not slug_count:
                break
            i += 1        
        self.slug = created_slug
        if not self.summary:
            self.summary = _generate_summary(self.text.raw)
        if not self.meta_keywords:
            self.meta_keywords = self.summary
        if not self.meta_description:
            self.meta_description = self.summary
        if self.is_published:
            if self.created_on.year == 9999:
                self.created_on = self.publish_date
        super(Blog,self).save(*args,**kwargs)
    def create_slug(self,initial_slug,i=1):
        if not i == 1:
            initial_slug += '-%s'%(i,)
        return initial_slug
    def get_absolute_url(self):
        return reverse('blog:blog_detail',
                        kwargs={'year':self.created_on.strftime('%Y'),
                                'month':self.created_on.strftime('%m'),
                                'day':self.created_on.strftime('%d'),
                                'slug':self.slug,
                                })
    def get_edit_url(self):        
        return reverse('blog:blog_admin_blog_edit',args=[self.id])
    def get_num_comments(self):
        cmnt_count = Comment.objects.filter(comment_for=self,is_spam=False).count()
        return cmnt_count
    def has_recent_comments(self):
        yesterady = datetime.now()-timedelta(days=1)
        return Comment.objects.filter(
            comment_for=self,is_spam=False,created_on__gt=yesterady
            ).exists()
    def get_recent_comments(self):
        yesterady = datetime.now()-timedelta(days=1)
        cmnts = Comment.objects.filter(
            comment_for=self, is_spam=False, created_on__gt=yesterday
        ).order_by('-created_on')
        return cmnts
class CommentManager(models.Manager):
    def get_queryset(self):
        return super(CommentManager, self).get_queryset().filter(is_public=True)
class Comment(models.Model):
    text = models.TextField()
    comment_for = models.ForeignKey(Blog)
    # reply_to = models.ForeignKey("self",related_name=)
    reply_to = models.ForeignKey("self",null=True,blank=True)
    # reply_to = models.ForeignKey("self",null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    user_name = models.CharField(max_length=100)
    user_url = models.URLField()
    created_by = models.ForeignKey(User, unique=False, blank=True, null=True)
    email_id = models.EmailField()
    is_spam = models.BooleanField(default=False)
    is_public = models.NullBooleanField(null=True, blank=True)
    user_ip = models.GenericIPAddressField(null=True)
    user_agent = models.CharField(max_length=200, default='')

    # default = models.Manager()
    objects = CommentManager()

    class Meta:
        ordering = ['created_on']

    def __unicode__(self):
        return self.text
    def save(self, *args, **kwargs):
        if self.is_spam:
            self.is_public = False
        super(Comment, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:comment_detail', 
                        kwargs={'year':self.comment_for.created_on.strftime('%Y'),
                                'month':self.comment_for.created_on.strftime('%m'),
                                'day':self.comment_for.created_on.strftime('%d'),
                                'slug':self.comment_for.slug,
                                'cmnt_id':self.id,
                                })
class BlogRoll(models.Model):
    url = models.URLField(unique=True)
    text = models.CharField(max_length=100)
    is_published = models.BooleanField(default=True)

    def __unicode__(self):
        return self.text

    def get_absolute_url(self):
        return self.url        
def _generate_summary(text):
    return ' '.join(text.split()[:50])        