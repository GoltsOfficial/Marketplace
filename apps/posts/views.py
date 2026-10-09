from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post


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
        # Привязываем автора, если есть профиль Author у пользователя
        # Пока просто сохраняем без автора или можно расширить
        form.instance.author_id = 1  # временно, пока нет связи User-Author
        return super().form_valid(form)
