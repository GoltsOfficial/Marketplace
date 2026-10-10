from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

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
        return (
            Post.objects.filter(is_published=True)
            .select_related("author")
            .prefetch_related("tags")
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "posts/post_create.html"
    fields = ["title", "body", "slug", "tags", "is_published"]
    success_url = reverse_lazy("posts:post_list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            author = getattr(request.user, "author", None)
            profile = getattr(author, "profile", None) if author else None
            if not profile or not profile.email_confirmed:
                messages.warning(
                    request,
                    "Чтобы публиковать объявления, подтвердите email в профиле.",
                )
                return redirect("accounts:profile")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        author, _ = Author.objects.get_or_create(
            user=self.request.user,
            defaults={"name": self.request.user.username},
        )
        Profile.objects.get_or_create(author=author)
        form.instance.author = author
        return super().form_valid(form)
