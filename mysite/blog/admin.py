from django.contrib import admin                      # 0.11 Django admin system
from .models import Post, Comment                     # 0.12 Import models


# 4.5 ADMIN CONFIG FOR POST MODEL
@admin.register(Post)                                 # 4.6 Register Post in admin panel
class PostAdmin(admin.ModelAdmin):                    # 4.7 Customize how Post appears in admin
    list_display = ['title','id','slug','author','publish','status']
    # 2.32 title → post title
    # 2.33 id → unique ID
    # 2.34 slug → URL name
    # 2.35 author → user who created post
    # 2.36 publish → publish date
    # 2.37 status → Draft/Published
    list_filter = ['status','created','publish','author']
    # 2.38 status → filter Draft/Published
    # 2.39 created → filter by creation date
    # 2.40 publish → filter by publish date
    # 2.41 author → filter by user
    search_fields = ['title','body']
    # 2.42 search in title
    # 2.43 search in body content
    date_hierarchy = 'publish'                        # 5.4 Filter by date hierarchy (year→month→day)
    ordering = ['status','publish']                   # 5.5 Order by status then publish date


# 8.40 ADMIN CONFIG FOR COMMENT MODEL
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name','email','post','created','post']
    # 8.42 name → commenter name
    # 8.43 email → commenter email
    # 8.44 post → related post
    # 8.45 created → when comment was added

    list_filter = ['active','created','updated']
    # 8.46 active → show/hide comments
    # 8.47 created → filter by creation time
    # 8.48 updated → filter by update time

    search_fields = ['name','email','body']
    # 8.49 search by name
    # 8.50 search by email
    # 8.51 search by comment text