from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post
from apps.accounts.models import Author, Profile


class PostListView(ListView):
    model = Post
    template_name = "posts/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(is_published=True).select_related("author")


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(is_published=True).select_related("author").prefetch_related("tags")


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "posts/post_create.html"
    fields = ["title", "body", "slug", "tags", "is_published"]
    success_url = reverse_lazy("posts:post_list")

    def form_valid(self, form):
        author, _ = Author.objects.get_or_create(
            user=self.request.user,
            defaults={"name": self.request.user.username},
        )
        Profile.objects.get_or_create(author=author)
        form.instance.author = author
        return super().form_valid(form)
