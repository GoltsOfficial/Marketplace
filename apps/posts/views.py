from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

from .models import Post


@require_http_methods(["GET"])
def post_list(request):
    posts = Post.objects.filter(is_published=True)
    return render(request, "blog/post_list.html", {"posts": posts})


@require_http_methods(["GET"])
@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "blog/post_detail.html", {"post": post})


@require_http_methods(["GET", "POST"])
@login_required
def create_post(request):
    if request.method == "POST":
        title = request.POST.get("title")
        Post.objects.create(title=title)
        return redirect("post_list")
    return render(request, "blog/create_post.html")
