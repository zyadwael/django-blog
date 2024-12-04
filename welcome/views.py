from django.shortcuts import render,redirect,get_object_or_404
from .models import BlogPost,Comment
from django.db import IntegrityError
from .forms import UserRegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from django.contrib import messages




@login_required
def welcome_view(request):
    posts = BlogPost.objects.all().distinct()
    post_comments_data = {}

    for post in posts:
        comment_count = Comment.objects.filter(post=post).count()
        print(f"Post ID: {post.id}, Comment Count: {comment_count}")  # Debugging
        post_comments_data[post.id] = comment_count

    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(BlogPost, id=post_id)
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                user=request.user,
                post=post,
                content=content
            )
        return redirect('welcome')

    return render(request, 'index.html', {
        'posts': posts,
        'post_comments_data': post_comments_data,
    })


@login_required
def view_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    comments = post.comments.all()  # Get all comments related to this post

    if request.method == 'POST':
        # Handle adding a new comment
        content = request.POST.get('content')
        if content:
            Comment.objects.create(user=request.user, post=post, content=content)
            return redirect('view_post', post_id=post.id)  # Redirect to the same post to avoid form resubmission

    return render(request, 'post-details.html', {
        'post': post,
        'comments': comments,
        'user_liked': request.user in post.likes.all()  # Check if the user already liked the post
    })


def blog_search(request):
    query = request.GET.get('q', '')
    search_type = request.GET.get('search_type', 'title')

    if search_type == 'title':
        blog_posts = BlogPost.objects.filter(title__icontains=query)
    elif search_type == 'content':
        blog_posts = BlogPost.objects.filter(content__icontains=query)
    elif search_type == 'author':
        blog_posts = BlogPost.objects.filter(author__name__icontains=query)  # Assuming a related 'author' field
    elif search_type == 'tags':
        blog_posts = BlogPost.objects.filter(tags__name__icontains=query)  # Assuming a Many-to-Many 'tags' relationship
    else:
        blog_posts = BlogPost.objects.none()  # Return an empty queryset if no valid search type is selected

    return render(request, 'blog_search.html', {'blog_posts': blog_posts, 'query': query})



def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Sending email
            send_mail(
                subject=f"Blog Contact from {name}",
                message=message,
                from_email=email,  # Using the sender's email
                recipient_list=[settings.DEFAULT_FROM_EMAIL],  # Your email here
                fail_silently=False,
            )

            # Redirect or render a success page
            return render(request, 'contact_success.html', {'name': name})
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')  # Redirect to the homepage or another page
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


def create_post(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        publication_date = request.POST.get('publication_date')
        image = request.FILES.get('image')  # Retrieve image file

        if not title:
            return render(request, "create_post.html", {"error": "Title is required."})

        try:
            # Save the new blog post with the image
            BlogPost.objects.create(
                title=title,
                content=content,
                publication_date=publication_date,
                image=image,  # Save image in database
                author=request.user
            )
            return redirect('welcome_view')  # Replace with the name of your success page/view

        except IntegrityError:
            return render(request, "create_post.html", {"error": "Failed to create post. Please try again."})
    
    return render(request, "create_post.html")

def update_post(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        publication_date_str = request.POST.get('publication_date')

    return render(request, "update_post.html")

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.user != post.author:
        return HttpResponseForbidden("You are not allowed to delete this post.")
    post.delete()
    return redirect('welcome_view')

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    
    content = request.POST.get('content')
    
    if content:
        comment = Comment.objects.create(
            user=request.user,
            post=post,
            content=content
        )
        
        # Return a JSON response with the comment details to update the frontend dynamically
        return JsonResponse({
            'username': comment.user.username,
            'created_at': comment.created_at.strftime('%B %d, %Y, %I:%M %p'),
            'content': comment.content
        })
    else:
        return JsonResponse({'error': 'You must provide content for your comment.'}, status=400)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count()  # Return the updated likes count
    })
