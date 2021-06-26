from django.urls import path, include

from . import views

app_name = "post"

urlpatterns = [
    # path('create/', views.post_create, name="create"),
    # path('post/<pk>/', views.post, name="detail"),
    # path('post/<id>/update/', views.post_update, name="post-update"),    
    # path('post/<id>/delete/', views.post_delete, name="post-delete"),
    # path('', views.index, name="index"),
    # path('blog/', views.blog, name="blog"),
    # path('search/', views.search, name="search"),
    # class base view
    path('', views.IndexView.as_view(), name="index"),
    path('blog/', views.PostListView.as_view(), name="blog"),
    path('post/<pk>/', views.PostDetailView.as_view(), name="detail"),
    path('create/', views.PostCreateView.as_view(), name="create"),
    path('post/<pk>/update/', views.PostUpdateView.as_view(), name="post-update"),  
    path('post/<pk>/delete/', views.PostDeleteView.as_view(), name="post-delete"),
    path('search/', views.SearchView.as_view(), name="search"),
]