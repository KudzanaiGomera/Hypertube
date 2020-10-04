from django.urls import path, NoReverseMatch
from django.conf import settings

from django.contrib.auth import views as auth_views
from django.urls import path, include

from . import views
from . views import MovieList, MovieDetail, MovieCategory, MovieLanguage, MovieSearch

urlpatterns = [
    path('login.html', views.login2, name='login2'),
    path('login42.html', views.login42, name='login42'),
    path('register.html', views.register, name='register'),
    path('', views.index, name='index'),
    path('logoutUser', views.logoutUser, name='logoutUser'),
    path('profile.html', views.profile, name='profile'),
    path('movies.html', views.movies, name='movies'),
    path('watch.html', views.watch, name='watch'),
    path('home.html', views.home, name='home'),
    path('videoplayer.html', views.videoplayer, name='videoplayer'),
    path('search_external_torrents.html', views.search_external_torrents, name='search_external_torrents'),

    path('movie_list/', MovieList.as_view(template_name="movie_list.html"), name="movie_list"),
    path('movie_category/<str:category>/', MovieCategory.as_view(template_name="movie_list.html"), name="movie_category"),
    path('movie_language/<str:lang>/', MovieLanguage.as_view(template_name="movie_list.html"), name="movie_language"),
    path('search', MovieSearch.as_view(template_name="movie_list.html"), name="search"),
    path('movie_detail/<str:slug>/', MovieDetail.as_view(template_name="movie_detail.html"), name="movie_detail"),
    # path('movie_year/<int:year>/', MovieYear.as_view(template_name="movie_archive_year.html"), name="movie_year"),
    path('movie_detail/<str:slug>/add_comment/', views.add_comment, name="add_comment"),
    

    #movies/<movie_id>/watched/
    path('movie_detail/<str:slug>/watched/',views.Watched,name="watched"),
    path('watched_movie',views.watched_movie,name='watched_movie'),


    path('reset_password/', 
        auth_views.PasswordResetView.as_view(template_name="password_reset.html"),
        name="reset_password"),
    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), 
        name="password_reset_done"),
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"), 
        name="password_reset_confirm"),
    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"), 
        name="password_reset_complete"),

    path('oauth/', include('social_django.urls',namespace='social')),
]

