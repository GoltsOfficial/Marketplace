from django.views.generic import ListView, DetailView

from .models import Post

# @require_http_methods(["GET"])
# def post_list(request):
#     posts = Post.objects.filter(is_published=True)
#     return render(request, "blog/post_list.html", {"posts": posts})
#
#
# @require_http_methods(["GET"])
# @login_required
# def post_detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     return render(request, "blog/post_detail.html", {"post": post})
#
#
# @require_http_methods(["GET", "POST"])
# @login_required
# def create_post(request):
#     if request.method == "POST":
#         title = request.POST.get("title")
#         Post.objects.create(title=title)
#         return redirect("post_list")
#     return render(request, "blog/create_post.html")

'''
Generic views для всего CRUD
Полный набор дженериков покрывает CRUD:
 ListView (список), 
 DetailView (один объект), 
 CreateView (создание формой), 
 UpdateView (редактирование), 
 DeleteView (удаление). 
 CreateView и UpdateView сами строят форму из модели, 
 валидируют её и сохраняют — об этом 
 подробнее в разделе про формы.
'''


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
