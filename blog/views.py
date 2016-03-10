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

from blog.models import Blog, Comment, BlogRoll
from blog import forms as myforms
# from blogango.conf.settings import AKISMET_COMMENT, AKISMET_API_KEY
# from blogango.akismet import Akismet, AkismetError

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'blogs'

    def get(self, request, *args, **kwargs):
        blog = Blog.objects.get_blog()
        if not blog:
            return HttpResponseRedirect(reverse('blog:blog_install'))
        self.kwargs['blog'] = blog
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
                entry = Blog.objects.get(created_on__year=self.kwargs['year'],
                                          created_on__month=self.kwargs['month'],
                                          created_on__day=self.kwargs['day'],
                                          slug=self.kwargs['slug'])            

        if not entry.is_published:
            if self.request.user.is_staff and 'preview' in self.request.GET:
                pass
            else:
                raise Http404
        return entry
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
        comment_f = myforms.CommentForm()
        comments = Comment.objects.filter(comment_for=blog, is_spam=False)
        payload = {'comments': comments,'comment_form': comment_f}
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
            comment.user_name = post_data['user_name']
            comment.reply_to = post_data['reply_to']
            comment.email_id = post_data['email_id']
            comment.comment_for = self.object
            comment.user_ip = request.META['REMOTE_ADDR']
            comment.user_agent = request.META['HTTP_USER_AGENT']
            comment.is_public = getattr(settings, 'AUTO_APPROVE_COMMENTS',
                                        True)
            comment.save()
            return HttpResponseRedirect('#comment-%s' % comment.pk)
        context.update({'comment_form': comment_f})
        return self.render_to_response(context)
detail = DetailView.as_view()

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
        return super(AdminCreateUpdateCommon,self).form_valid(form)

    def get_context_data(self,*args,**kwargs):
        context = super(AdminCreateUpdateCommon,self).get_context_data(*args,**kwargs)
        tags_josn = json.dumps([each.name for each in Tag.objects.all()])
        context['tags_josn'] = tags_josn
        return context
    def get_success_ful(self):
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

class AdminBlogView(StaffMemReqMixin,AdminCreateUpdateCommon,generic.edit.CreateView):
    # def get_initial(self):
        # initial = super(AdminEntryView, self).get_initial()
        # initials = {'created_by': self.request.user.id,
        #             'publish_date': datetime.now()}
        # initial.update(initials)
        # return initial
    def get_initial(self):
        initial = super(AdminBlogView,self).get_initial()
        initials = {'created_by':self.request.user.id,
                    'publish_date':datetime.now()}
        initial.update(initials)
        return initial

admin_blogs_manage = AdminDashboardView.as_view()
admin_blog_new = AdminBlogView.as_view()
admin_blog_edit = AdminDashboardView.as_view()
admin_comments_manage = AdminDashboardView.as_view()
admin_meta_edit = AdminDashboardView.as_view()


#Helper method
def _is_blog_installed():
    return Blog.objects.get_blog()