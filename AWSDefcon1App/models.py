from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models

class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    wins = models.IntegerField(default=0)
    achievements = models.IntegerField(default=0)
    bio = models.CharField(max_length=500, null=True, blank=True)
    pass

class Games(models.Model):
    id = models.BigAutoField(primary_key=True)
    players = models.IntegerField(default=7)
    player0 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_player0', null=True) #Cuba
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_player1', null=True) #UK
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_player2', null=True) #USA
    player3 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_player3', null=True) #France
    player4 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_player4', null=True) #USSR
    player5 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_player5', null=True) #Germany
    player6 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_player6', null=True) #Italy
    player7 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_player7', null=True) #Japan

class Nations(models.Model):
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    player_number = models.IntegerField(default=0)
    states = models.IntegerField()
    divisions = models.IntegerField()
    boats = models.IntegerField()
    planes = models.IntegerField()
    alliance_name = models.CharField(max_length=255, null=True, blank=True)
    points = models.IntegerField()
    nuke_time = models.IntegerField()
    nukes = models.IntegerField()
    nuked = models.IntegerField(default = 0)
    attacks = models.IntegerField(default = 0, null=True, blank=True)
    requests = models.IntegerField(default = 4, null=True, blank=True)
    spies = models.IntegerField(default = 10, null=True, blank=True)
    friendlyness = models.IntegerField(default = 10, null=True, blank=True)


class MakeAlliance(models.Model):
    nation1 = models.ForeignKey(Nations, on_delete=models.CASCADE, related_name='nation1_alliances')
    nation2 = models.ForeignKey(Nations, on_delete=models.CASCADE, related_name='nation2_alliances')

class War(models.Model):
    nation1 = models.ForeignKey(Nations, on_delete=models.CASCADE, related_name='nation1_wars')
    nation2 = models.ForeignKey(Nations, on_delete=models.CASCADE, related_name='nation2_wars')

class FreindRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alliance_requests_sent')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alliance_requests_received')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')

class Map(models.Model):
    number = models.IntegerField()
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    
class Square(models.Model):
    map = models.ForeignKey(Map, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="")
    number = models.IntegerField()
    owner = models.ForeignKey(Nations, on_delete=models.CASCADE)
    neighbors = models.JSONField(default=list)
    color = models.CharField(max_length=255)
    coastal = models.BooleanField(default=False)

class GameTiming(models.Model):
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    days_passed = models.IntegerField(default=0)
    
class Announcements(models.Model):
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    text = models.CharField(max_length=1000, null=True, blank=True)

class Achievements(models.Model):
    name = models.CharField(max_length=255, default="")
    users = models.JSONField(default=list)

class Message(models.Model):
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()
    read = models.BooleanField(default=False)

class DM(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='DM_sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='DM_received_messages')
    text = models.TextField()
    read = models.BooleanField(default=False)
