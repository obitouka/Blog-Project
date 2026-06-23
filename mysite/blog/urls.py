from django.urls import path                              # 0.8 django.urls→module for URL routing;path(route,view,name)→maps URL pattern to view function
from . import views                                       # 0.9 '.'→current app;views→file containing functions handling requests
from .feeds import LatestPostsFeed
app_name='blog'                                           # 7.9 Namespace→used in reverse() and {% url %} to avoid name conflicts between apps

urlpatterns=[                                             # urlpatterns→list of URL patterns Django checks sequentially

    path('',views.post_list,name='post_list'),             # 9.11 ''→empty route(homepage '/');     views.post_list→function;name='post_list'→used for reverse lookup

    path('<int:year>/<int:month>/<int:day>/<slug:post>/',  # dynamic URL with converters→int(year,month,day),slug(post)
        views.post_detail,                                # view handling this URL
        name='post_detail'),                              # 7.10 name used in reverse() and get_absolute_url()

    # Example URL→/2026/04/03/my-first-post/

    path('<int:post_id>/share/',                          # dynamic route→post_id(integer) passed to view
        views.post_share,                                # email sharing view
        name='post_share'),                               # 11.14 used in {% url 'blog:post_share' post.id %}

    path('<int:post_id>/comment/',                        # route for submitting comments for a post
        views.post_comment,                              # view handling comment submission
        name='post_comment'),                             # 8.30 used in form action for posting comment

    path('tag/<slug:tag_slug>/',                          # slug converter→string with letters,numbers,hyphens
        views.post_list,                                 # reuse post_list view but with tag filtering
        name='post_list_by_tag'),                         # 3.10 used for filtering posts by tag in templates

    path('feed/', LatestPostsFeed(), name='post_feed'),

    path('search/', views.post_search, name='post_search'),
]