from django.shortcuts import render
from django.views import generic
from datetime import datetime

from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.template import RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.encoding import smart_str
from django.db.models import Q
from django.views.decorators.http import require_POST
import json
from django.views.generic.dates import MonthArchiveView
from django.views import generic
from taggit.models import Tag

from blog.models import BlogMeta,Blog, Comment, BlogRoll
from blog import forms as myforms
# from blogango.conf.settings import AKISMET_COMMENT, AKISMET_API_KEY
# from blogango.akismet import Akismet, AkismetError

# Create your views here.
class ResumeView(generic.TemplateView):
    template_name = "blog/resume.html"
    pass
resume = ResumeView.as_view()
class IndexView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'blogs'

    def get_paginate_by(self, queryset):
        paginate_by = self.kwargs['blogmeta'].blogs_per_page
        return  paginate_by
    def get(self, request, *args, **kwargs):
        blogmeta = BlogMeta.objects.get_blogmeta()
        if not blogmeta:
            return HttpResponseRedirect(reverse('blog:blog_install'))
        self.kwargs['blogmeta'] = blogmeta
        return super(IndexView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        blogs = Blog.objects.all()
        return blogs

index = IndexView.as_view()    
class DetailView(generic.DetailView):
    template_name = 'blog/detail.html'
    context_object_name = 'blog'
    def get_object(self,queryset=None):
        if 'year' in self.kwargs:
            blog = Blog.default.get(created_on__year=self.kwargs['year'],
                                    created_on__month=self.kwargs['month'],
                                    created_on__day=self.kwargs['day'],
                                    slug=self.kwargs['slug'])
        else:
            blog = Blog.default.get(slug=self.kwargs['slug'])
        if not blog.is_published:
            if 'preview' in self.request.GET:
                pass
            else:
                raise Http404
        return blog
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        init_data = {}
        if self.request.user.is_authenticated():
            init_data['name'] = self.request.user.get_full_name() or self.request.user.username
            init_data['email'] = self.request.user.email
        else:
            init_data['name'] = self.request.session.get("name", "")
            init_data['email'] = self.request.session.get("email", "")
            init_data['url'] = self.request.session.get("url", "")
        blog = context['blog']
        reply_to_list = [temp.pk for temp in Comment.objects.filter(comment_for=blog.pk)]
        comment_f = myforms.CommentForm()
        comments = Comment.objects.filter(comment_for=blog, is_spam=False)
        payload = {'comments': comments,'comment_form': comment_f}
        comment_f.fields['reply_to'].queryset = Comment.default.filter(pk__in=reply_to_list)
        context.update(payload)
        return context
    def post(self,*args,**kwargs):
        self.object = self.get_object()
        request = self.request
        context = self.get_context_data(object=self.object)
        comment_f = myforms.CommentForm(self.request.POST)
        if comment_f.is_valid():
            # (1,2,3).append(5)
            comment = Comment()
            post_data = comment_f.cleaned_data
            comment.text = post_data['text']
            comment.reply_to = post_data['reply_to']
            comment.email_id = post_data['email_id']
            comment.comment_for = self.object
            comment.user_name = post_data['user_name']
            comment.user_url = post_data['user_url']
            comment.user_ip = request.META['REMOTE_ADDR']
            comment.user_agent = request.META['HTTP_USER_AGENT']
            comment.is_public = getattr(settings, 'AUTO_APPROVE_COMMENTS',
                                        True)
            comment.save()
            return HttpResponseRedirect('#comment-%s' % comment.pk)
        context.update({'comment_form': comment_f})
        return self.render_to_response(context)
detail = DetailView.as_view()

class BlogArchiveView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'blogs'

    def get_paginate_by(self, queryset):
        paginate_by = self.kwargs['blogmeta'].blogs_per_page
        return  paginate_by
    def get(self, request, *args, **kwargs):
        blogmeta = BlogMeta.objects.get_blogmeta()
        if not blogmeta:
            return HttpResponseRedirect(reverse('blog:blog_install'))
        self.kwargs['blogmeta'] = blogmeta
        return super(BlogArchiveView, self).get(request, *args, **kwargs)
    def get_context_data(self, *args,**kwargs):
        context = super(BlogArchiveView,self).get_context_data(*args,**kwargs)
        context['archive_tag'] = 'archive_tag'
        return  context
    def get_queryset(self):
        blogs = Blog.objects.all()
        if self.kwargs["year"]:
            blogs = blogs.filter(publish_date__year=self.kwargs['year'])
            if self.kwargs["month"]:
                blogs = blogs.filter(publish_date__month=self.kwargs['month'])
        return blogs
archive = BlogArchiveView.as_view()
class BlogTagsView(generic.ListView):
    context_object_name = "tags"
    template_name = "blog/tags.html"
    def get_queryset(self):
        tags = Tag.objects.all()
        return tags
tags = BlogTagsView.as_view()
class BlogTagDetailView(generic.ListView):
    template_name = 'blog/tag_details.html'
    context_object_name = 'blogs'

    def get_paginate_by(self, queryset):
        paginate_by = self.kwargs['blogmeta'].blogs_per_page
        return  paginate_by
    def get(self, request, *args, **kwargs):
        blogmeta = BlogMeta.objects.get_blogmeta()
        if not blogmeta:
            return HttpResponseRedirect(reverse('blog:blog_install'))
        self.kwargs['blogmeta'] = blogmeta
        return super(BlogTagDetailView, self).get(request, *args, **kwargs)
    def get_context_data(self, *args,**kwargs):
        context = super(BlogTagDetailView,self).get_context_data(*args,**kwargs)
        context["tag"] = self.kwargs["tag"]
        return  context
    def get_queryset(self):
        tag = get_object_or_404(Tag, slug= self.kwargs['tag_slug'])
        self.kwargs["tag"]=tag
        blogs = Blog.objects.filter(tags__in=[tag])
        return blogs
tagdetails = BlogTagDetailView.as_view()
class InstallBlog(generic.TemplateView):
    template_name = 'blog/install.html'

    def get(self, request, *args, **kwargs):
        if _is_blog_installed():
            return HttpResponseRedirect(reverse('blog:index'))
        return super(InstallBlog, self).get(request, *args, **kwargs)

install_blog = InstallBlog.as_view()


class StaffMemReqMixin(object):
    @method_decorator(staff_member_required)
    def dispatch(self,*args,**kwargs):
        return super(StaffMemReqMixin,self).dispatch(*args,**kwargs)
class AdminDashboardView(StaffMemReqMixin,generic.TemplateView):
    template_name = 'blog/admin/index.html'
    def get_context_data(self,*args,**kwargs):
        context = super(AdminDashboardView,self).get_context_data(*args,**kwargs)
        recent_drafts = Blog.default.filter(is_published=False).order_by('-created_on')[:5]
        recent_blogs = Blog.objects.order_by('-created_on')[:5]
        context['recent_drafts']=recent_drafts
        context['recent_blogs']=recent_blogs
        return context
admin_dashboard = AdminDashboardView.as_view()

class AdminCreateUpdateCommon(object):
    model = Blog
    form_class = myforms.BlogForm
    template_name = 'blog/admin/edit_blog.html'
    def form_valid(self,form):
        if "publish" in self.request.POST:
            # print 2222
            # print self.request.POST
            # print form.instance.is_published
            form.instance.is_published = True
            # print form.instance.is_published
        elif "save" in self.request.POST:
            # print 1111
            # print self.request.POST
            # print form.instance.is_published
            form.instance.is_published = False
            # print form.instance.is_published
        return super(AdminCreateUpdateCommon,self).form_valid(form)

    def get_context_data(self,*args,**kwargs):
        context = super(AdminCreateUpdateCommon,self).get_context_data(*args,**kwargs)
        tags_josn = json.dumps([each.name for each in Tag.objects.all()])
        context['tags_josn'] = tags_josn
        return context
    def get_success_url(self):
        blog = self.object
        if blog.is_published:
            publish_date = blog.publish_date
            return reverse('blog:blog_detail',
                            kwargs={'year':publish_date.year,
                                    'month':publish_date.month,
                                    'day':publish_date.day,
                                    'slug':blog.slug
                            })
        else:
            return reverse('blog:blog_admin_blog_edit',
                            args=[blog.id])+'?done'
class AdminBlogsMangeView(StaffMemReqMixin,generic.ListView):
    template_name = 'blog/admin/manage_blogs.html'
    model = Blog
    context_object_name = 'blogs'
    def get_queryset(self):
        blogs = Blog.default.all()
        return  blogs
    def get_context_data(self, **kwargs):
        context = super(AdminBlogsMangeView,self).get_context_data(**kwargs)
        return  context
admin_blogs_manage = AdminBlogsMangeView.as_view()

class AdminBlogView(StaffMemReqMixin,AdminCreateUpdateCommon,generic.edit.CreateView):
    def get_initial(self):
        initial = super(AdminBlogView,self).get_initial()
        initials = {'created_by':self.request.user.id,
                    'publish_date':datetime.now()}
        initial.update(initials)
        return initial

admin_blog_new = AdminBlogView.as_view()
class AdminBlogEditView(StaffMemReqMixin,AdminCreateUpdateCommon,generic.UpdateView):
    pass
admin_blog_edit = AdminBlogEditView.as_view()

class AdminCommentsManageView(StaffMemReqMixin,generic.ListView):
    model = Comment
    template_name = "blog/admin/manage_comments.html"
    context_object_name = "comments"
    def get_queryset(self):
        blog = None
        if "blog_id" in self.kwargs:
            blog = get_object_or_404(Blog,pk=self.kwargs["blog_id"])
        if "blocked" in self.request.GET:
            comments = \
                Comment.default.filter(Q(is_spam=True) | Q(is_public=False)).order_by('-created_on')
        else:
            comments = Comment.objects.order_by('-created_on')
        if blog:
            comments = comments.filter(comment_for=blog)
        return comments
    def get_context_data(self,*args,**kwargs):
        context = super(AdminCommentsManageView,self).get_context_data(*args,**kwargs)
        blog = None
        if "blog_id" in self.kwargs:
            blog = get_object_or_404(Blog,pk=self.kwargs["blog_id"])
        context["blog"] = blog
        return  context
    def get_paginate_by(self, queryset):
        paginate_by = getattr(settings,"COMMENT_PER_PAGE",20)
        return  paginate_by

admin_comments_manage = AdminCommentsManageView.as_view()
class AdminMetaEditView(StaffMemReqMixin,generic.UpdateView):
    model = BlogMeta
    form_class = myforms.BlogMetaForm
    template_name = "blog/admin/edit_blogmeta.html"
    success_url = "?done"

    def get_object(self, *args,**kwargs):
        return BlogMeta.objects.get_blogmeta()
admin_meta_edit = AdminMetaEditView.as_view()

@staff_member_required
@require_POST
def admin_comment_approve(request):
    comment_id = request.POST.get("comment_id",None)
    comment = get_object_or_404(Comment,pk=comment_id)
    comment.is_spam = False
    comment.is_public = True
    comment.save()
    return HttpResponse(comment.pk)
@staff_member_required
@require_POST
def admin_comment_block(request):
    comment_id = request.POST.get("comment_id",None)
    comment = get_object_or_404(Comment,pk=comment_id)
    comment.is_spam = True
    comment.is_public = False
    comment.save()
    return HttpResponse(comment.pk)
#Helper method
def _is_blog_installed():
    return BlogMeta.objects.get_blog()