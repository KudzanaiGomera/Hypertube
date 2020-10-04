from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.conf.urls.static import static
from django.utils.text import slugify
from django.utils import timezone
from PIL import Image
import uuid

# Create your models here.
class Profile(models.Model):
   user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
   profile_pic = models.ImageField(upload_to='images', default='profile.png', null=True, blank=True)
   date_created = models.DateTimeField(auto_now_add=True, null=True)

   def __str__(self):
      return f'{self.user.username} Profile'

   def save(self, *args, **kwargs):
      super(Profile, self).save(*args, **kwargs)

      img = Image.open(self.profile_pic.path)

      if img.height > 200 or img.width > 200:
         output_size = (200, 200)
         img.thumbnail(output_size)
         img.save(self.profile_pic.path)


CATEGORY_CHOICES = (
   ('action', 'ACTION'), 
   ('drama', 'DRAMA'),
   ('comedy', 'COMEDY'),
   ('romance', 'ROMANCE'),
)

LANGUAGE_CHOICES = (
   ('english', 'ENGLISH'), 
   ('german', 'GERMAN'),
)

STATUS_CHOICES = (
   ('RA', 'RECENTLY ADDED'), 
   ('MW', 'MOST WATCHED'),
   ('TR', 'TOP RATED'),
)

class Movie(models.Model):
   title = models.CharField(max_length=100)
   description = models.TextField(max_length=1000)
   image = models.ImageField(upload_to='images')
   banner = models.ImageField(upload_to='images')
   category = models.CharField(choices=CATEGORY_CHOICES, max_length=100)
   language = models.CharField(choices=LANGUAGE_CHOICES, max_length=10)
   status = models.CharField(choices=STATUS_CHOICES, max_length=2)
   year_of_production = models.IntegerField(null=True)
   views_count = models.IntegerField(default=0)
   cast = models.CharField(max_length=100)
   slug = models.SlugField(blank=True, null=True)
   movie_trailer = models.URLField()
   movie_url = models.URLField()
   movie_torrent_link = models.URLField()
   rating = models.FloatField(null=True)
   runtime = models.IntegerField(null=True)
   Watched=models.BooleanField(default=False)
   created = models.DateTimeField(default=timezone.now)

   def save(self, *args, **kwargs):
      if not self.slug:
         self.slug = slugify(self.title)
      super(Movie, self).save(*args, **kwargs)

   def __str__(self):
      return self.title

LINK_CHOICES = (
   ('D', 'DOWNLOAD LINK'),
   ('W', 'WATCH LINK'),
)

class MovieLinks(models.Model):
   movie = models.ForeignKey(Movie, related_name='movie_watch_link', on_delete=models.CASCADE)
   type = models.CharField(choices=LINK_CHOICES, max_length=1)
   link = models.URLField()

   def __str__(self):
      return str(self.movie)

class Comment(models.Model):
   user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
   movie = models.ForeignKey(Movie, related_name='comments', on_delete=models.CASCADE)
   comment = models.TextField()
   date_added = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return f'{self.user.username} Comment'

