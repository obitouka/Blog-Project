from django.shortcuts import render,get_object_or_404   # 0.6 django.shortcuts→helper module;render(request,template,context)→returns HTML response;get_object_or_404(Model,conditions)→returns object or raises 404
from . models import Post                                # 0.7 '.'→current app;models→file;Post→class mapped to DB table
from django.core.mail import send_mail                   # 11.1 send_mail(subject,message,from,recipient_list)→sends email using configured SMTP
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger # 9.1 Paginator→splits queryset into pages;EmptyPage→exception if page too high;PageNotAnInteger→exception if invalid page
from .forms import CommentForm,EmailPostForm, SearchForm           # 8.18 CommentForm→ModelForm for comments;11.2 EmailPostForm→Form for email input
from django.views.decorators.http import require_POST    # 8.19 decorator→restricts view to only POST requests
from taggit.models import Tag                            # 3.3 Tag model from django-taggit→used for tagging posts
from django.db.models import Count                       # 10.1 Count(field)→counts related rows (used in aggregation)
from django.contrib.postgres.search import SearchVector, TrigramSimilarity
from django.contrib.postgres.search import (SearchVector, SearchQuery, SearchRank)

# 9.2 POST LIST (HOME PAGE)
def post_list(request,tag_slug=None):                   # request→HttpRequest object(tag,data,headers);tag_slug→optional URL parameter
    post_list=Post.published.all()                      # 4.8 Post→model;published→custom manager;.all()→QuerySet of only published posts
    tag=None                                            # Python variable initialized to None(no tag selected)

    if tag_slug:                                        # checks if tag_slug is not None/empty
        tag=get_object_or_404(Tag,slug=tag_slug)        # Tag→model;slug=tag_slug→lookup condition;returns object or 404
        post_list=post_list.filter(tags__in=[tag])      # filter()→QuerySet method;tags→ManyToMany field;__in→SQL IN lookup;[tag]→list→returns posts with that tag

    paginator=Paginator(post_list,3)                    # 9.3 Paginator(object_list,per_page)→splits posts into pages of 3 items each
    page_number=request.GET.get('page',1)               # request.GET→QueryDict of URL params;'page'→key;1→default if missing

    try:
        posts=paginator.page(page_number)               # .page(n)→returns Page object(containing objects + metadata like has_next)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)       # paginator.num_pages→total pages;fallback to last page
    except PageNotAnInteger:
        posts=paginator.page(1)                         # fallback to first page if invalid input

    return render(request,'blog/post/list.html',{       # render()→loads template and injects context dict
        'posts':posts,                                  # 'posts' key→Page object (iterable in template)
        'tag':tag                                       # 'tag' key→current tag object or None
    })


# 10.2 POST DETAIL
def post_detail(request,year,month,day,post):            # year,month,day,post(slug) extracted from URL path converters
    post=get_object_or_404(                             # safe DB fetch or 404 response
        Post,                                           # model class
        status=Post.Status.PUBLISHED,                   # filter→only published posts(using TextChoices enum)
        slug=post,                                      # match slug field with URL slug
        publish__year=year,                             # field lookup→extract year part of DateTimeField
        publish__month=month,                           # month lookup
        publish__day=day                                # day lookup
    )
    comments=post.comments.filter(active=True)          # post.comments→reverse relation via related_name;filter(active=True)→only visible comments
    form=CommentForm()                                  # instantiate empty form(unbound form)

    # 10.3 SIMILAR POSTS
    post_tags_ids=post.tags.values_list('id',flat=True) # values_list('id')→get only id column;flat=True→returns simple list instead of tuples
    similar_posts=Post.published.filter(                # QuerySet of published posts
        tags__in=post_tags_ids                          # tags__in→SQL IN lookup;matches posts having any of these tag IDs
    ).exclude(id=post.id)                               # exclude()→remove current post from results

    similar_posts=similar_posts.annotate(               # annotate()→adds computed field to each row
        same_tags=Count('tags')                         # Count('tags')→number of tags each post shares
    ).order_by('-same_tags','publish')[:4]              # order_by()→sort(descending by same_tags,then publish);[:4]→limit to top 4

    return render(request,"blog/post/detail.html",{     # render detail template
        'post':post,                                    # single Post object
        'comments':comments,                            # QuerySet of comments
        'form':form,                                    # form instance
        'similar_posts':similar_posts                   # QuerySet of similar posts
    })


# 11.3 EMAIL SYSTEM
def post_share(request,post_id):                        # post_id→integer from URL
    post=get_object_or_404(Post,id=post_id,status=Post.Status.PUBLISHED) # fetch post with id AND published status
    sent=False                                          # boolean flag(initially False)

    if request.method=='POST':                          # request.method→string like 'GET'/'POST';POST means form submitted
        form=EmailPostForm(request.POST)                # bind form with POST data(QueryDict)
        if form.is_valid():                             # runs validation rules(field types,required,etc.)
            cd=form.cleaned_data                        # cleaned_data→dict of validated inputs
            post_url=request.build_absolute_uri(        # build_absolute_uri(path)→converts relative URL to full URL
                post.get_absolute_url()                 # get_absolute_url()→returns relative path from model
            )
            subject=f"{cd['name']} recommends {post.title}"  # f-string→string formatting;cd['name']→sender;post.title→title
            message=f"Read at {post_url}\n\n{cd['comments']}" # \n→newline;message body with URL + user comment
            send_mail(subject,message,None,[cd['to']])  # send_mail args→(subject,message,from_email,recipient_list);None→default sender;list required for recipients
            sent=True                                   # update flag after sending
    else:
        form=EmailPostForm()                            # create empty(unbound) form for GET request

    return render(request,'blog/post/share.html',{      # render share page
        'post':post,
        'form':form,
        'sent':sent
    })


# 8.22 COMMENT SYSTEM
@require_POST                                           # decorator ensures only POST requests reach this view
def post_comment(request,post_id):
    post=get_object_or_404(Post,id=post_id,status=Post.Status.PUBLISHED) # fetch valid post
    form=CommentForm(data=request.POST)                 # bind form with POST data
    comment=None                                        # initialize variable

    if form.is_valid():                                 # validate input
        comment=form.save(commit=False)                 # commit=False→create model instance without saving to DB
        comment.post=post                               # manually assign ForeignKey(post) before saving
        comment.save()                                  # save instance to DB

    return render(request,'blog/post/comment.html',{    # render result page
        'post':post,
        'form':form,
        'comment':comment
    })

# def post_search(request):
#     form = SearchForm()
#     query = None
#     results = []
#     if 'query' in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             results = (Post.published.annotate(
#                 search = SearchVector('title', 'body'),).filter(search = query)            
#             )

#     return render(request, 'blog/post/search.html',{
#         'form':form,
#         'query':query,
#         'results':results
#     })


# def post_search(request):
#     form = SearchForm()
#     query = None
#     results = []
#     if 'query' in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             search_vector = SearchVector('title', weight='A')+SearchVector('body', weight='B')
#             search_query = SearchQuery(query)
#             results = (
#                 Post.published.annotate(
#                     search=search_vector,
#                     rank=SearchRank(search_vector, search_query)
#                 )
#                 .filter(rank__gte=0.3)
#                 .order_by('-rank')
#             )
#     return render(
#         request,
#         'blog/post/search.html',
#         {
#             'form': form,
#             'query': query,
#             'results': results
#         }
#     )



def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = (
                Post.published.annotate(
                    similarity = TrigramSimilarity('title', query)
                )
                .filter(similarity__gte=0.01)
                .order_by('-similarity')
            )
    return render(
        request,
        'blog/post/search.html',
        {
            'form': form,
            'query': query,
            'results': results
        }
    )