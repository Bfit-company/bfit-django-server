from django.contrib import admin
from coach_app.models import CoachDB
# Register your models here.
from post_app.models import PostDB

admin.site.register(PostDB)