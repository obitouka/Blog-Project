from django.db import models                          # 0.1 Core Django ORM (creates DB tables)
from django.utils import timezone                     # 0.2 Time utilities (timezone-aware current time)
from django.conf import settings                      # 0.3 Access AUTH_USER_MODEL (User table)
from django.urls import reverse                       # 7.1 Used to generate URLs dynamically
from taggit.managers import TaggableManager           # 3.1 Tag system (external library)


# 4.1 CUSTOM MANAGER (filter only published posts)
class PublishedManager(models.Manager):               # 4.2 Extends default manager
    def get_queryset(self):                           # 4.3 Override default query
        return super().get_queryset().filter(          # 4.4 super()→base query,filter→apply condition
            status=Post.Status.PUBLISHED              # 2.1 STATUS reuse→only published posts
        )


# 1.1 MAIN POST MODEL (represents blog post table)
class Post(models.Model):                             # 1.2 models.Model→creates DB table
    # 2.2 STATUS SYSTEM
    class Status(models.TextChoices):                 # 2.3 Creates dropdown choices
        DRAFT = "DF","Draft"                          # 2.4 DB="DF",UI="Draft"→hidden post
        PUBLISHED = "PB","Published"                  # 2.5 DB="PB",UI="Published"→visible post

    # 1.3 TITLE FIELD
    title = models.CharField(max_length=250)          # 1.4 Stores post title(max 250 chars)
    # Example→"How to Learn Django"

    # 1.5 SLUG FIELD (URL identifier)
    slug = models.SlugField(
        max_length=250,                               # 1.6 Max length
        unique_for_date='publish'                     # 1.7 Prevent duplicate slug per date
    )
    # Example→"how-to-learn-django"

    # 1.8 AUTHOR RELATION
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,                    # 1.9 Links to User model
        on_delete=models.CASCADE,                    # 1.10 Delete posts if user deleted
        related_name='blog_posts'                    # 1.11 Access→user.blog_posts.all()
    )

    # 1.12 BODY CONTENT
    body = models.TextField()                        # 1.13 Unlimited text(blog content)

    # 1.14 DATE FIELDS
    publish = models.DateTimeField(
        default=timezone.now                         # 1.15 Default=current time
    )
    created = models.DateTimeField(auto_now_add=True) # 1.16 Set once on creation
    updated = models.DateTimeField(auto_now=True)     # 1.17 Updates every save

    # 2.6 STATUS FIELD
    status = models.CharField(
        max_length=2,                                # 2.7 Stores DF/PB
        choices=Status.choices,                      # 2.8 Connects dropdown
        default=Status.DRAFT                         # 2.9 Default=Draft
    )

    # 3.2 TAG SYSTEM
    tags = TaggableManager()                         # 3.3 Add tags like "python","django"

    # 4.5 MANAGERS
    objects = models.Manager()                       # 4.6 Default(all posts)
    published = PublishedManager()                  # 4.7 Only published posts

    # 5.1 META CONFIG
    class Meta:
        ordering = ['-publish']                      # 5.2 Latest posts first
        indexes = [models.Index(fields=['-publish'])]# 5.3 Faster DB queries

    # 6.1 STRING OUTPUT
    def __str__(self):
        return self.title                            # 6.2 Shows title in admin

    # 7.2 ABSOLUTE URL SYSTEM
    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',                      # 7.3 URL name
            args=[
                self.publish.year,                  # 7.4 Year
                self.publish.month,                 # 7.5 Month
                self.publish.day,                   # 7.6 Day
                self.slug                          # 7.7 Slug
            ]
        )
    # Output→/2026/04/03/my-post/


# 8.1 COMMENT MODEL
class Comment(models.Model):
    # 8.2 RELATION
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,                   # 8.3 Delete comments if post deleted
        related_name='comments'                     # 8.4 Access→post.comments.all()
    )

    # 8.5 USER INPUT
    name = models.CharField(max_length=80)          # 8.6 Commenter name
    email = models.TextField()                      # 8.7 Email
    body = models.TextField()                       # 8.8 Comment text

    # 8.9 TIME
    created = models.DateTimeField(auto_now_add=True)# 8.10 Created once
    updated = models.DateTimeField(auto_now=True)    # 8.11 Updated on edit

    # 8.12 VISIBILITY
    active = models.BooleanField(default=True)      # 8.13 True=visible

    # 8.14 META
    class Meta:
        ordering = ['created']                      # 8.15 Oldest first
        indexes = [models.Index(fields=['created'])]# 8.16 Faster query

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"  # 8.17 Display