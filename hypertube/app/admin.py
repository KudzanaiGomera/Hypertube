from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(Movie)
admin.site.register(MovieLinks)
admin.site.register(Comment)