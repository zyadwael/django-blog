from django.db import models
from django.contrib.auth.models import User 

class BlogPost(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(blank=False)
    publication_date = models.DateField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True) 
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', null=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)