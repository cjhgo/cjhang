from django.conf.urls import patterns, url
from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^$',views.index,name='index'),
    url(r'^resume/$',views.resume,name='resume'),
    #page urlconf
    url(r'^page(?P<page>[0-9]+)/$',views.index,name='blog_page'),
    url(r'^install/$', views.install_blog, name='blog_install'),
    url(r'^(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>.+)/$',
        views.detail,name='blog_detail'),
    # url(r'^(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>[-\w]+)/'+\
    #     r'#comment-(?P<cmnt_id>[-\w]+)$',
    #     views.detail,name='comment_detail'),
    url(r'^tags/$',views.tags,name="blog_tags"),
    url(r'^tags/(?P<tag_slug>[-\w]+)/$',views.tagdetails,name="blog_tag_details"),
    url(r'^tags/(?P<tag_slug>[-\w]+)/(?P<page>\d+)/$$',views.tagdetails,name="blog_tag_details_page"),
    # url(r'^archive/$',views.archive,name='blog_archive'),
    url(r'^archive/((?P<year>\d+)/((?P<month>\w+)/)?)?$', views.archive, name='blog_archive'),
    

    #manage url conf
    #manage
    url(r'^manage/$',views.admin_dashboard,name='blog_admin_dashboard'),
    #manage blogs
    url(r'^manage/blog/manage/$',views.admin_blogs_manage,name='blog_admin_blogs_manage'),
    #add new blog
    url(r'^manage/blog/new/$',views.admin_blog_new,name='blog_admin_blog_new'),
    #edit blog
    url(r'^manage/blog/edit/(?P<pk>\d+)/$',views.admin_blog_edit,name='blog_admin_blog_edit'),
    #manage comments
    url(r'^manage/comment/manage/$',views.admin_comments_manage,name='blog_admin_comments_manage'),
    #approve/block comment
    url(r'^admin/comment/approve',views.admin_comment_approve,name="blog_admin_comment_approve"),
    url(r'^admin/comment/block',views.admin_comment_block,name="blog_admin_comment_block"),
    #manage comments of some blog
    url(r'^manage/comment/manage/(?P<blog_id>\d+)/$',views.admin_comments_manage,
        name='blog_admin_blog_comments_manage'),
    #edit blog meta
    url(r'^manage/meta/edit/$',views.admin_meta_edit,name='blog_admin_meta_edit'),
]
