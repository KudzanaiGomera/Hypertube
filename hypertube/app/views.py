from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import connections
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
from .forms import AccountForm, ProfileForm, CommentForm, UserUpdateForm
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.dates import YearArchiveView
from django.core.files.storage import FileSystemStorage
from .models import *
import mysql.connector
import bcrypt
import re, sys
import requests
import subprocess
import os

sys.setrecursionlimit(1500)

# Create your views here.

def login2(request):
    #check if username and password POST requests exits (user submitted form)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, "incorrect Username or Password...")
    context = {}
    return render(request, 'login.html')

def logoutUser(request):
    logout(request)
    return redirect('login2')

def register(request):
    form = AccountForm()
   
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
            user  = form.cleaned_data.get('username')

            messages.success(request, 'Account successfully created for ' + user)
            return redirect('login2')
        
    context = {'form':form}   
    return render(request, 'register.html', context)

def index(request):
    response = requests.get(
    'https://yts.mx/api/v2/list_movies.json',
     params={'page':'400','limit':'20'},
    )
    #https://yts.mx/api/v2/movie_details.json',
    #params={'movie_id':'movie_id', 'with_cast':'true'}

    #movie_id = movies[0]['id]

    json_response = response.json()
    movies = json_response['data']['movies']

    if not Movie.objects.all():    
        for value in movies:
            Movie.objects.create(
                title=value['title'],
                description = value['description_full'],
                image = value['medium_cover_image'],
                category = value['genres'][0],
                year_of_production = value['year'],
                movie_url = value['url'],
                movie_torrent_link = value['torrents'][0]['url'],
                rating = value['rating'],
                runtime = value['runtime'],
            )
    else:
        messages.info(request, "Movie..exists")
    return render(request, 'index.html',)

def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, 
                             request.FILES,
                             instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Account successfully Updated for ')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
        }
    return render(request, 'profile.html', context)

def movies(request):
    return render(request, 'movies.html')

class HomeView(ListView):
    model = Movie
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['top_rated'] = Movie.objects.filter(status='TR')
        context['most_watched'] = Movie.objects.filter(status='MW')
        context['recently_added'] = Movie.objects.filter(status='RA')
        return context
        
class MovieList(ListView):
    model = Movie
    paginate_by = 10

class MovieDetail(DetailView):
    model = Movie

    def get_object(self):
        object = super(MovieDetail, self).get_object()
        object.views_count += 1
        object.save()
        return object

    def get_context_data(self, **kwargs):
        context = super(MovieDetail, self).get_context_data(**kwargs)
        context['links'] = MovieLinks.objects.filter(movie=self.get_object())
        context['related_movies'] = Movie.objects.filter(category=self.get_object().category)
        context['comment'] = Comment.objects.all()
        context['form'] = CommentForm()
        return context

class MovieCategory(ListView):
    model = Movie
    paginate_by = 2


    def get_queryset(self):
        self.category = self.kwargs['category']
        return Movie.objects.filter(category=self.category)

    def get_context_data(self , **kwargs):
        context = super(MovieCategory, self).get_context_data(**kwargs)
        context['movie_category'] = self.category
        return context


class MovieLanguage(ListView):
    model = Movie
    paginate_by = 2


    def get_queryset(self):
        self.language = self.kwargs['lang']
        return Movie.objects.filter(category=self.language)

    def get_context_data(self , **kwargs):
        context = super(MovieLanguage, self).get_context_data(**kwargs)
        context['movie_language'] = self.language
        return context


class MovieSearch(ListView):
    model = Movie
    paginate_by = 2


    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            object_list = self.model.objects.filter(title__icontains=query).order_by('title')

        else:
            object_list = self.model.objects.none()
        return object_list

class MovieYear(YearArchiveView):
    queryset = Movie.objects.all()
    date_field = 'year_of_production'
    make_object_list = True
    allow_future = True


def add_comment(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.movie = movie
            comment.user = request.user
            comment.save()
            return redirect('movie_detail', slug=movie.slug)
    else:
        form = CommentForm()
    template = 'add_comment.html'
    context = {
        'form':form,
        }
    return render(request, template,context)

def watch(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        # torrent_path = os.path.join('Hypertube/hypertube', 'static/images')
        torrent_name = os.path.join('static/images', filename)
        subprocess.run(['python3', "app/torrent_client/main.py", torrent_name])
        return render(request, 'videoplayer.html')
    return render(request, 'watch.html')

def videoplayer(request):
    return render(request, 'videoplayer.html')
    