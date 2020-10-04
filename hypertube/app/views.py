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

from pyYify import yify
from bs4 import BeautifulSoup

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

    json_response = response.json()
    movies = json_response['data']['movies']

        
    for value in movies:
        Movie.objects.get_or_create(
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

def home(request):
    model = Movie
    if request.method == 'POST':
        queryset = Movie.objects.all().order_by('-rating')
        context = {
            "object_list": queryset
        }
    
    else:
        queryset = Movie.objects.all().order_by('-year_of_production')
        context = {
            "object_list": queryset
        }
    return render(request, 'home.html', context)
        
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
    paginate_by = 10


    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            object_list = self.model.objects.filter(title__icontains=query).order_by('title')

        else:
            object_list = self.model.objects.none()
        return object_list

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
        torrent_name = os.path.join('static/images', filename)
        subprocess.run(['python3', "app/torrent_client/main.py", torrent_name])
        return render(request, 'videoplayer.html')
    return render(request, 'watch.html')

def videoplayer(request):
    return render(request, 'videoplayer.html')

def Watched(request,slug):
    movie=get_object_or_404(Movie,slug=slug)
    if movie.Watched:
        movie.Watched=False
    else:
        movie.Watched=True
    movie.save()
    return redirect('movie_detail', slug=movie.slug)

def watched_movie(request):
    queryset = Movie.objects.filter(Watched=True)
    print(queryset)
    context = {
        "object_list": queryset
    }
    return render(request, 'watched.html', context)
    
def search_external_torrents(request):
    if request.method == 'POST':
        name = request.POST['movie']
        print(name)
        print("")
        for page in range(1, 2):
            #Returns Movies Based On Seeds
            url = "https://yts.mx/browse-movies/" + str(
                name) + "/all/all/0/seeds/0/all"
            r = requests.get(url).text
            soup = BeautifulSoup(r, "lxml")
            for name in soup.findAll(
                "div",
                class_="browse-movie-wrap col-xs-10 col-sm-4 col-md-5 col-lg-4"):
                mov_name = name.find("div", class_="browse-movie-bottom")
                movie_name = mov_name.a.text
                movie_year = mov_name.div.text
                movie_name = movie_name + " " + movie_year
                rating = name.find("h4", class_="rating", text=True)
                if rating is not None:
                    rating = rating.text
                    rating = rating[:3]
                else:
                    rating = "0.0"
                if rating[2] == "/":
                    rating = rating[0:2]
                try:
                    #Handles Movie Name Containing [xx]
                    if movie_name[0] == "[" and movie_name[3] == "]":
                        movie_name = movie_name[5:]
                    movie_name = movie_name.replace(" ", "-")
                    index = 0
                    for char in movie_name:  #Handles Special Character In Url
                        if char.isalnum() == False and char != "-":
                            movie_name = movie_name.replace(char, "")
                    for char in movie_name:
                        if char == "-" and movie_name[index + 1] == "-":
                            movie_name = movie_name[:index] + movie_name[index + 1:]
                        if index < len(movie_name) - 1:
                            index = index + 1
                    if "--" in movie_name:  #Handles Movie Url Containing "--"
                        movie_name = movie_name.replace("--", "-")
                    movie_url = "https://yts.mx/movie/" + movie_name
                    movie_url = movie_url.lower()
                    request = requests.get(movie_url).text
                    n_soup = BeautifulSoup(request, "lxml")
                    info = n_soup.find("div", class_="bottom-info")
                    torrent_info = n_soup.find("p", class_="hidden-xs hidden-sm")
                    genre = n_soup.findAll("h2")[1].text
                    description = n_soup.find("p", class_="hidden-sm hidden-md hidden-lg").text
                    image = n_soup.find("img", class_="img-responsive")["src"]
                    likes = info.find("span", id="movie-likes").text
                    imdb_link = info.find("a", title="IMDb Rating")["href"]
                    for torrent in torrent_info.findAll("a"):
                        if (torrent.text[:3] == "720"):
                            torrent_720 = torrent["href"]
                        if torrent.text[:4] == "1080":
                            torrent_1080 = torrent["href"]
                except Exception as e:
                    likes = None
                    genre = None
                    description = None
                    image = None
                    num_downloads = None
                    imdb_link = None
                    torrent_720 = None
                    torrent_1080 = None
                    pass
                movie_name = mov_name.a.text

                title = movie_name
                category = genre
                year_of_production = movie_year
                movie_url = movie_url
                movie_torrent_link = torrent_720
                rating = rating

                Movie.objects.get_or_create(
                    title=title,
                    category=category,
                    year_of_production=year_of_production,
                    movie_url=movie_url,
                    movie_torrent_link=movie_torrent_link,
                    rating=rating,
                    description=description,
                    image=image
                    )
        print("Done Scrapping...!!")
        return redirect('search_external_torrents')
    else:
        return render(request, 'search_external_torrents.html')

def login42(request):
    code = request.GET.get('code')
    print(code)
    r = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': 'c4504b0c67190db0c8756ba8c42c9f81e64bbdcc2815fa42144585a58dde47f2',
            'client_secret': 'f00df9c6e8e34df9c5ed2950e78c4ad7d410378136b401add7e8a478463a43e1',
            'code': code,
            'redirect_uri': 'http://127.0.0.1:8000/login42.html'
        })
    access_response = r.json()
    token = access_response.get('access_token')
    print(access_response)
    print(token)
    print(type(token))
    if token:
        print(token)
        response = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization':'Bearer '+token})
        data = response.json()
        login_name = data['login']
        email = data['email']
        user_firstname = data['first_name']
        last_name = data['last_name']

        User.objects.get_or_create(username = login_name, email = email, first_name = user_firstname, last_name =last_name)
        user = authenticate(username=login_name)
        print(user)
        if user is not None:
            print('it went here')
            login(request, user, backend='app.auth_backend.PasswordlessAuthBackend')
            return redirect('index')
    return render(request, 'login42.html')