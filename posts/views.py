from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, NewForm
from .models import Follow, Group, Post, User


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "latest": latest,
        "paginator": paginator
    }
    return render(request, "index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        "group": group,
        "page": page,
        "paginator": paginator
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    form = NewForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    author = get_object_or_404(User, username=username)
    follow_count = Follow.objects.filter(author=author).count()
    follow1_count = Follow.objects.filter(user=author).count()
    following = Follow.objects.filter(user__username=request.user,
                                      author=author)

    context = {
        "page": page,
        "author": user,
        "paginator": paginator,
        'follow_count': follow_count,
        'follow1_count': follow1_count,
        'following': following
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    form = CommentForm(request.POST or None)
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    posts = user.posts.all()
    comments = post.comments.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        "form": form,
        "page": page,
        "post": post,
        "comments": comments,
        "author": post.author,
        "paginator": paginator,
    }

    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)

    form = NewForm(
        request.POST or None, files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)

    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }

    return render(request, 'new_post.html', context)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

    return redirect('post', post.author, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    follow = True
    context = {'page': page,
               'paginator': paginator,
               'follow': follow}
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.username != username:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(user=request.user,
                          author__username=username).delete()
    return redirect('profile', username)
