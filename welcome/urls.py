from django.urls import path
from .views import welcome_view,create_post,delete_post,add_comment,register,user_login,user_logout,like_post,view_post
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', welcome_view, name='welcome_view'),
    path('create_post/',create_post,name='create_post'),
    path('delete_post/<int:post_id>/',delete_post,name='delete_post'),
    path('comment/<int:post_id>/', add_comment, name='add_comment'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/',user_logout, name='logout'),
    path('like/<int:post_id>/', like_post, name='like_post'),
    path('post/<int:post_id>/', view_post, name='view_post'),  # URL for viewing a post

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)