from utils import insert_mongo
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

from django.views.generic.base import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.detail import DetailView

from .models import Post, Category, Author, PostView
from .forms import PostForm, CommentForm
from marketing.models import Signup

import json
import pymongo
from pymongo import MongoClient
client = pymongo.MongoClient('mongodb://localhost:27017/')
_db = client["blog"]
collection_name = _db["post"]

'''
class Home(View):
    def get(self, request):
        posts = Post.objects.all()
        context = {
            'posts': posts,
        }
        return render(request, 'blog/home.html', context)'''


# class PostDetail(View):
#     def get(self, request, pk):
#         post = Post.objects.get(pk=pk)
#         return render(request, 'blog/post_detail.html', {'post': post})


# class PostCreate(View):
#     def get(self, request):
#         form = PostForm()
#         return render(request, 'blog/post_form.html', {'form': form})

#     # @method_decorator(insert_mongo("blog", "post"))
#     def post(self, request):
#         form = PostForm(request.POST)
#         if form.is_valid():
#             data = form.save()
#             _data = serializers.serialize("json", [data])
#             collection_name.insert_many(json.loads(_data))
#             return redirect("post:home")
#         return render(request, "blog/post_form.html", {'form': form})


# class Home(ListView):
#     model = Post
#     template_name = "blog/home.html"
#     context_object_name = "posts"
class IndexView(View):
    def get(self, request, *arg, **kwargs):
        posts = Post.objects.filter(featured=True)
        latest = Post.objects.order_by('-timestamp')[:3]
        context = {
            'object_list': posts,
            'latest': latest
        }
        return render(request, 'index.html', context)
    def post(self, request, *arg, **kwargs):
        email = request.POST.get('email')
        new_signup = Signup()
        new_signup.email = email
        new_signup.save()
        return redirect("post:index")


def index(request):
    posts = Post.objects.filter(featured=True)
    latest = Post.objects.order_by('-timestamp')[:3]

    if request.method == 'POST':
        email = request.POST.get('email')
        new_signup = Signup()
        new_signup.email = email
        new_signup.save()

    context = {
        'object_list': posts,
        'latest': latest
    }
    return render(request, 'index.html', context)


class PostListView(ListView):
    model = Post
    template_name = "blog.html"
    context_object_name = "queryset"
    paginate_by = 1

    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-timestamp')[:3]
        context = super(PostListView, self).get_context_data(**kwargs)
        context["most_recent"] = most_recent
        context["page_request_var"] = "page"
        context["category_count"] = category_count
        return context
    

def blog(request):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var, '')
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)
    
    context = {
        'queryset': paginated_queryset,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count
    }
    return render(request, 'blog.html', context)


class PostDetailView(DetailView):
    model = Post
    template_name = "post.html"
    context_object_name = "post"
    form_class = CommentForm()

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated:
            PostView.objects.get_or_create(
                user = self.request.user,
                post = obj
            )
        return obj

    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-timestamp')[:3]
        context = super().get_context_data(**kwargs)
        context["most_recent"] = most_recent
        context["page_request_var"] = "page"
        context["category_count"] = category_count
        context["form"] = self.form_class
        print(context)
        return context

    def post(self, request, *arg, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = self.get_object()
            form.save()
            return redirect(reverse("post:detail", kwargs={
                "pk": self.get_object().pk
            }))



def post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    PostView.objects.get_or_create(user=request.user, post=post)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("post:detail", kwargs={'pk': post.pk}))

    context = {
        'post': post,
        'category_count': category_count,
        'most_recent': most_recent,   
        'form': form
    }
    return render(request, 'post.html', context)


def get_category_count():
    queryset = Post.objects.values('categories__title').annotate(
            Count('categories__title')
        )
    return queryset


class SearchView(View):
    def get(self, request, *arg, **kwargs):
        queryset = Post.objects.all()
        query = request.GET.get('q')
        import pdb
        pdb.set_trace()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(overview__icontains=query)
            ).distinct()
        context = {
            'queryset': queryset
        }
        return render(request, "search_results.html", context)


def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    import pdb
    pdb.set_trace()
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()
    context = {
        'queryset': queryset
    }
    return render(request, "search_results.html", context)


class PostUpdateView(UpdateView):
    model = Post
    template_name = "post_create.html"
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update"
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse('post:detail', kwargs={'pk': form.instance.id}))


def post_update(request, id):
    title = 'Update'
    post = get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None
    , request.FILES or None
    ,instance=post)
    author = get_author(request.user)
    if request.method == 'POST':
        form.instance.author = author
        if form.is_valid():
            form.save()
            return redirect(reverse('post:detail', kwargs={'pk': form.instance.id}))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "post_create.html", context)


class PostDeleteView(DeleteView):
    model = Post
    success_url = "/blog"
    template_name = "post_confirm_delete.html"


def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse('post:blog'))


def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None


class PostCreateView(CreateView):
    model = Post
    template_name = "post_create.html"
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create"
        return context

    def form_valid(self,form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse('post:detail', kwargs={'pk': form.instance.id}))


def post_create(request):
    title = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse('post:detail', kwargs={'pk': form.instance.id}))
    context = {
        'form': form,
        'title': title
    }
    return render(request, "post_create.html", context)