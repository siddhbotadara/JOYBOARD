from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class PlayerRecord(models.Model):
    username = models.CharField(max_length=100)
    time_taken = models.FloatField()
    level_completed = models.IntegerField()
    input_used = models.CharField(max_length=20)
    date_played = models.DateTimeField(auto_now_add=True)

class GameSession(models.Model):
    username = models.CharField(max_length=150)
    time_taken = models.FloatField()
    level_completed = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

class BannedUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return getattr(self, 'user', None) or self.username or "BannedUser"