from django.conf.urls import patterns, url
from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^$',views.index,name='index'),
    url(r'^install/$', views.install_blog, name='blog_install'),
    url(r'^(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>[-\w]+)/$',
        views.detail,name='blog_detail'),
    # url(r'^(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>[-\w]+)/'+\
    #     r'#comment-(?P<cmnt_id>[-\w]+)$',
    #     views.detail,name='comment_detail'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$',views.index,
        name='blog_tag_details'),    
    url(r'^archive/(?P<year>\d+)/(?P<month>\w+)/$', views.index, name='blog_archives'),
    

    #admin url 
    #admin
    url(r'^admin/$',views.admin_dashboard,name='blog_admin_dashboard'),
    #manage blogs
    url(r'^admin/blog/manage/$',views.admin_blogs_manage,name='blog_admin_blogs_manage'),
    #add new blog
    url(r'^admin/blog/new/$',views.admin_blog_new,name='blog_admin_blog_new'),
    #edit blog
    url(r'^admin/blog/edit/(?P<pk>\d+)/$',views.admin_blog_edit,name='blog_admin_blog_edit'),
    #manage comments
    url(r'^admin/comment/manage/$',views.admin_comments_manage,name='blog_admin_comments_manage'),
    #edit blog meta
    url(r'^admin/meta/edit/$',views.admin_meta_edit,name='blog_admin_meta_edit'),
]
