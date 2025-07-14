from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import User,Games,Nations,Map,Square,War,MakeAlliance,Announcements,Message,DM,Achievements
from django.contrib.admin.views.decorators import staff_member_required
import random
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count
import datetime
from datetime import datetime
from django.db.models import Max
import math
from PIL import Image, ImageOps
import os
from glob import glob
import requests
import base64
import io
import re

api_key = "ba9263b16b26bece76964b0b4cad6b6d"

colors = {
    'United Kingdom': '#ff4879',
    'Soviet Union': '#a3101f',
    'Italy': '#56a552',
    'Second Brazilian Republic': '#62bd52',
    'Sultanate of Aussa': '#4d0019',
    'Turkey': '#c7e9b4',
    'Norway': '#623c3c',
    'Iraq': '#e79481',
    'Saudi Arabia': '#def7c6',
    'United States': '#57a1ff',
    'Albania': '#c23b85',
    'Dominion of Canada': '#9b3e33',
    'France': '#4892FF',
    'Kingdom of Hungary': '#ffa47f',
    'China': '#dfe5a0',
    'Chile': '#ca828b',
    'Peru': '#fff6ff',
    'British Raj': '#c80a0a',
    'Spain': '#ffff79',
    'Kingdom of Greece': '#79ebff',
    'Lithuania': '#ffff9b',
    'Mexico': '#86c66c',
    'Ethiopia': '#c3a5f5',
    'Romania': "#9e9e00", #Spain
    'Portugal': '#33965b',
    'Bhutan': '#ac7a58',
    'Poland': '#ff7789',
    'Australia': '#49bb7e',
    'Czechoslovakia': '#46d8cb',
    'Sweden': '#2eadff',
    'Venezuela': '#70b626', #Denmark
    'Yugoslavia': '#5e5ea4',
    'Netherlands': '#ffb35f',
    'German Reich': '#525252',
    'Bulgaria': '#329a00',
    'Belgium': '#fbdf0a',
    'South Africa': '#be96fa',
    'Philippines': '#b496e6',
    'Uruguay': '#abbe99',
    'Argentina': '#bdccff',
    'Republic of Paraguay': '#4696fa',
    'Mengkukuo': '#a5e684',
    'Japan': '#fee8c8',
    'Ireland': '#68cf75',
    'Costa Rica': '#927a30',
    'Cuba': '#8b40a6',
    'Colombia': '#fff375',
    'Sinkiang': '#3fb08d',
    'Yunnan': '#698948',
    'Dominican Republic': '#bea0f0',
    'Mongolia': '#5a771d',
    'Switzerland': '#c15151',
    'Ecuador': '#ffbe7f',
    'El Salvador': '#fabe78',
    'Iran': '#5c927e',
    'Xibei San Ma': '#685b84',
    'Denmark': '#e25c0e', #Iceland
    'Guangxi Clique': '#8a9a74',
    'Guatemala': '#473070',
    'Haiti': '#ab6f72',
    'Finland': '#ffffff',
    'Estonia': '#63cdfe',
    'Manchukuo': '#ff7847',
    'Afghanistan': '#53d0d9',
    'Honduras': '#B6E01F', #Guanxi Clique
    'Iceland': '#c79779',
    'Siam': '#d7f0c8',
    'Dutch East Indies': '#5b21e2', #Netherlands
    'Latvia': '#7b7cb8',
    'Bolivian Republic': '#ffeab1',
    'Liberia': '#cdafff',
    'Austria': '#a999f0', #Finland
    'Luxembourg': '#8adba2',
    'Tibet': '#456722',
    'Nepal': '#c8aafa',
    'Nicaragua': '#92b2bf',
    'British Malaya': '#e623d5', #Britain
    'New Zealand': '#b99beb',
    'Oman': '#905c5c', #Yemen
    'Shanxi': '#651e29',
    'Panama': '#9e8add',
    'Communist China': '#b2233b',
    'Tannu Tuva': '#e94a4a', #Nepal
    'Yemen': '#905d5d',
}

def bad_request(request, title="Invalid Request", message="Please try again."):
    return render(request, "AWSDefcon1App/error.html", {
        "title": title,
        "message": message
    })

def ads(request):
      return render(request, "AWSDefcon1App/ads.html")
def gameMonetize(request):
      return render(request, "AWSDefcon1App/gameMonetize.html")
def credits(request):
      return render(request, "AWSDefcon1App/credits.html")

def error(request, exception):
      return render(request, "AWSDefcon1App/error.html")
  
def error500(request):
        return bad_request(request, title="A serious issue occured", message="The action you just did is not currently working, this issue will not fix itself automatically and you will need to wait for the developer to fix it")

def error404(request, exception):
    return bad_request(request, title="Page does not exsist", message="The page you are trying to access does not exsist, check the URL to make sure there are no typos")
    
@login_required(login_url='login')
def passer(request, game_id):
    user = request.user
    nation = Nations.objects.get(game = game_id, user = user)
    nation.attacks = 0
    nation.save()
    all_nations = Nations.objects.filter(game = game_id, player_number__lt = 8).exclude(user = User.objects.get(username = "loser")).exclude(user = User.objects.get(username = "empty")).exclude(user = User.objects.get(username = "closed"))
    i = 0
    j = 0
    for nation in all_nations:
      i += 1
      if nation.attacks == 0:
        j += 1
    j += 2
    if i < j:
      nations = Nations.objects.filter(game = game_id)
      for nation in nations:
          states = nation.states
          mult = 1
          if states <= 20:
              mult = 2
          elif states < 50:
              mult = 1.7
          elif states < 150:
              mult = 1.5
          elif states < 200:
              mult = 1.4
          elif states < 250:
              mult = 1

          nation.divisions = nation.divisions + states * mult
          nation.planes = nation.planes + states * 10
          nation.boats = nation.boats + states / 2
          nation.points += 1
          if nation.nuke_time <= 0:
              nation.nukes += 1
          else:
              nation.nuke_time -= 1
          nation.attacks = 5
          nation.requests = 10
          nation.save()
    nations = Nations.objects.filter(game=game_id)
    user = request.user.username
    # Get the player's nation
    playernation = Nations.objects.filter(game=game_id, user=request.user).first()
    if playernation and playernation.alliance_name:
        knownnations = Nations.objects.filter(game=game_id, alliance_name=playernation.alliance_name)
    else:
        knownnations = [playernation] if playernation else []
    return HttpResponseRedirect(reverse('map', kwargs={'game_id': game_id}))


@login_required(login_url='login')
def message(request, game_id, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    game = get_object_or_404(Games, id=game_id)
    unread = Message.objects.filter(sender =recipient, receiver=request.user, read=False)
    for unreaded in unread:
        unreaded.read = True
        unreaded.save()    
    if request.method == 'POST':
        content = request.POST.get('content')
        Message.objects.create(sender=request.user, receiver=recipient, text=content, game=game)

        # Notify recipient via WebSocket
    
    messages = Message.objects.filter(
        game=game,
        receiver__in=[request.user, recipient],
        sender__in=[request.user, recipient]
    ).order_by('id')
    return render(request, 'AWSDefcon1App/message.html', {'recipient': recipient, 'messages': messages, 'game_id': game_id})


@login_required(login_url='login')
def SendDM(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    unread = DM.objects.filter(sender =recipient, receiver=request.user, read=False)
    for unreaded in unread:
        unreaded.read = True
        unreaded.save()
    if request.method == 'POST':
        content = request.POST.get('content')
        DM.objects.create(sender=request.user, receiver=recipient, text=content)
    
    messages = DM.objects.filter(
        receiver__in=[request.user, recipient],
        sender__in=[request.user, recipient]
    ).order_by('id')
    return render(request, 'AWSDefcon1App/message.html', {'recipient': recipient, 'messages': messages})


@login_required(login_url='login')
def user_list(request, game_id):
    if game_id == 0:
        users = User.objects.exclude(id=request.user.id).distinct()
        return render(request, 'AWSDefcon1App/user_list.html', {'users': users, 'game_id': game_id})
    else: 
        game = get_object_or_404(Games, id=game_id)
        users = User.objects.filter(nations__game=game).exclude(id=request.user.id).distinct()
        return render(request, 'AWSDefcon1App/user_list.html', {'users': users, 'game_id': game_id})

@login_required(login_url='login')
def profile(request, user_id):
    user = User.objects.get(id=user_id)
    hunWins = False
    ruleTheWorld = False
    cubaWins = False
    cubaRules = False
    defcon1 = False
    if user.wins == 100 or user.wins > 100 and user.id not in Achievements.objects.get(name = "100 Wins").users:
        achievement = Achievements.objects.get(name="100 Wins")
        users_list = achievement.users  
        users_list.append(user.id)  
        achievement.users = users_list
        achievement.save()
        user.achievements += 1
        user.save()

    if Achievements.objects.filter(name="100 Wins").exists():
        if user.id in Achievements.objects.get(name="100 Wins").users:
            hunWins = True

    if Achievements.objects.filter(name="Defcon1").exists():
        if user.id in Achievements.objects.get(name="Defcon1").users:
            defcon1 = True

    if Achievements.objects.filter(name="Cuba Rules").exists():
        if user.id in Achievements.objects.get(name="Cuba Rules").users:
            cubaRules = True

    if Achievements.objects.filter(name="Cuba Wins").exists():
        if user.id in Achievements.objects.get(name="Cuba Wins").users:
            cubaWins = True

    if Achievements.objects.filter(name="Rule the World").exists():
        if user.id in Achievements.objects.get(name="Rule the World").users:
            ruleTheWorld = True
        
    if request.method == "POST" and request.user == user:
        new_bio = request.POST.get('bio')
        if new_bio:
            user.bio = new_bio
            user.save()
            return redirect('profile', user_id=user_id)

    return render(request, 'AWSDefcon1App/profile.html', {
        'name': user.username,
        'user_id': user.id,
        'wins': user.wins,
        'achievements': user.achievements,
        'bio': user.bio,
        'is_owner': request.user == user,
        'hunWins':hunWins,
        'ruleTheWorld':ruleTheWorld,
        'cubaWins':cubaWins,
        'cubaRules':cubaRules,
        'defcon1':defcon1
    })
    
def creates(request):
  max_id = Games.objects.aggregate(max_id=Max('id'))['max_id']
  max_id += 1
  return render(request, "AWSDefcon1App/creates.html", {"max_id":max_id})



@login_required(login_url='login')
def announcemnts(request, game_id):
  announces = Announcements.objects.filter(game=game_id).order_by('-start_time')
  return render(request, "AWSDefcon1App/announcements.html", {"game_id": game_id,"announces" : announces})

@login_required  
def beg(request, game_id):
  PlayerAAA = Nations.objects.get(game=game_id, user=request.user)
  user = request.user
  alliance = Nations.objects.get(game = game_id, user = user).alliance_name 
  allies = Nations.objects.filter(game = game_id, alliance_name = alliance, player_number__gt=7)
  ally_num = len(allies)
  user = request.user
  player = Nations.objects.get(game = game_id, user = user)
  if request.method == 'POST':
    if player.requests < 1:
        return bad_request(request, title="User Error", message="You are out of diplomatic requests for the day. Please click the back button to return to the game")
        return HttpResponseBadRequest("You are out of diplomatic requests for the day. Please click the back button to return to the game")
    player.requests -= 1
    player.save()
    try:
        ally = allies[random.randint(0, ally_num-1)]
    except:
        ally = player
    type = random.randint(1,6)
    if type == 1:
      amount = random.randint(0,ally.divisions)
      ally.divisions -= amount
      ally.save()
      player.divisions += amount
      player.save()
      announcements = Announcements.objects.create(text =f"{player.name} has recived divisions from {ally.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
    if type == 2:
      amount = random.randint(0,ally.planes)
      ally.planes -= amount
      ally.save()
      player.planes += amount
      player.save()
      announcements = Announcements.objects.create(text =f"{player.name} has recived planes from {ally.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
    if type == 3:
      amount = random.randint(0,ally.boats)
      ally.boats -= amount
      ally.save()
      player.boats += amount
      player.save()
      announcements = Announcements.objects.create(text =f"{player.name} has recived boats from {ally.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
    if type == 4:
      amount = random.randint(0,ally.points)
      ally.points -= amount
      ally.save()
      player.points += amount
      player.save()
      announcements = Announcements.objects.create(text =f"{player.name} has recived points from {ally.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
    if type == 6:
      amount = random.randint(0,ally.spies)
      ally.spies -= amount
      ally.save()
      player.spies += amount
      player.save()
      announcements = Announcements.objects.create(text =f"{player.name} has recived spies from {ally.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
    if type == 5:
      if ally.nukes > 0:
        amount = random.randint(0,ally.nukes)
        ally.nukes -= amount
        ally.save()
        player.nukes += amount
        player.save()
        announcements = Announcements.objects.create(text =f"{player.name} has recived nukes from {ally.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
      else:
        times = 8 - ally.nuke_time
        ally.nuke_time += times
        ally.save()
        player.nuke_time -= times
        player.save()
        announcements = Announcements.objects.create(text =f"{player.name} has recived nuclear technology from {ally.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
          
    player = Nations.objects.get(game = game_id, user = user)
    user = request.user
    requesters = player.requests
    user = request.user.username
    # Get the player's nation
    playernation = Nations.objects.filter(game=game_id, user=request.user).first()
    knownnations = Nations.objects.filter(game=game_id, alliance_name=playernation.alliance_name)
    return HttpResponseRedirect(reverse('map', kwargs={'game_id': game_id}))
  player = Nations.objects.get(game = game_id, user = user)
  user = request.user
  requesters = player.requests
  nations = Nations.objects.filter(game=game_id)
  user = request.user.username
  # Get the player's nation
  playernation = Nations.objects.filter(game=game_id, user=request.user).first()
  knownnations = Nations.objects.filter(game=game_id, alliance_name=playernation.alliance_name)
  if playernation.alliance_name == "":
    knownnations =  Nations.objects.filter(game=game_id, user=request.user)
  return render(request, "AWSDefcon1App/beg.html", {"game_id": game_id, "requesters":requesters, "PlayerAAA":PlayerAAA, "knownnations":knownnations})

def index(request):
    games = Games.objects.all()
    user = request.user.username
    for game in games:
        gameMap = Map.objects.get(game = game)
        if Square.objects.filter(map = gameMap).count() < 902:
            game.delete()
        if Nations.objects.filter(name = 'United Kingdom', game = game).count() != 1:
            game.delete()

    if not Achievements.objects.exists():
        Achievements.objects.create(name = "Rule the World") #Own every state
        Achievements.objects.create(name = "Cuba Wins")#Win as Cuba
        Achievements.objects.create(name = "Cuba Rules")#Own Every state as Cuba
        Achievements.objects.create(name = "Defcon1")#Have more then 200 Nukes
        Achievements.objects.create(name = "100 Wins")#Have 100 wins

    for game in games:
      # Get the most recent announcement for the game
      most_recent_announcement = Announcements.objects.filter(game=game).order_by('-start_time').first()
      game_id = game.id
      # Check if there is a most recent announcement
      if most_recent_announcement:
          # Calculate the time difference between now and the announcement's start_time
          time_difference = timezone.now() - most_recent_announcement.start_time

          if time_difference > timedelta(hours=8):
            all_nations = Nations.objects.filter(game = game_id, player_number__lt = 8).exclude(user = User.objects.get(username = "loser")).exclude(user = User.objects.get(username = "empty")).exclude(user = User.objects.get(username = "closed"))
            nations = Nations.objects.filter(game = game_id)
            for nation in nations:
                states = nation.states
                mult = 1
                if states <= 20:
                    mult = 2
                elif states < 50:
                    mult = 1.7
                elif states < 150:
                    mult = 1.5
                elif states < 200:
                    mult = 1.4
                elif states < 250:
                    mult = 1

                nation.divisions = nation.divisions + states * mult
                nation.planes = nation.planes + states * 10
                nation.boats = nation.boats + states / 2
                nation.points += 1
                if nation.nuke_time <= 0:
                    nation.nukes += 1
                else:
                    nation.nuke_time -= 1
                nation.attacks = 5
                nation.requests = 10
                nation.save()
            Announcements.objects.create(text =f"The game has been refreshed due to inactivity", start_time = datetime.now(), game = Games.objects.get(id = game_id))

    loser_nations = Nations.objects.filter(player_number__lt=8, user__username="loser")
    for loser_nation in loser_nations:
        game = loser_nation.game
        if game:
            player_number_to_update = f"player{loser_nation.player_number}"
            setattr(game, player_number_to_update, User.objects.get(username = 'loser'))
            game.save()
    
    loser_nations = Nations.objects.filter(player_number__lt=8, user__username="closed")
    for loser_nation in loser_nations:
        game = loser_nation.game
        if game:
            player_number_to_update = f"player{loser_nation.player_number}"
            setattr(game, player_number_to_update, User.objects.get(username = 'closed'))
            game.save()

    if not User.objects.filter(username='Admin').exists():
        user = User.objects.create_superuser('Admin', 'randomdams@gmail.com', 'C0deClub')
        user.save()
        
    max_game_id = Games.objects.count()
    
    games = Games.objects.all()
    nationscount = 0
    for game in games:
        # Obtain the game_id for the current game
        game_id = game.id
        nations = Nations.objects.filter(game_id=game_id, player_number__lt=8)
        nationscount = 0
        for nation in nations:
            if nation.user.username == 'loser':
                nationscount += 1
                if nationscount == 6:
                    non_loser_nations = nations.exclude(user__username='loser')
                    for non_loser_nation in non_loser_nations:
                        if non_loser_nation.name == "Cuba":
                            if non_loser_nation.user.id not in Achievements.objects.get(name = "Cuba Wins").users:
                                achievement = Achievements.objects.get(name="Cuba Wins")
                                users_list = achievement.users  
                                users_list.append(non_loser_nation.user.id)  
                                achievement.users = users_list
                                achievement.save()

                                non_loser_nation.user.achievements += 1
                                non_loser_nation.user.save()
                        if non_loser_nation.states == 903 or non_loser_nation.states > 903:
                                if non_loser_nation.user.id not in Achievements.objects.get(name = "Rule the World").users:
                                    achievement = Achievements.objects.get(name="Rule the World")
                                    users_list = achievement.users  
                                    users_list.append(non_loser_nation.user.id)  
                                    achievement.users = users_list
                                    achievement.save()

                                    non_loser_nation.user.achievements += 1
                                    non_loser_nation.user.save()
                        if non_loser_nation.states == 903 or non_loser_nation.states > 903 and non_loser_nation.name == "Cuba" and non_loser_nation.user.id not in Achievements.objects.get(name = "Cuba Rules").users:
                            achievement = Achievements.objects.get(name="Cuba Rules")
                            users_list = achievement.users  
                            users_list.append(non_loser_nation.user.id)  
                            achievement.users = users_list
                            achievement.save()

                            non_loser_nation.user.achievements += 1
                            non_loser_nation.user.save()

                        non_loser_nation.user.wins += 1
                        if non_loser_nation.user.wins == 100 and non_loser_nation.user.id not in Achievements.objects.get(name = "100 Wins").users:
                            achievement = Achievements.objects.get(name="100 Wins")
                            users_list = achievement.users  
                            users_list.append(non_loser_nation.user.id)  
                            achievement.users = users_list
                            achievement.save()
                            
                            non_loser_nation.user.achievements += 1
                            non_loser_nation.user.save()

                        non_loser_nation.user.save()
                    game.delete()
                    name = non_loser_nation.user.username
                    current_date = datetime.now()
                    # Check if the date is December 25th
                    if current_date.month == 12 and current_date.day == 25:
                        # Render the Christmas win screen
                        return render(request, "AWSDefcon1App/christmaswinner.html", {"game_id": game_id, "name": name})
                    return render(request, "AWSDefcon1App/winner.html", {"game_id": game_id, "name":name})

                    
    next_id = 1
    all_games = Games.objects.all()
    lst = list(all_games.values_list('id', flat=True))

    if not lst:
        # If no game objects exist, start with ID 1
        next_id =  1

    # Step 2: Determine the range of IDs
    else:
        min_id = min(lst)
        max_id = max(lst)

        # Step 3: Find missing IDs
        missing_ids = [num for num in range(min_id, max_id + 1) if num not in lst]

        if missing_ids:
            # Step 4: Return the first missing ID
            next_id = missing_ids[0]
        else:
            # If no IDs are missing within the range, return the next available ID
            next_id = max_id + 1

    leaderboard = User.objects.filter(wins__gt=0).order_by('-wins').exclude(username ='closed').exclude(username ='empty').exclude(username ='loser')

    games  = Games.objects.all()
    played_games = []     
    for game in games:
        if is_user_in_game(game, request.user):
            played_games.append(game)


    games = played_games
    
    
    return render(request, "AWSDefcon1App/index.html", {"games": games, "user": user, "max_game_id":max_game_id,'next_id':next_id,'leaderboard': leaderboard})

def full_index(request):
    games = Games.objects.all()
    user = request.user.username
    for game in games:
        gameMap = Map.objects.get(game = game)
        if Square.objects.filter(map = gameMap).count() < 902:
            game.delete()
        if Nations.objects.filter(name = 'United Kingdom', game = game).count() != 1:
            game.delete()

    if not Achievements.objects.exists():
        Achievements.objects.create(name = "Rule the World") #Own every state
        Achievements.objects.create(name = "Cuba Wins")#Win as Cuba
        Achievements.objects.create(name = "Cuba Rules")#Own Every state as Cuba
        Achievements.objects.create(name = "Defcon1")#Have more then 200 Nukes
        Achievements.objects.create(name = "100 Wins")#Have 100 wins

    for game in games:
      # Get the most recent announcement for the game
      most_recent_announcement = Announcements.objects.filter(game=game).order_by('-start_time').first()
      game_id = game.id
      # Check if there is a most recent announcement
      if most_recent_announcement:
          # Calculate the time difference between now and the announcement's start_time
          time_difference = timezone.now() - most_recent_announcement.start_time

          if time_difference > timedelta(hours=8):
            all_nations = Nations.objects.filter(game = game_id, player_number__lt = 8).exclude(user = User.objects.get(username = "loser")).exclude(user = User.objects.get(username = "empty")).exclude(user = User.objects.get(username = "closed"))
            nations = Nations.objects.filter(game = game_id)
            for nation in nations:
                states = nation.states
                mult = 1
                if states <= 20:
                    mult = 2
                elif states < 50:
                    mult = 1.7
                elif states < 150:
                    mult = 1.5
                elif states < 200:
                    mult = 1.4
                elif states < 250:
                    mult = 1

                nation.divisions = nation.divisions + states * mult
                nation.planes = nation.planes + states * 10
                nation.boats = nation.boats + states / 2
                nation.points += 1
                if nation.nuke_time <= 0:
                    nation.nukes += 1
                else:
                    nation.nuke_time -= 1
                nation.attacks = 5
                nation.requests = 10
                nation.save()
            Announcements.objects.create(text =f"The game has been refreshed due to inactivity", start_time = datetime.now(), game = Games.objects.get(id = game_id))

    loser_nations = Nations.objects.filter(player_number__lt=8, user__username="loser")
    for loser_nation in loser_nations:
        game = loser_nation.game
        if game:
            player_number_to_update = f"player{loser_nation.player_number}"
            setattr(game, player_number_to_update, User.objects.get(username = 'loser'))
            game.save()
    
    loser_nations = Nations.objects.filter(player_number__lt=8, user__username="closed")
    for loser_nation in loser_nations:
        game = loser_nation.game
        if game:
            player_number_to_update = f"player{loser_nation.player_number}"
            setattr(game, player_number_to_update, User.objects.get(username = 'closed'))
            game.save()

    if not User.objects.filter(username='Admin').exists():
        user = User.objects.create_superuser('Admin', 'randomdams@gmail.com', 'C0deClub')
        user.save()
        
    max_game_id = Games.objects.count()
    
    games = Games.objects.all()
    nationscount = 0
    for game in games:
        # Obtain the game_id for the current game
        game_id = game.id
        nations = Nations.objects.filter(game_id=game_id, player_number__lt=8)
        nationscount = 0
        for nation in nations:
            if nation.user.username == 'loser':
                nationscount += 1
                if nationscount == 6:
                    non_loser_nations = nations.exclude(user__username='loser')
                    for non_loser_nation in non_loser_nations:
                        if non_loser_nation.name == "Cuba":
                            if non_loser_nation.user.id not in Achievements.objects.get(name = "Cuba Wins").users:
                                achievement = Achievements.objects.get(name="Cuba Wins")
                                users_list = achievement.users  
                                users_list.append(non_loser_nation.user.id)  
                                achievement.users = users_list
                                achievement.save()

                                non_loser_nation.user.achievements += 1
                                non_loser_nation.user.save()
                        if non_loser_nation.states == 903 or non_loser_nation.states > 903:
                                if non_loser_nation.user.id not in Achievements.objects.get(name = "Rule the World").users:
                                    achievement = Achievements.objects.get(name="Rule the World")
                                    users_list = achievement.users  
                                    users_list.append(non_loser_nation.user.id)  
                                    achievement.users = users_list
                                    achievement.save()

                                    non_loser_nation.user.achievements += 1
                                    non_loser_nation.user.save()
                        if non_loser_nation.states == 903 or non_loser_nation.states > 903 and non_loser_nation.name == "Cuba" and non_loser_nation.user.id not in Achievements.objects.get(name = "Cuba Rules").users:
                            achievement = Achievements.objects.get(name="Cuba Rules")
                            users_list = achievement.users  
                            users_list.append(non_loser_nation.user.id)  
                            achievement.users = users_list
                            achievement.save()

                            non_loser_nation.user.achievements += 1
                            non_loser_nation.user.save()

                        non_loser_nation.user.wins += 1
                        if non_loser_nation.user.wins == 100 and non_loser_nation.user.id not in Achievements.objects.get(name = "100 Wins").users:
                            achievement = Achievements.objects.get(name="100 Wins")
                            users_list = achievement.users  
                            users_list.append(non_loser_nation.user.id)  
                            achievement.users = users_list
                            achievement.save()
                            
                            non_loser_nation.user.achievements += 1
                            non_loser_nation.user.save()

                        non_loser_nation.user.save()
                    game.delete()
                    name = non_loser_nation.user.username
                    current_date = datetime.now()
                    # Check if the date is December 25th
                    if current_date.month == 12 and current_date.day == 25:
                        # Render the Christmas win screen
                        return render(request, "AWSDefcon1App/christmaswinner.html", {"game_id": game_id, "name": name})
                    return render(request, "AWSDefcon1App/winner.html", {"game_id": game_id, "name":name})

                    
    next_id = 1
    all_games = Games.objects.all()
    lst = list(all_games.values_list('id', flat=True))

    if not lst:
        # If no game objects exist, start with ID 1
        next_id =  1

    # Step 2: Determine the range of IDs
    else:
        min_id = min(lst)
        max_id = max(lst)

        # Step 3: Find missing IDs
        missing_ids = [num for num in range(min_id, max_id + 1) if num not in lst]

        if missing_ids:
            # Step 4: Return the first missing ID
            next_id = missing_ids[0]
        else:
            # If no IDs are missing within the range, return the next available ID
            next_id = max_id + 1

    leaderboard = User.objects.filter(wins__gt=0).order_by('-wins').exclude(username ='closed').exclude(username ='empty').exclude(username ='loser')

    games  = Games.objects.all()
    played_games = []     
    for game in games:
        if not is_user_in_game(game, request.user):
            played_games.append(game)


    games = played_games
    
    
    return render(request, "AWSDefcon1App/full_index.html", {"games": games, "user": user, "max_game_id":max_game_id,'next_id':next_id,'leaderboard': leaderboard})


def is_user_in_game(game, user):
    # Check if request.user matches any of the player fields
    return any([
        game.player0 == user,
        game.player1 == user,
        game.player2 == user,
        game.player3 == user,
        game.player4 == user,
        game.player5 == user,
        game.player6 == user,
        game.player7 == user,
    ])

@login_required(login_url='login')
def unread_senders(request):
    unread_game_messages = (
        Message.objects.filter(receiver=request.user, read=False)
        .values('sender', 'game_id')  # Group by sender and game_id
        .annotate(unread_count=Count('id'))  # Count unread messages
    )

    # Unread messages in the DM model
    unread_dms = (
        DM.objects.filter(receiver=request.user, read=False)
        .values('sender')  # Group by sender (no game_id for DMs)
        .annotate(unread_count=Count('id'))
    )

    # Pass both lists to the template
    context = {
        'unread_game_messages': unread_game_messages,
        'unread_dms': unread_dms,
    }
    return render(request, 'AWSDefcon1App/unreadmessages.html', context)

@login_required(login_url='login')
def game_maker_redirrect(request):
    next_id = 1
    all_games = Games.objects.all()
    lst = list(all_games.values_list('id', flat=True))

    if not lst:
        # If no game objects exist, start with ID 1
        next_id =  1

    # Step 2: Determine the range of IDs
    else:
        min_id = min(lst)
        max_id = max(lst)

        # Step 3: Find missing IDs
        missing_ids = [num for num in range(min_id, max_id + 1) if num not in lst]

        if missing_ids:
            # Step 4: Return the first missing ID
            next_id = missing_ids[0]
        else:
            # If no IDs are missing within the range, return the next available ID
            next_id = max_id + 1
    make_game = True
    return render(request, "AWSDefcon1App/makegame.html", {"game_id":next_id, "make_game":make_game})

    

@login_required(login_url='login')
def game(request, game_id):

    non_loser_nation = Nations.objects.get(game = game_id, user = request.user)
    if non_loser_nation.nukes == 200 or non_loser_nation.nukes > 200 and non_loser_nation.user.id not in Achievements.objects.get(name = "Defcon1").users:
        achievement = Achievements.objects.get(name="Defcon1")
        users_list = achievement.users  
        users_list.append(non_loser_nation.user.id)  
        achievement.users = users_list
        achievement.save()

        non_loser_nation.user.achievements += 1
        non_loser_nation.user.save()

    nations = Nations.objects.filter(game=game_id)
    for nation in nations:
        if nation.friendlyness == 0 or nation.friendlyness < 1:
            nation.friendlyness = 1
    user = request.user.username
    # Get the player's nation
    playernation = Nations.objects.filter(game=game_id, user=request.user).first()
    if playernation and playernation.alliance_name:
        knownnations = Nations.objects.filter(game=game_id, alliance_name=playernation.alliance_name)
    else:
        knownnations = [playernation] if playernation else []

    allies = Nations.objects.filter(game = game_id , alliance_name = playernation)
    wars = War.objects.filter(nation1__game=game_id) | War.objects.filter(nation2__game=game_id)
    return render(request, "AWSDefcon1App/game.html", {"nations": nations, "user": user, "game_id": game_id, "knownnations":knownnations, "wars":wars, "allies":allies, "playernation":playernation})
  

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "AWSDefcon1App/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "AWSDefcon1App/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = "noemail@email.com"
        if len(username) > 30:
          return render(request, "AWSDefcon1App/register.html", {
                "message": "Username too long"
            })
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "AWSDefcon1App/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "AWSDefcon1App/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("full_index"))
    else:
        return render(request, "AWSDefcon1App/register.html")
    
#from background_task import background
#@background(schedule=timedelta(days=1))  
@staff_member_required
def new(request, game_id):
    if request.method == 'POST':
        all_nations = Nations.objects.filter(game = game_id)
        i = 0
        j = 0
        for nation in all_nations:
            states = nation.states
            mult = 0.1
            if states <= 20:
                mult = 4
            elif states < 50:
                mult = 2
            elif states < 100:
                mult = 1
            elif states < 200:
                mult = 0.5
            elif states < 250:
                mult = 0.25

            nation.divisions = nation.divisions + states * mult
            nation.planes = nation.planes + states * 10
            nation.boats = nation.boats + states / 2
            nation.points += 1
            nation.attacks = 2
            if nation.nuke_time <= 0:
                nation.nukes += 1
            else:
                nation.nuke_time -= 1
            nation.save()
    return render(request, "AWSDefcon1App/new.html", {'game_id': game_id})




@login_required(login_url='login')
def focus(request, game_id):
    PlayerAAA = Nations.objects.get(game=game_id, user=request.user)
    if request.method == 'POST':
          player = Nations.objects.get(game = game_id, user = request.user)
          if player.points <= 0:
              return bad_request(request, title="User Error", message="You don't have enough focus points to do that. Please click the back button to return to the game")
              return HttpResponseBadRequest("You don't have enough focus points to do that. Please click the back button to return to the game")
          army = request.POST.get("army")
          air = request.POST.get("air")
          navy = request.POST.get("navy")
          nuke = request.POST.get("nuke")
          spies = request.POST.get("spies")
          policy = request.POST.get("policy")
          if spies:
              player.points -= 1
              player.spies += 1
          if army:
              player.points -= 1
              player.divisions += 80
          if navy:
              player.points -= 1
              player.boats += 60
          if air:
              player.points -= 1
              player.planes += 1000
          if nuke:
              if player.points < 2:
                  return bad_request(request, title="User Error", message="You don't have enough focus points to do that. Please click the back button to return to the game")
                  return HttpResponseBadRequest("You don't have enough focus points to do that. Please click the back button to return to the game")
              player.points -= 2
              player.nuke_time -= 1
              if player.nuke_time <= 0:
                  player.nukes += 1
                  player.nuke_time += 1
                  player.save()
          if policy:
              if player.points < 2:
                  return bad_request(request, title="User Error", message="You don't have enough focus points to do that. Please click the back button to return to the game")
                  return HttpResponseBadRequest("You don't have enough focus points to do that. Please click the back button to return to the game")
              player.points -= 2
              war = War.objects.filter(nation1 = player).delete()
              war = War.objects.filter(nation2 = player).delete()
              player.alliance_name = ''
          player.save()
    player = Nations.objects.get(game = game_id, user = request.user)
    points = player.points
    return HttpResponseRedirect(reverse('map', kwargs={'game_id': game_id}))

def spies(request, game_id):
    PlayerAAA = Nations.objects.get(game=game_id, user=request.user)
    if request.method == 'POST':
        get = request.POST.get("get")
        army = request.POST.get("army")
        air = request.POST.get("air")
        navy = request.POST.get("navy")
        nuke = request.POST.get("nuke")
        coup = request.POST.get("coup")
        civil = request.POST.get("civil")
        kill = request.POST.get("kill")

        target = request.POST.get("target")
        enemy = Nations.objects.get(game = game_id, name = target)
        player = Nations.objects.get(game = game_id, user = request.user)
        if player.requests < 1:
            return bad_request(request, title="User Error", message="You are out of diplomatic requests for the day. Please click the back button to return to the game")
            return HttpResponseBadRequest("You are out of diplomatic requests for the day. Please click the back button to return to the game")
        if enemy.spies < 1:
            nations = Nations.objects.filter(game = game_id).exclude(user = User.objects.get(username = "loser")).exclude(user = request.user)
            requesters = player.requests
            return HttpResponseRedirect(reverse('map', kwargs={'game_id': game_id}))
        if get:
            chance = player.spies/((enemy.spies * 1) + 1)
            if chance > 0.75:
                chance = 0.75
            chance = chance * 100
            rand = random.randint(1,100)
            if rand < chance or rand == chance:
                player.spies += 1
                enemy.spies -= 1
                announcements = Announcements.objects.create(text =f"A spy from {enemy.name} has turned to join {player.name}'s nation", start_time = datetime.now(), game = Games.objects.get(id = game_id))
            else:
                player.spies -= 1
                player.save()
                announcements = Announcements.objects.create(text =f"A spy from {player.name} has been caught and executed by {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
        if army:
            chance = player.spies/((enemy.spies * 2) + 1)
            if chance > 0.75:
                chance = 0.75
            chance = chance * 100
            rand = random.randint(1,100)
            if rand < chance or rand == chance:
                if enemy.divisions > 0:
                    enemy.divisions -= random.randint(0, enemy.divisions)
                    announcements = Announcements.objects.create(text =f"A spy from {player.name} has sabotaged the army of {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
            else:
                player.spies -= 1
                player.save()
                announcements = Announcements.objects.create(text =f"A spy from {player.name} has been caught and executed by {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
        if navy:
            chance = player.spies/((enemy.spies * 2) + 1)
            if chance > 0.75:
                chance = 0.75
            chance = chance * 100
            rand = random.randint(1,100)
            if rand < chance or rand == chance:
                if enemy.boats > 0:
                    enemy.boats -= random.randint(0, enemy.boats)
                    announcements = Announcements.objects.create(text =f"A spy from {player.name} has sabotaged the navy of {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
            else:
                player.spies -= 1
                player.save()
                announcements = Announcements.objects.create(text =f"A spy from {player.name} has been caught and executed by {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
        if air:
            chance = player.spies/((enemy.spies * 2) + 1)
            if chance > 0.75:
                chance = 0.75
            chance = chance * 100
            rand = random.randint(1,100)
            if rand < chance or rand == chance:
                if enemy.planes > 0:
                    enemy.planes -= random.randint(0, enemy.planes)
                    announcements = Announcements.objects.create(text =f"A spy from {player.name} has sabotaged the air force of {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
            else:
                player.spies -= 1
                player.save()
                announcements = Announcements.objects.create(text =f"A spy from {player.name} has been caught and executed by {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
        if nuke:
            chance = player.spies/((enemy.spies * 2) + 1)
            if chance > 0.75:
                chance = 0.75
            chance = chance * 100
            rand = random.randint(1,100)
            if rand < chance or rand == chance:
                if player.nuke_time > 0:
                    player.nuke_time -= 1
                else:
                    player.nukes += 1
                    announcements = Announcements.objects.create(text =f"A spy from {player.name} has stole technology of {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
            else:
                player.spies -= 1
                player.save()         
                announcements = Announcements.objects.create(text =f"A spy from {player.name} has been caught and executed by {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
        if coup:
            chance = player.spies/((enemy.spies * 3) + 1)
            if chance > 0.75:
                chance = 0.75
            chance = chance * 100
            rand = random.randint(1,100)
            if rand < chance or rand == chance:
                squares = Square.objects.filter(map = Map.objects.get(game = game_id), owner = enemy)
                if squares.count() == 1:
                    pass
                else:
                    random_square = random.choice(squares)
                    random_square.owner = player
                    random_square.color = colors.get(player.name)
                    player.states += 1
                    random_square.save()
                    player.save()
                    announcements = Announcements.objects.create(text =f"A spy from {player.name} has created a small revolt in {random_square.name},{enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
            else:
                player.spies -= 1
                player.save()
                announcements = Announcements.objects.create(text =f"A spy from {player.name} has been caught and executed by {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
        if kill:
            chance = player.spies/((enemy.spies * 2) + 1)
            if chance > 0.75:
                chance = 0.75
            chance = chance * 100
            rand = random.randint(1,100)
            if rand < chance or rand == chance:
                if enemy.spies > 0:
                    enemy.spies -= 1
                announcements = Announcements.objects.create(text =f"A spy from {enemy.name} has been caught and executed by {player.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
            else:
                player.spies -= 1
                player.save()
                announcements = Announcements.objects.create(text =f"A spy from {player.name} has been caught and executed by {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
        if civil:
            chance = player.spies/((enemy.spies * 4) + 1)
            if chance > 0.75:
                chance = 0.75
            chance = chance * 100
            rand = random.randint(1,100)
            if rand < chance or rand == chance:
                    squares = Square.objects.filter(map = Map.objects.get(game = game_id), owner = enemy)
                    square_list = list(squares)    
                    random.shuffle(square_list)
                    half_count = len(square_list) // 2
                    random_half_squares = square_list[:half_count]
                    for square in random_half_squares:
                        square.owner = player
                        square.color = colors.get(player.name)
                        player.states += 1
                        enemy.states -= 1
                        enemy.save()
                        square.save()
                        player.save()
                        announcements = Announcements.objects.create(text =f"{player.name} started a civil war in {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))                             
            else:
                player.spies = 0
                announcements = Announcements.objects.create(text =f"All spies from {player.name} has been caught and executed by {enemy.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))        
        player.requests -= 1
        player.save()
        enemy.save()

    player = Nations.objects.get(game = game_id, user = request.user)
    nations = Nations.objects.filter(game = game_id).exclude(user = User.objects.get(username = "loser")).exclude(user = request.user)
    points = player.points
    requesters = player.requests
    if player.spies < 0:
        player.spies = 0
        player.save()
    return HttpResponseRedirect(reverse('map', kwargs={'game_id': game_id}))

@login_required(login_url='login')
def join(request, game_id, player_number):
    game = get_object_or_404(Games, id=game_id)

    if request.method == 'POST' or request.method == 'GET':
        player_field = f"player{player_number}"

        # Check if the player already has a spot in any player field
        existing_player_field = None
        for i in range(0, 8):
            field_name = f"player{i}"
            player = getattr(game, field_name)
            if player == request.user:
                existing_player_field = field_name
                break

        # Remove the player from the existing spot if any
        try:
            setattr(game, existing_player_field,User.objects.get(username='empty'))
            nation = Nations.objects.get(game=game, user=request.user)
            nation.user = User.objects.get(username='empty')  # Replace 'name' with the field you want to update
            nation.save()
        except:
            pass

        setattr(game, player_field, request.user)
        game.save()
        # Update the Nations model
        nation, created = Nations.objects.get_or_create(game=game, player_number=player_number)
        nation.user = request.user
        nation.save()
        return HttpResponseRedirect(reverse('map', kwargs={'game_id': game_id}))
    
    make_game = True
    return render(request, 'AWSDefcon1App/join.html', {'game_id': game_id, 'player_number': player_number, 'make_game':make_game})

@login_required(login_url='login')
def battle(request, game_id):
    # Prefetch related objects early to avoid redundant queries
    game = Games.objects.select_related().get(id=game_id)
    map_instance = Map.objects.select_related().get(game=game)

    # Use select_related to fetch Nations efficiently
    owner = Nations.objects.select_related('user', 'game').get(game=game, user=request.user)
    PlayerAAA = owner  # same as owner for now
    attacks_left = owner.attacks

    # Get all wars involving the owner in one query
    wars = War.objects.filter(Q(nation1=owner) | Q(nation2=owner)).select_related('nation1', 'nation2')
    nations_at_war = {
        war.nation2 if war.nation1 == owner else war.nation1
        for war in wars
    }

    # Fetch owned squares in one efficient query
    owned_squares = Square.objects.filter(owner=owner, map=map_instance).only('number')
    controlled_squares = [square.number for square in owned_squares]

    # Determine bordering square numbers
    border_offsets = [1, -1, 69, -69]
    border_squares = {
        square_num + offset
        for square_num in controlled_squares
        for offset in border_offsets
    } - set(controlled_squares)

    # Get bordering nation owners from those bordering squares
    bordering_owners = Square.objects.filter(number__in=border_squares).values_list('owner', flat=True)
    bordering_nations = set(Nations.objects.filter(name__in=bordering_owners))
    borders_at_war = bordering_nations & nations_at_war

    if request.method == 'GET':
        return render(request, 'AWSDefcon1App/battles.html', {
            'game_id': game_id,
            'PlayerAAA': PlayerAAA,
            'borders_at_war': borders_at_war,
            'nations_at_war': nations_at_war,
            'attacks_left': attacks_left,
            'owner': owner
        })

    elif request.method == 'POST':
        if attacks_left <= 0:
            return bad_request(request, title="User Error", message= "You have already fought all your battles for the day. Please click the back button to return to the game")
            return HttpResponseBadRequest("You have already fought all your battles for the day. Please click the back button to return to the game")
            
        changed_squares = []
        owner.attacks -= 1
        owner.save()
        
        boat_defender = request.POST.get('defender')
        planes_defender = request.POST.get('defender')
        division_defender = request.POST.get('defender')
        action = request.POST.get('action')
        defender_name = request.POST.get('defender')

        division_attack_type = ""
        planes_attack_type = ""
        boat_attack_type = ""
        nuke_defender = ""
        division_attack_amount = None
        planes_attack_amount = None
        boat_attack_amount = None

        # Determine attack types and amounts
        if action == 'Ndivision':
            division_attack_type = "normal"
            division_attack_amount = 9999999999
        elif action == 'Nplanes':
            planes_attack_type = "normal"
            planes_attack_amount = 99999999999
        elif action == 'Nboat':
            boat_attack_type = "normal"
            boat_attack_amount = 9999999999
        elif action == 'division':
            division_attack_type = "encirclement"
            division_attack_amount = 9999999999
        elif action == 'planes':
            planes_attack_type = "bombing"
            planes_attack_amount = 99999999999
        elif action == 'boat':
            boat_attack_type = "amphibious"
            boat_attack_amount = 9999999999
        elif action == 'nuke':
            planes_attack_amount = 99999999999
            nuke_defender = defender_name
        elif action == 'Bplanes':
            planes_attack_type = "Bbombing"
            planes_attack_amount = 99999999999

        # Defensive unit counts with safe fallbacks
        def get_defense_units(name, field):
            try:
                return getattr(Nations.objects.get(game=game_id, name=name), field)
            except Nations.DoesNotExist:
                return 0

        division_defend_amount = get_defense_units(defender_name, 'divisions')
        planes_defend_amount = get_defense_units(defender_name, 'planes')
        boat_defend_amount = get_defense_units(defender_name, 'boats')
        
        if boat_attack_amount:
            if int(boat_attack_amount) > Nations.objects.get(game=game_id, user=request.user).boats:
                boat_attack_amount = Nations.objects.get(game=game_id, user=request.user).boats 
            ogab = int(boat_attack_amount)
            ogdb = int(boat_defend_amount)
            if boat_attack_type == "normal":
                owner = Nations.objects.get(game=Games.objects.get(id = game_id), user=request.user)
                announcements = Announcements.objects.create(text =f"{owner.name} has fought a naval battle with {boat_defender}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
                chance = random.randint(1, 20)
                if chance > 1 and chance < 20:
                    boat_defend_amount = int(ogdb) - int(ogab)*0.3
                elif chance == 1:
                    boat_defend_amount = int(ogdb) - int(ogab)*0.9
                elif chance == 20:
                    boat_defend_amount = int(ogdb) - int(ogab)*0.1
                chance = random.randint(1, 20)
                if chance > 1 and chance < 20:
                    boat_attack_amount = int(ogab) - int(ogdb)*0.3
                elif chance == 1:
                    boat_attack_amount = int(ogab) - int(ogdb)*0.9
                elif chance == 20:
                    boat_attack_amount = int(ogab) - int(ogdb)*0.1

                boat_attackers_lost = ogab - int(boat_attack_amount)
                boat_defenders_lost =  ogdb - int(boat_defend_amount)
                nation_attacker = Nations.objects.get(game=game_id, user=request.user) 
                nation_defender = Nations.objects.get(game = game_id, name = boat_defender)
                nation_attacker.boats -= boat_attackers_lost
                nation_defender.boats -= boat_defenders_lost
                if nation_attacker.boats < 0:
                    nation_attacker.boats = 0
                if nation_defender.boats < 0:
                    nation_defender.boats = 0
                nation_attacker.save()
                nation_defender.save()
                

            if boat_attack_type == "amphibious":
                owner = owner.name
                if ogab > ogdb:
                    announcements = Announcements.objects.create(text =f"{owner} has landed on the beaches of {boat_defender}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
                    O_border_squares = Square.objects.filter(map = Map.objects.get(game=game_id), coastal = True, owner = Nations.objects.get(game = game_id, name = boat_defender))
                    length  = len(O_border_squares) - 1
                    try:
                        fallen_state = O_border_squares[random.randint(1, length)]
                    except:
                        try:
                            fallen_state = O_border_squares[0]
                        except:
                            owners = Nations.objects.get(game=game_id, user = request.user)
                            owners.attacks += 1
                            owners.save()
                            return bad_request(request, title="User Error", message= "Boats can't reach! There doesn't seem to be a way for your boats to reach you're enemy.  A battle wasn't used as you didn't know! Please click the back button to return to the game")
                            return HttpResponseBadRequest("No Water to Invade! (This could be a mistake so try again, don't wory your battle wasn't used)  Please click the back button to return to the game")

                            
                    fallen_state.owner = Nations.objects.get(game=game_id, user=request.user)
                    owner = Nations.objects.get(game=game_id, user=request.user)
                    color = colors.get(owner.name)
                    fallen_state.color = color
                    fallen_state.save()
                    changed_squares.append(fallen_state)
                    player = Nations.objects.get(game=game_id, user=request.user)
                    defender = Nations.objects.get(game = game_id, name = boat_defender)
                    player.states += 1
                    defender.states -= 1
                    player.save()
                    defender.save()

                else:
                    announcements = Announcements.objects.create(text =f"{owner} has failed to land on the beaches of {boat_defender}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
                    chance = random.randint(1, 20)
                    if chance > 1 and chance < 20:
                        boat_attack_amount = int(boat_attack_amount) - int(boat_defend_amount)*0.3
                    elif chance == 1:
                        boat_attack_amount = int(boat_attack_amount) - int(boat_defend_amount)*0.9
                    elif chance == 20:
                        boat_attack_amount = int(boat_attack_amount) - int(boat_defend_amount)*0.1


        
        if planes_attack_amount:
            owner = owner.name
            if int(planes_attack_amount) > Nations.objects.get(game=game_id, user=request.user).planes:
                planes_attack_amount = Nations.objects.get(game=game_id, user=request.user).planes 
            ogap = int(planes_attack_amount)
            ogdp = int(planes_defend_amount)
            if planes_attack_type == "bombing":
                announcements = Announcements.objects.create(text =f"{owner} has sent a bombing raid over {planes_defender}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
                change = ogap//1000
                enemy = Nations.objects.get(game = game_id, name = planes_defender)
                enemy.divisions -= change
                if enemy.divisions < 0:
                    enemy.divisions = 0
                enemy.save()
            elif planes_attack_type == "normal":
                chance = random.randint(1, 20)
                if chance > 1 and chance < 20:
                    planes_defend_amount = int(ogdp) - int(ogap)*0.3
                elif chance == 1:
                    planes_defend_amount = int(ogdp) - int(ogap)*0.9
                elif chance == 20:
                    planes_defend_amount = int(ogdp) - int(ogap)*0.1
                chance = random.randint(1, 20)
                if chance > 1 and chance < 20:
                    planes_attack_amount = int(ogap) - int(ogdp)*0.3
                elif chance == 1:
                    planes_attack_amount = int(ogap) - int(ogdp)*0.9
                elif chance == 20:
                    planes_attack_amount = int(ogap) - int(ogdp)*0.1

                planes_attackers_lost = ogap - int(planes_attack_amount)
                planes_defenders_lost =  ogdp - int(planes_defend_amount)
                nation_attacker = Nations.objects.get(game=game_id, user=request.user) 
                nation_defender = Nations.objects.get(game = game_id, name = planes_defender)
                announcements = Announcements.objects.create(text =f"{owner} has sent planes to fight {planes_defender}", start_time = datetime.now(), game = Games.objects.get(id = game_id))

                nation_attacker.planes -= planes_attackers_lost
                nation_defender.planes -= planes_defenders_lost  
                if nation_attacker.planes < 0:
                    nation_attacker.planes = 0
                if nation_defender.planes < 0:
                    nation_defender.planes = 0
                nation_attacker.save()
                nation_defender.save()
            
            elif planes_attack_type == "Bbombing":
              try:
                boat_defend_amount = Nations.objects.get(game = game_id, name = boat_defender).boats
              except:
                boat_defend_amount = 0
              
              ogdb = int(boat_defend_amount)
              chance = random.randint(1, 20)
              if chance > 1 and chance < 20:
                  planes_defend_amount = int(ogdb) - int(ogap)*0.003
              elif chance == 1:
                  planes_defend_amount = int(ogdb) - int(ogap)*0.009
              elif chance == 20:
                  planes_defend_amount = int(ogdb) - int(ogap)*0.001
              chance = random.randint(1, 20)
              if chance > 1 and chance < 20:
                  planes_attack_amount = int(ogap) - int(ogdb)*3
              elif chance == 1:
                  planes_attack_amount = int(ogap) - int(ogdb)*10
              elif chance == 20:
                  planes_attack_amount = int(ogap) - int(ogdb)*1

              planes_attackers_lost = ogap - int(planes_attack_amount)
              boats_defenders_lost =  ogdb - int(boat_defend_amount)
              nation_attacker = Nations.objects.get(game=game_id, user=request.user) 
              nation_defender = Nations.objects.get(game = game_id, name = planes_defender)
              announcements = Announcements.objects.create(text =f"{owner} has sent planes to fight {planes_defender}'s boats'", start_time = datetime.now(), game = Games.objects.get(id = game_id))

              nation_attacker.planes -= planes_attackers_lost
              nation_defender.boats -= boats_defenders_lost  
              if nation_attacker.planes < 0:
                  nation_attacker.planes = 0
              if nation_defender.boats < 0:
                  nation_defender.boats = 0
              nation_attacker.save()
              nation_defender.save()

        
        if nuke_defender:
            try:
                ogap = int(planes_attack_amount)
                ogdp = int(planes_defend_amount)
            except:
                return bad_request(request, title="User Error", message= "You need to send planes in either a dog fight or bombing raid. Please click the back button to return to the game")
                return HttpResponseBadRequest("You need to send planes in either a dog fight or bombing raid. Please click the back button to return to the game")
            planes_defender = request.POST.get('defender')
            
            if ogap > ogdp:
                enemy = Nations.objects.get(game=game_id, name=nuke_defender)
                player = Nations.objects.get(game=game_id, user=request.user)
                nuke_amount = player.nukes
                player.nukes = nuke_amount - 1
                player.save()
                nuked = enemy.nuked
                enemy.nuked = nuked + 1
                enemy.save()
                nuked = nuked + 1
                announcements = Announcements.objects.create(text =f"{owner} has used nuclear weapons against {planes_defender}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
                number = enemy.player_number
                enemy_player_number = f"player{number}"
               
                numerator = math.log(enemy.states / 10)
                denominator = math.log(1.5)
                result = numerator / denominator

                if nuked == result or nuked > result:
                    player.boats += enemy.boats
                    player.planes += enemy.planes
                    player.states += enemy.states
                    enemy.states = 0
                    enemy.boats = 0
                    enemy.planes = 0
                    enemy.user = User.objects.get(username='loser')
                    enemy.divisions = 0
                    enemy.alliance_name = ''
                    maper = Map.objects.get(number=game_id, game = Games.objects.get(id=game_id))
                    number = enemy.player_number
                    enemy_player_number = f"player{number}"
                    enemy_squares = Square.objects.filter(map=maper, owner=enemy)
                    game_instance = Games.objects.get(id=game_id)
                    game_instance.enemy_player_number = User.objects.get(username='loser')
                    game_instance.save()
                    for square in enemy_squares:
                        square.owner = player
                        color = colors.get(player.name)
                        square.color = color
                        square.save()
                    enemy.save()
                    player.save()
                    War.objects.filter(Q(nation1=enemy) | Q(nation2=enemy)).delete()

        if division_attack_amount:
            # Fetch attacker and defender nations only once
            attacker_nation = Nations.objects.get(game=game_id, user=request.user)
            defender_nation = Nations.objects.get(game=game_id, name=division_defender)

            # Clamp attack amount to available divisions
            oga = min(int(division_attack_amount), attacker_nation.divisions)
            ogd = defender_nation.divisions

            chance = random.randint(1, 20)

            if division_attack_type == "normal":
                if 1 < chance < 20:
                    division_defend_amount = ogd - int(oga * 0.3)
                elif chance == 1:
                    division_defend_amount = ogd - int(oga * 0.9)
                elif chance == 20:
                    division_defend_amount = ogd - int(oga * 0.1)
                division_attack_amount = oga  # No attacker loss in normal attack

            elif division_attack_type == "encirclement":
                if chance > 10:
                    division_defend_amount = ogd - int(oga * 0.9)
                    division_attack_amount = oga - int(ogd * 0.1)
                else:
                    division_defend_amount = ogd - int(oga * 0.1)
                    division_attack_amount = oga - int(ogd * 0.9)

            # Clamp to zero if negative
            division_defend_amount = max(0, division_defend_amount)
            division_attack_amount = max(0, division_attack_amount)

            # Calculate state changes
            state_changeA = (oga - division_attack_amount) // 10
            state_changeD = (ogd - division_attack_amount) // 10

            
            ## Offensive Wins 
            if state_changeD < state_changeA:
                state_change = min(state_changeA - state_changeD, 15)

                owner = Nations.objects.select_related("game").get(game=game_id, user=request.user)
                defender = Nations.objects.get(game=game_id, name=division_defender)
                game = Games.objects.only("id").get(id=game_id)
                map_obj = Map.objects.only("id").get(game=game)

                owner_alliance = owner.alliance_name

                # If the defender is in an alliance, get all nations in the same alliance (excluding empty/closed/loser if needed)
                if owner_alliance:
                    allies = Nations.objects.filter(game=game_id, alliance_name=owner_alliance)
                else:
                    # Defender is not in an alliance — only they count as their own ally
                    allies = Nations.objects.filter(pk=owner.pk)

                # Now fetch all squares owned by these allies
                owned_squares = Square.objects.filter(owner__in=allies, map=map_obj).only("number") 
                controlled_numbers = set(sq.number for sq in owned_squares)

                # Pre-fetch all neighbor squares to reduce queries
                all_squares = Square.objects.filter(map=map_obj).only("number", "owner", "color", "neighbors")
                square_dict = {sq.number: sq for sq in all_squares}

                captured = 0
                max_iterations = len(controlled_numbers) * 2  # Same logic as stater = states * 2
                iterations = 0
                attacker_color = colors.get(owner.name)

                for num in controlled_numbers:
                    if iterations > max_iterations or captured >= state_change:
                        break

                    square = square_dict.get(num)
                    if not square or not square.neighbors:
                        continue

                    for neighbor_num in square.neighbors:
                        neighbor = square_dict.get(neighbor_num)
                        if not neighbor or neighbor.owner_id != defender.id:
                            continue

                        # Capture square
                        neighbor.owner = owner
                        neighbor.color = attacker_color
                        changed_squares.append(neighbor)
                        neighbor.save()

                        # Adjust nation stats
                        owner.states += 1
                        defender.states -= 1
                        captured += 1

                        if captured >= state_change:
                            break

                    iterations += 1


            ## Defensive Wins
            elif state_changeD >= state_changeA:
                game = Games.objects.only("id").get(id=game_id)
                map_obj = Map.objects.only("id").get(game=game)

                defender = Nations.objects.select_related("game").get(game=game_id, name=division_defender)
                attacker = Nations.objects.get(game=game_id, user=request.user)

                # Precompute state-change attempts
                max_swaps = 10
                stater = defender.states * 3

                # Squares owned by defender
                defender_alliance = defender.alliance_name

                # If the defender is in an alliance, get all nations in the same alliance (excluding empty/closed/loser if needed)
                if defender_alliance:
                    allies = Nations.objects.filter(game=game_id, alliance_name=defender_alliance)
                else:
                    # Defender is not in an alliance — only they count as their own ally
                    allies = Nations.objects.filter(pk=defender.pk)

                # Now fetch all squares owned by these allies
                owned_squares = Square.objects.filter(owner__in=allies, map=map_obj).only("number")                
                controlled_numbers = set(sq.number for sq in owned_squares)

                # Pre-fetch all relevant squares
                all_squares = Square.objects.filter(map=map_obj).only("number", "owner", "color", "neighbors")
                square_dict = {sq.number: sq for sq in all_squares}

                attacker_name = attacker.name
                defender_color = colors.get(defender.name)

                swapped = 0
                iterations = 0

                for num in controlled_numbers:
                    if iterations > stater or swapped >= max_swaps:
                        break

                    square = square_dict.get(num)
                    if not square or not square.neighbors:
                        continue

                    for neighbor_num in square.neighbors:
                        neighbor = square_dict.get(neighbor_num)
                        if not neighbor or neighbor.owner_id != attacker.id:
                            continue

                        # Flip control
                        neighbor.owner = defender
                        neighbor.color = defender_color
                        changed_squares.append(neighbor)
                        neighbor.save()


                        attacker.states -= 1
                        defender.states += 1
                        swapped += 1

                        if swapped >= max_swaps:
                            break

                    iterations += 1

                    # Save nations once
                    attacker.save()
                    defender.save()

        

            div_attackers_lost = oga - int(division_attack_amount)
            div_defenders_lost = ogd - int(division_defend_amount)

            # Pre-fetch once
            game = Games.objects.only("id").get(id=game_id)
            attacker = Nations.objects.get(game=game_id, user=request.user)
            defender_name = request.POST.get('defender')
            defender = Nations.objects.get(game=game_id, name=defender_name)

            # Announcements
            if state_changeD <= state_changeA:
                Announcements.objects.create(
                    text=f"{attacker.name} has defeated {division_defender} in a battle",
                    start_time=datetime.now(),
                    game=game
                )
            else:
                Announcements.objects.create(
                    text=f"{division_defender} has defeated {attacker.name} in a battle",
                    start_time=datetime.now(),
                    game=game
                )

            # Clamp divisions
            attacker.divisions = max(0, attacker.divisions - div_attackers_lost)
            defender.divisions = max(0, defender.divisions - div_defenders_lost)

            # Clamp states
            if defender.states < 0:
                attacker.states += defender.states  # subtracts a negative = adds loss
                defender.states = 0

            if attacker.states < 0:
                defender.states += attacker.states
                attacker.states = 0

            # Save both once
            attacker.save()
            defender.save()

            player = Nations.objects.get(game=game_id, user=request.user)

            if division_defender:
                div_defender = Nations.objects.get(game = game_id, name = division_defender)
            if planes_defender:
                planes_defender = Nations.objects.get(game = game_id, name = planes_defender)
            if boat_defender:
                boat_defender = Nations.objects.get(game = game_id, name = boat_defender)

            number = div_defender.player_number
            player_number_value = f"player{number}"
            if div_defender.states <= 1:
                player.boats += div_defender.boats
                player.planes += div_defender.planes
                div_defender.boats = 0
                div_defender.planes = 0
                div_defender.user = User.objects.get(username='loser')
                div_defender.divisions = 0
                div_defender.alliance_name = ''
                div_defender.save()
                player.save()
                game_instance = Games.objects.get(id=game_id)
                game_instance.enemy_player_number = User.objects.get(username='loser')
                game_instance.save()
                War.objects.filter(Q(nation1=div_defender) | Q(nation2=div_defender)).delete()


            if planes_defender.states <= 1:
                player.boats += planes_defender.boats
                player.planes += planes_defender.planes
                div_defender.boats = 0
                div_defender.planes = 0
                planes_defender.user = User.objects.get(username='loser')
                planes_defender.divisions = 0
                planes_defender.alliance_name = ''
                planes_defender.save()
                player.save()
                game_instance = Games.objects.get(id=game_id)
                game_instance.enemy_player_number = User.objects.get(username='loser')
                game_instance.save()
                War.objects.filter(Q(nation1=planes_defender) | Q(nation2=planes_defender)).delete()
                
            if boat_defender.states <= 1:
                player.boats += boat_defender.boats
                player.planes += boat_defender.planes
                div_defender.boats = 0
                div_defender.planes = 0
                boat_defender.user = User.objects.get(username='loser')
                boat_defender.divisions = 0
                boat_defender.alliance_name = ''
                boat_defender.save()
                player.save()
                game_instance = Games.objects.get(id=game_id)
                game_instance.enemy_player_number = User.objects.get(username='loser')
                game_instance.save()
                War.objects.filter(Q(nation1=boat_defender) | Q(nation2=boat_defender)).delete()

            number = player.player_number
            player_number_value = f"player{number}"
            if player.states <= 1:
                if division_attack_amount:
                    div_defender.boats += player.boats
                    div_defender.planes += player.planes
                    player.user = User.objects.get(username='loser')
                    player.divisions = 0
                    player.alliance_name = ''
                    War.objects.filter(Q(nation1=player) | Q(nation2=player)).delete()
                elif boat_attack_amount:
                    boat_defender.boats += player.boats
                    boat_defender.planes += player.planes
                    player.user = User.objects.get(username='loser')
                    player.divisions = 0
                    player.alliance_name = ''
                    War.objects.filter(Q(nation1=player) | Q(nation2=player)).delete()
                game_instance = Games.objects.get(id=game_id)
                game_instance.player_number_value = User.objects.get(username='loser')
                game_instance.save()
                                
            if division_defender:
                div_defender.save()
            if planes_defender:
                planes_defender.save() 
            if boat_defender:
                boat_defender.save()

            player.save()


        # Preload 'special' users once
        loser_user = User.objects.get(username="loser")
        empty_user = User.objects.get(username="empty")
        closed_user = User.objects.get(username="closed")

        # Get active nations
        active_nations = Nations.objects.filter(
            game=game_id,
            player_number__lt=8
        ).exclude(
            user__in=[loser_user, empty_user, closed_user]
        )

        # Check how many players have completed their turn
        players_ready = sum(1 for nation in active_nations if nation.attacks == 0)

        # Allow two extra players not required to play
        if len(active_nations) < players_ready + 2:
            all_nations = Nations.objects.filter(game=game_id)
            for nation in all_nations:
                states = nation.states

                # Production multiplier based on number of states
                if states <= 20:
                    mult = 2
                elif states < 50:
                    mult = 1.7
                elif states < 150:
                    mult = 1.5
                elif states < 200:
                    mult = 1.4
                elif states < 250:
                    mult = 1
                else:
                    mult = 0.8  # You may want to penalize huge nations? Optional.

                # Apply production values
                nation.divisions += int(states * mult)
                nation.planes += states * 10
                nation.boats += states // 2
                nation.points += 1
                nation.nuke_time -= 1

                if nation.nuke_time <= 0:
                    nation.nukes += 1
                    nation.nuke_time = 5  # Reset or leave at 0 if auto-generating
                nation.attacks = 5
                nation.requests = 10
                nation.save()

        if division_attack_amount or boat_attack_type == "amphibious":
            canvas_width, canvas_height = 1120, 480


            try:
                game = Games.objects.get(id=game_id)
                map_obj = Map.objects.get(number=game_id, game=game)
            except (Games.DoesNotExist, Map.DoesNotExist):
                return bad_request(request, title="User Error", message= "You chose a game that doesn't exsist!")
                return HttpResponseBadRequest("Invalid game or map.")
            
            response = requests.get(map_obj.URL)
            final_image = Image.open(io.BytesIO(response.content)).convert("RGBA")
            white_image_dir = "AWSDefcon1App/static/AWSDefcon1App/white_image"
            existing_images = set(os.listdir(white_image_dir))

            for square in changed_squares:
                filename = f"MapChart_Map.{square.name}.png"
                if filename not in existing_images:
                    continue

                image_path = os.path.join(white_image_dir, filename)
                try:
                    img = Image.open(image_path).convert("RGBA")
                    r, g, b = tuple(int(square.color[i:i+2], 16) for i in (1, 3, 5))  # hex to RGB
                    r_img, _, _, alpha = img.split()
                    colorized = ImageOps.colorize(r_img, black=(r, g, b), white=(r, g, b))
                    colorized.putalpha(alpha)
                    final_image.alpha_composite(colorized)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    continue

            def upload_pil_image_to_imgbb(pil_image, api_key):
                try:
                    buffer = io.BytesIO()
                    pil_image.save(buffer, format="PNG", optimize=True)
                    encoded_image = base64.b64encode(buffer.getvalue())

                    response = requests.post(
                        "https://api.imgbb.com/1/upload",
                        data={"key": api_key, "image": encoded_image}
                    )
                    result = response.json()
                    if result.get("success"):
                        return result["data"]["url"], result["data"]["delete_url"]
                    else:
                        raise Exception(result)
                except Exception as e:
                    print(f"Image upload failed: {e}")
                    raise

            # Upload final image and update Map
            try:
                image_url, delete_url = upload_pil_image_to_imgbb(final_image, api_key)
                map_instance = Map.objects.get(game_id=game_id)

                if map_instance.deleteURL:
                    try:
                        requests.get(map_instance.deleteURL)
                    except requests.RequestException as e:
                        print(f"Failed to delete old image: {e}")

                map_instance.URL = image_url
                map_instance.deleteURL = delete_url
                map_instance.save()
            except Exception as e:
                return HttpResponse(f"Image upload failed: {e}", status=500)
        
        return HttpResponseRedirect(reverse('map', kwargs={'game_id': game_id}))

@login_required(login_url='login')
def loader(request, game_id, reload):
    if request.method == "GET":
        return render(request, 'AWSDefcon1App/loader.html', {'game_id': game_id, 'reload':reload})

    if request.method == "POST":
        canvas_width, canvas_height = 1120, 480
        final_image = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
        game = Games.objects.get(id=game_id)
        map_obj = Map.objects.get(number=game_id, game=game)
        white_image_dir = "AWSDefcon1App/static/AWSDefcon1App/white_image"
        existing_images = set(os.listdir(white_image_dir))

        for square in Square.objects.filter(map=map_obj).only("name", "color"):
            filename = f"MapChart_Map.{square.name}.png"
            if filename not in existing_images:
                continue

            image_path = os.path.join(white_image_dir, filename)
            try:
                img = Image.open(image_path).convert("RGBA")
                r, g, b = tuple(int(square.color[i:i+2], 16) for i in (1, 3, 5))  # hex to RGB
                r_img, _, _, alpha = img.split()
                colorized = ImageOps.colorize(r_img, black=(r, g, b), white=(r, g, b))
                colorized.putalpha(alpha)
                final_image.alpha_composite(colorized)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue

        def upload_pil_image_to_imgbb(pil_image, api_key):
            try:
                buffer = io.BytesIO()
                pil_image.save(buffer, format="PNG", optimize=True)
                encoded_image = base64.b64encode(buffer.getvalue())

                response = requests.post(
                    "https://api.imgbb.com/1/upload",
                    data={"key": api_key, "image": encoded_image}
                )
                result = response.json()
                if result.get("success"):
                    return result["data"]["url"], result["data"]["delete_url"]
                else:
                    raise Exception(result)
            except Exception as e:
                print(f"Image upload failed: {e}")
                raise

        try:
            image_url, delete_url = upload_pil_image_to_imgbb(final_image, api_key)
            map_instance = Map.objects.get(game_id=game_id)

            if map_instance.deleteURL:
                try:
                    requests.get(map_instance.deleteURL)
                except requests.RequestException as e:
                    print(f"Failed to delete old image: {e}")

            map_instance.URL = image_url
            map_instance.deleteURL = delete_url
            map_instance.save()
        except Exception as e:
            return HttpResponse(f"Image upload failed: {e}", status=500)
        
        if reload == 1:
            return HttpResponseRedirect(reverse('map', kwargs={'game_id': game_id}))
        else:  
            return HttpResponseRedirect(reverse('full_index'))

@login_required(login_url = 'login')
def diplomacy(request,game_id):
    return render(request, 'AWSDefcon1App/diplomacy.html', {'game_id':game_id})

@login_required(login_url = 'login')
def makealliance(request,game_id):
    user = request.user
    player = Nations.objects.get(game = game_id, user = request.user)
    if request.method == 'POST':
        if player.requests < 1:
          return bad_request(request, title="User Error", message= "You are out of diplomatic requests. Please click the back button to return to the game")
          return HttpResponseBadRequest("You are out of diplomatic requests. Please click the back button to return to the game")
        player.requests -= 1
        player.save()
        selected_nation = request.POST.get('selected_nation')
        yesman = False
        accepting_nation = request.POST.get('accepting_nation')
        rejecting_nation = request.POST.get('rejected_nation')
        action = request.POST.get('action')
        player_nation = Nations.objects.get(user=request.user,game_id = game_id)

        if action == 'reject':
            rejected_nation = MakeAlliance.objects.filter(nation1__name = rejecting_nation, nation2 = player_nation).first()
            rejected_nation.delete()

        elif action == 'accept':
            player_nation = Nations.objects.get(user=request.user,game_id = game_id)
            accepting_nation = MakeAlliance.objects.filter(nation1__name = accepting_nation, nation2 = player_nation).first()
            player_nation.alliance_name = accepting_nation.nation1.alliance_name
            accepting_nation.delete()
            accepting_nation = Nations.objects.get(game = game_id, name = request.POST.get('accepting_nation'))
            war = War.objects.filter(nation1__alliance_name = accepting_nation.alliance_name, nation2 = player_nation)
            war.delete()
            war = War.objects.filter(nation2__alliance_name = accepting_nation.alliance_name, nation1 = player_nation)
            war.delete()
            player_nation.save()
        elif not selected_nation == "":
            nation2 = Nations.objects.get(name=selected_nation, game=game_id)
            selected_nation_alliance = MakeAlliance.objects.get_or_create(nation1 = Nations.objects.get(user=request.user, game=game_id), nation2 = Nations.objects.get(name=selected_nation, game=game_id))    
            selected_nation_alliance = MakeAlliance.objects.get(nation1 = Nations.objects.get(user=request.user, game=game_id), nation2 = Nations.objects.get(name=selected_nation, game=game_id))    
  
            if nation2.player_number > 7 and nation2.alliance_name == None or nation2.alliance_name == '':
              if nation2.friendlyness < 0: 
                nation2.friendlyness = 0
                nation2.save()
              if nation2.friendlyness != 1:
                  chance = random.randint(1,nation2.friendlyness + 1)
              if chance == 1 or nation2.friendlyness == 1:
                  player_nation = Nations.objects.get(name=selected_nation, game=game_id)
                  player_nation.alliance_name = Nations.objects.get(user=request.user,game_id = game_id).alliance_name
                  player_nation.friendlyness = 10
                  player_nation.save()
                  war = War.objects.filter(nation1 = player_nation).delete()
                  war = War.objects.filter(nation2 = player_nation).delete()
                  announcements = Announcements.objects.create(text =f"{nation2.name} has accepted {Nations.objects.get(user=request.user,game_id = game_id).name}'s invitation to the {Nations.objects.get(user=request.user,game_id = game_id).alliance_name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
                  yesman = True
                  selected_nation_alliance.delete()

            elif nation2.player_number > 7 and nation2.alliance_name != None or nation2.alliance_name != '':
              chance = random.randint(1,nation2.friendlyness + 5)
              if chance == 1:
                player_nation = Nations.objects.get(name=selected_nation, game=game_id)
                player_nation.alliance_name = Nations.objects.get(user=request.user,game_id = game_id).alliance_name
                player_nation.friendlyness = 10
                player_nation.save()
                war = War.objects.filter(nation1 = player_nation).delete()
                war = War.objects.filter(nation2 = player_nation).delete()
                announcements = Announcements.objects.create(text =f"{nation2.name} has accepted {Nations.objects.get(user=request.user,game_id = game_id).name}'s invitation to the {Nations.objects.get(user=request.user,game_id = game_id).alliance_name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
                yesman = True   
                selected_nation_alliance.delete()

            if yesman:
                nations = Nations.objects.filter(game=game_id)
                for nation in nations:
                    if nation.friendlyness == 0 or nation.friendlyness < 1:
                        nation.friendlyness = 1
                user = request.user.username
                # Get the player's nation
                playernation = Nations.objects.filter(game=game_id, user=request.user).first()
                if playernation and playernation.alliance_name:
                    knownnations = Nations.objects.filter(game=game_id, alliance_name=playernation.alliance_name)
                else:
                    knownnations = [playernation] if playernation else []
                return HttpResponseRedirect(reverse('map', kwargs={'game_id': game_id}))

  
    playernation = Nations.objects.filter(game=game_id, user=request.user).first()
    if playernation and playernation.alliance_name:
        knownnations = Nations.objects.filter(game=game_id).exclude(alliance_name=playernation.alliance_name).exclude(user = User.objects.get(username = "loser"))
    else:
        knownnations = Nations.objects.filter(game=game_id).exclude(user=request.user).exclude(user = User.objects.get(username = "loser"))
    playernation = Nations.objects.get(user=request.user, game=game_id)
    alliances = MakeAlliance.objects.filter(nation2__user=request.user)
    user = request.user
    player = Nations.objects.get(game = game_id, user = user)
    requesters = player.requests
    return HttpResponseRedirect(reverse('map', kwargs={'game_id': game_id}))

@login_required(login_url='login')
def war(request,game_id):
    if request.method == 'POST':
        '''
        eligible_nations = Nations.objects.exclude(user__username__in=["closed", "empty", "loser"])
        rand_nation1 = random.choice(eligible_nations)
        eligible_nations_2 = eligible_nations.filter(game = rand_nation1.game).exclude(id=rand_nation1.id)
        rand_nation2 = random.choice(eligible_nations_2)
        war, created = War.objects.get_or_create(nation1=rand_nation1, nation2=rand_nation2)
        announcements = Announcements.objects.create(text =f"{rand_nation1.name} has declared war on {rand_nation2.name}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
        '''
        selected_nation = request.POST.get('selected_nation')
        if selected_nation:
            
            if Nations.objects.get(user=request.user, game=game_id).alliance_name == Nations.objects.get(name=selected_nation, game=game_id).alliance_name:
                return bad_request(request, title="User Error", message="To declare war on an ally, break the alliance using 2 points from the shop")

            selected_nation = War.objects.get_or_create(nation1 = Nations.objects.get(user=request.user, game=game_id), nation2 = Nations.objects.get(name=selected_nation, game=game_id))
        playernation = Nations.objects.get(user=request.user, game=game_id)
        wars = War.objects.filter(nation1__game=game_id) | War.objects.filter(nation2__game=game_id)
        announcements = Announcements.objects.create(text =f"{playernation.name} has declared war on {request.POST.get('selected_nation')}", start_time = datetime.now(), game = Games.objects.get(id = game_id))
        return HttpResponseRedirect(reverse('map', kwargs={'game_id': game_id}))
    # Get the player's nation
    playernation = Nations.objects.filter(game=game_id, user=request.user).first()
    playernationt = playernation.alliance_name
    allies = Nations.objects.filter(game = game_id , alliance_name = playernationt)
    wars = War.objects.filter(nation1__game=game_id) | War.objects.filter(nation2__game=game_id)
    if playernation and playernation.alliance_name:
        knownnations = Nations.objects.filter(game=game_id).exclude(alliance_name=playernation.alliance_name).exclude(user = User.objects.get(username = "loser"))
    else:
        knownnations = Nations.objects.filter(game=game_id).exclude(user=request.user).exclude(user = User.objects.get(username = "loser"))
    
    return render(request, 'AWSDefcon1App/war.html', {'game_id': game_id, 'knownnations': knownnations, "allies":allies})
@login_required(login_url='login')
def send(request,game_id):
    PlayerAAA = Nations.objects.get(game=game_id, user=request.user)
    if request.method == 'POST':
        selected_nation = request.POST.get('selected_nation')
        send_type = request.POST.get('send_type')
        amount = int(request.POST.get('amount'))
        amount = amount/100
        if amount < 0:
          amount = amount * -1
        playernation = Nations.objects.get(user=request.user, game=game_id)
        reciver_nation = Nations.objects.get(game=game_id,name=selected_nation)
        if int(send_type) == 1:
            if amount > playernation.divisions:
                amount = playernation.divisions
            reciver_nation.divisions += amount*playernation.divisions
            playernation.divisions -= amount*playernation.divisions
            reciver_nation.friendlyness -= amount*10
            playernation.save()
            reciver_nation.save()
        if int(send_type) == 2:
            if amount > playernation.planes:
                amount = playernation.planes
            reciver_nation.planes += amount*playernation.planes
            playernation.planes -= amount * playernation.planes
            reciver_nation.friendlyness -= amount*10
            playernation.save()
            reciver_nation.save()
        if int(send_type) == 3:
            if amount > playernation.boats:
                amount = playernation.boats
            reciver_nation.boats += amount*playernation.boats
            playernation.boats -= amount*playernation.boats
            reciver_nation.friendlyness -= amount*10
            playernation.save()
            reciver_nation.save()
        playernation.save()
        reciver_nation.save()
    

    knownnations = Nations.objects.filter(game=game_id).exclude(user=request.user).exclude(user = User.objects.get(username = "loser"))
    nations = Nations.objects.filter(game=game_id)
    for nation in nations:
        if nation.friendlyness < 1:
            nation.friendlyness = 1
    user = request.user.username
    # Get the player's nation
    playernation = Nations.objects.filter(game=game_id, user=request.user).first()
    allies = Nations.objects.filter(game=game_id, alliance_name=playernation.alliance_name)

    return HttpResponseRedirect(reverse('map', kwargs={'game_id': game_id}))


@login_required(login_url='login')
def current_wars(request,game_id):
    playernation = Nations.objects.get(user=request.user, game=game_id)
    playernationt = playernation.alliance_name
    allies = Nations.objects.filter(game = game_id , alliance_name = playernationt)
    wars = War.objects.filter(nation1__game=game_id) | War.objects.filter(nation2__game=game_id)
    if request.method == 'POST':
        winner = request.POST.get('winner')
        if winner:
            loser = Nations.objects.get(user=request.user,game_id = game_id)
            war = War.objects.get(nation1__name = winner, nation2 = loser)
            winner = Nations.objects.get(name = winner ,game_id = game_id)
            winner.states += loser.states
            winner.boats += loser.boats
            winner.planes += loser.planes
            winner.points += loser.points
            winner.nukes += loser.nukes



            # Save the changes to the winner
            winner.save()
            loser.user = User.objects.get(username='loser')
            loser.states = 0
            loser.divisions = 0
            loser.boats = 0
            loser.planes = 0
            loser.alliance_name = ""
            loser.points = 0
            loser.nuke_time = 0
            loser.nukes = 0
            loser.save()
            player_number = loser.player_number
            game = Games.objects.get(id= game_id)
            player_field_name = f"player{player_number}"
            game_instance = Games.objects.get(id=game_id)
            game_instance.player_field_name = User.objects.get(username='loser')
            game_instance.save()
            maper = Map.objects.get(number=game_id, game = Games.objects.get(id=game_id))
            enemy_squares = Square.objects.filter(map=maper, owner=loser)
            for square in enemy_squares:
                square.owner = winner
                color = colors.get(request.POST.get('winner'))
                square.color = color
                square.save()

            return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, 'AWSDefcon1App/current_wars.html', {'wars': wars, 'playernation': playernation, "game_id":game_id, "allies":allies})

@login_required(login_url='login')
def map(request, game_id):

    try:
        PlayerAAA = Nations.objects.get(game=game_id, user=request.user)
    except:
        return bad_request(request, title="User Error", message= "You don't have a nation selected in this game")
    owner = PlayerAAA
    attacks_left = owner.attacks
    wars_as_nation1 = War.objects.filter(nation1=owner)

    wars_as_nation2 = War.objects.filter(nation2=owner)

    nations_at_war = set(
        [war.nation2 for war in wars_as_nation1] + [war.nation1 for war in wars_as_nation2]
    )
    nation_name_at_war = []
    for nations in nations_at_war:
        nation_name_at_war.append(nations.name)

    owner = owner.name
    game = Games.objects.get(id=game_id)
    owned_squares = Square.objects.filter(owner=Nations.objects.get(game = game_id, name = owner), map=Map.objects.get(game=Games.objects.get(id=game_id)))
    controlled_squares = [square.number for square in owned_squares]
    owner = Nations.objects.get(game=Games.objects.get(id = game_id), user=request.user)
    user = request.user
    player = Nations.objects.get(game = game_id, user = user)
    requesters = player.requests
    user = request.user.username
    playernation = Nations.objects.filter(game=game_id, user=request.user).first()
    knownnations = Nations.objects.filter(game=game_id, alliance_name=playernation.alliance_name)
    if(playernation.alliance_name == ""):
        knownnations = [playernation]
    announce = Announcements.objects.filter(game=game_id).order_by('-start_time').first()
    alliances = MakeAlliance.objects.filter(nation2__user=request.user)

    non_loser_nation = Nations.objects.get(game = game_id, user = request.user)
    if non_loser_nation.nukes == 200 or non_loser_nation.nukes > 200 and non_loser_nation.user.id not in Achievements.objects.get(name = "Defcon1").users:
        achievement = Achievements.objects.get(name="Defcon1")
        users_list = achievement.users  
        users_list.append(non_loser_nation.user.id)  
        achievement.users = users_list
        achievement.save()

        non_loser_nation.user.achievements += 1
        non_loser_nation.user.save()

    nations = Nations.objects.filter(game=game_id)
    for nation in nations:
        if nation.friendlyness == 0 or nation.friendlyness < 1:
            nation.friendlyness = 1

    image_filename = Map.objects.get(game = game).URL
    return render(request, "AWSDefcon1App/JSMap.html",{"game_id":game_id ,'image_filename':image_filename,'PlayerAAA':PlayerAAA,'alliances':alliances, 'nation_name_at_war':nation_name_at_war, 'nations_at_war':nations_at_war,'attacks_left':attacks_left, 'owner':owner, "requesters":requesters, "knownnations":knownnations, 'announce':announce, 'nations':nations})

    
def makegame(request,game_id):
    if request.method == 'GET':
        message = ""
        if(not Games.objects.get(id = 1).exsits()):
            next_id = 1
        elif(not Games.objects.get(id = 2).exsits()):
            next_id = 2
        elif(not Games.objects.get(id = 3).exsits()):
            next_id = 3
        elif(not Games.objects.get(id = 4).exsits()):
            next_id = 4
        elif(not Games.objects.get(id = 5).exsits()):
            next_id = 5
        elif(not Games.objects.get(id = 6).exsits()):
            next_id = 6
        make_game = True
        return render(request, "AWSDefcon1App/makegame.html", {"game_id":next_id, "make_game":make_game, "message":message})
    if not User.objects.filter(username='empty').exists():
        user = User.objects.create_user("empty", "emtpyman289666880990@gmail.com", "jkoor8ut09rugho9u069ft-gyyh0j9")
        user = User.objects.create_user("loser", "loserman289666880990@gmail.com", "jkoor8ut09ghy5ho9u069ft-gyyh0j9")
        user.save()
    if not User.objects.filter(username='closed').exists():
      user = User.objects.create_user("closed", "loserman289666880990@gmail.com", "jkoor8ut09ghy5ho9u069ft-gyyh0j9")

    selected_countries = request.POST.getlist('countries')
    
    hard = 1

    if 'UK' in selected_countries:
      user_uk = User.objects.get(username='empty')
    else:
      user_uk = User.objects.get(username='closed')
    
    if 'USA' in selected_countries:
      user_usa = User.objects.get(username='empty')
    else:
      user_usa = User.objects.get(username='closed')
      
    if 'France' in selected_countries:
      user_france = User.objects.get(username='empty')
    else:
      user_france = User.objects.get(username='closed')
    
    if 'USSR' in selected_countries:
      user_ussr = User.objects.get(username='empty')
    else:
      user_ussr = User.objects.get(username='closed')
   
    if 'Germany' in selected_countries:
        user_germany = User.objects.get(username='empty')
    else:
      user_germany = User.objects.get(username='closed')

    if 'Italy' in selected_countries:
        user_italy = User.objects.get(username='empty')
    else:
        user_italy = User.objects.get(username='closed')

    if 'Japan' in selected_countries:
      user_japan = User.objects.get(username='empty')
    else:
      user_japan = User.objects.get(username='closed')

    if 'Cuba' in selected_countries:
      user_cuba = User.objects.get(username='empty')
    else:
      user_cuba = User.objects.get(username='closed')

    if 'Hard' in selected_countries:
      hard = 10

    game_obj = Games.objects.get_or_create(    id=game_id, player1 = User.objects.get(username='empty') , player2 = User.objects.get(username='empty') , player3 = User.objects.get(username='empty') , player4 = User.objects.get(username='empty') , player5 = User.objects.get(username='empty') , player6 = User.objects.get(username='empty') ,player7 =User.objects.get(username='empty'),player0 =User.objects.get(username='empty'))
    game_obj = Games.objects.get(id = game_id)
    Nations.objects.create(    game=game_obj,    name='Cuba',  user = user_cuba,  player_number=0,    states=1,    divisions=80/hard,    boats=200/hard,    planes=4000/hard,    alliance_name='Cuban Pact',    points=1,    nuke_time=8,    nukes=0, attacks = 10, requests = 10) #Player 1
    Nations.objects.create(    game=game_obj,    name='United Kingdom',  user = user_uk,  player_number=1,    states=64,    divisions=170/hard,    boats=300/hard,    planes=2000/hard,    alliance_name='Allies',    points=1,    nuke_time=8,    nukes=0, attacks = 5, requests = 10)#Player 2
    Nations.objects.create(    game=game_obj,    name='United States',  user = user_usa,  player_number=2,    states=36,    divisions=70/hard,    boats=250/hard,    planes=3000/hard,    alliance_name='Neutrality Pact',    points=1,    nuke_time=8,    nukes=0, attacks = 5, requests = 10)#Player 3
    Nations.objects.create(    game=game_obj,    name='France', user = user_france,   player_number=3,    states=68,    divisions=70/hard,    boats=100/hard,    planes=5000/hard,    alliance_name='Allies',    points=1,    nuke_time=8,    nukes=0, attacks = 5, requests = 10)#Player 4
    Nations.objects.create(    game=game_obj,    name='Soviet Union',  user = user_ussr,  player_number=4,    states=152,    divisions=30/hard,    boats=100/hard,    planes=7000/hard,    alliance_name='Comintern',    points=1,    nuke_time=8,    nukes=0, attacks = 5, requests = 10)#Player 5
    Nations.objects.create(    game=game_obj,    name='German Reich', user = user_germany,   player_number=5,    states=23,    divisions=570/hard,    boats=200/hard,    planes=5000/hard,    alliance_name='Axis',    points=1,    nuke_time=8,    nukes=0, attacks = 5, requests = 10)#Player 6
    Nations.objects.create(    game=game_obj,    name='Italy',   user = user_italy, player_number=6,    states=29,    divisions=320/hard,    boats=150/hard,    planes=4500/hard,    alliance_name='Axis',    points=1,    nuke_time=8,    nukes=0, attacks = 5, requests = 10)#Player 7
    Nations.objects.create(    game=game_obj,    name='Japan',  user = user_japan,  player_number=7,    states=24,    divisions=340/hard,    boats=300/hard,    planes=6500/hard,    alliance_name='GEACPS',    points=1,    nuke_time=8,    nukes=0, attacks = 5, requests = 10)#Player 8
    Nations.objects.create( game=game_obj, name = 'Turkey', player_number = 13, states = 21, divisions = 19, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Mexico', player_number = 15, states = 13, divisions = 27, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Spain', player_number = 16, states = 24, divisions = 14, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Poland', player_number = 17, states = 18, divisions = 22, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Australia', player_number = 18, states = 15, divisions = 25, boats = 50, planes = 5000, alliance_name='Allies', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'China', player_number = 19, states = 22, divisions = 18, boats = 50, planes = 5000, alliance_name='Second United Front', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Czechoslovakia', player_number = 20, states = 9, divisions = 31, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Belgium', player_number = 21, states = 10, divisions = 30, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Netherlands', player_number = 22, states = 4, divisions = 35, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Dominion of Canada', player_number = 23, states = 23, divisions = 17, boats = 50, planes = 5000, alliance_name='Allies', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Austria', player_number = 24, states = 4, divisions = 36, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Sweden', player_number = 25, states = 13, divisions = 27, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'British Raj', player_number = 26, states = 23, divisions = 14, boats = 50, planes = 5000, alliance_name='Allies', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Yugoslavia', player_number = 27, states = 14, divisions = 26, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Finland', player_number = 28, states = 12, divisions = 27, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Portugal', player_number = 23, states = 20, divisions = 20, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Kingdom of Greece', player_number = 30, states = 5, divisions = 33, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Iran', player_number = 31, states = 12, divisions = 28, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Bulgaria', player_number = 32, states = 4, divisions = 36, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Second Brazilian Republic', player_number = 33, states = 31, divisions = 28, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Romania', player_number = 34, states = 11, divisions = 29, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Norway', player_number = 35, states = 11, divisions = 29, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Denmark', player_number = 36, states = 7, divisions = 33, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Switzerland', player_number = 37, states = 5, divisions = 35, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Ethiopia', player_number = 38, states = 10, divisions = 30, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Iraq', player_number = 39, states = 3, divisions = 37, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Kingdom of Hungary', player_number = 40, states = 3, divisions = 37, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'South Africa', player_number = 41, states = 7, divisions = 33, boats = 50, planes = 5000, alliance_name='Allies', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Philippines', player_number = 42, states = 7, divisions = 33, boats = 50, planes = 5000, alliance_name='Neutrality Pact', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Ireland', player_number = 43, states = 3, divisions = 37, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Guangxi Clique', player_number = 44, states = 5, divisions = 35, boats = 50, planes = 5000, alliance_name='Second United Front', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Latvia', player_number = 45, states = 5, divisions = 35, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'New Zealand', player_number = 46, states = 3, divisions = 37, boats = 50, planes = 5000, alliance_name='Allies', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Mongolia', player_number = 47, states = 5, divisions = 35, boats = 50, planes = 5000, alliance_name='Comintern', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Xibei San Ma', player_number = 48, states = 7, divisions = 33, boats = 50, planes = 5000, alliance_name='Second United Front', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Colombia', player_number = 49, states = 3, divisions = 37, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Dutch East Indies', player_number = 50, states = 8, divisions = 32, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Lithuania', player_number = 51, states = 5, divisions = 35, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Albania', player_number = 52, states = 3, divisions = 37, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Argentina', player_number = 53, states = 14, divisions = 34, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'British Malaya', player_number = 54, states = 2, divisions = 38, boats = 50, planes = 5000, alliance_name='Allies', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Siam', player_number = 55, states = 4, divisions = 36, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Yunnan', player_number = 56, states = 2, divisions = 38, boats = 50, planes = 5000, alliance_name='Second United Front', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Chile', player_number = 57, states = 8, divisions = 37, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Estonia', player_number = 58, states = 5, divisions = 35, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Sinkiang', player_number = 59, states = 6, divisions = 34, boats = 50, planes = 5000, alliance_name='Second United Front', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Afghanistan', player_number = 60, states = 2, divisions = 38, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Venezuela', player_number = 61, states = 3, divisions = 37, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Saudi Arabia', player_number = 62, states = 9, divisions = 31, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Peru', player_number = 63, states = 5, divisions = 35, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Ecuador', player_number = 65, states = 2, divisions = 38, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Dominican Republic', player_number = 66, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Panama', player_number = 67, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Manchukuo', player_number = 68, states = 7, divisions = 33, boats = 50, planes = 5000, alliance_name='GEACPS', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Tibet', player_number = 69, states = 3, divisions = 37, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Bolivian Republic', player_number = 70, states = 2, divisions = 38, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Haiti', player_number = 71, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Uruguay', player_number = 72, states = 3, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Republic of Paraguay', player_number = 73, states = 2, divisions = 38, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Luxembourg', player_number = 74, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Mengkukuo', player_number = 75, states = 2, divisions = 38, boats = 50, planes = 5000, alliance_name='GEACPS', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Shanxi', player_number = 76, states = 3, divisions = 37, boats = 50, planes = 5000, alliance_name='Second United Front', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Communist China', player_number = 77, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='Second United Front', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Nepal', player_number = 78, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Yemen', player_number = 79, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Guatemala', player_number = 80, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'El Salvador', player_number = 81, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Honduras', player_number = 82, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Liberia', player_number = 83, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Nicaragua', player_number = 84, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Costa Rica', player_number = 85, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Bhutan', player_number = 86, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Oman', player_number = 87, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Tannu Tuva', player_number = 88, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='Comintern', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Sultanate of Aussa', player_number = 89, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )
    Nations.objects.create( game=game_obj, name = 'Iceland', player_number = 90, states = 1, divisions = 39, boats = 50, planes = 5000, alliance_name='', points = 0, nuke_time = 8, nukes = 0, attacks = 2, requests = 4 )

    map_obj = Map.objects.get_or_create(number=game_id, game =game_obj)
    map_obj = Map.objects.get(game = game_obj)
    squares_data = [
        {"name": "Aberdeenshire", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Abkhazia", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Abruzzo", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Abu Dhabi", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Acre", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Aden", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Afar", "color": "#4d0019", "owner_name": "Sultanate of Aussa"},
        {"name": "Afyon", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Agder", "color": "#623c3c", "owner_name": "Norway"},
        {"name": "Akhtubinsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Akmolinsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Al Hajara", "color": "#e79481", "owner_name": "Iraq"},
        {"name": "Al Qassim", "color": "#def7c6", "owner_name": "Saudi Arabia"},
        {"name": "Alabama", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Alaska", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Albania", "color": "#c23b85", "owner_name": "Albania"},
        {"name": "Alberta", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Aleppo", "color": "#4993ff", "owner_name": "France"},
        {"name": "Alexandria", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Alfold", "color": "#ffa47f", "owner_name": "Kingdom of Hungary"},
        {"name": "Algerian Desert", "color": "#4993ff", "owner_name": "France"},
        {"name": "Algiers", "color": "#4993ff", "owner_name": "France"},
        {"name": "Alma Ata", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Alpes", "color": "#4993ff", "owner_name": "France"},
        {"name": "Alsace Lorraine", "color": "#4993ff", "owner_name": "France"},
        {"name": "Altai Krai", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Alto Adige", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Amapa", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Amasya", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Amazon impassable 1", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Amazon impassable 2", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Amazon impassable 3", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Amazon impassable 4", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Amazon impassable 5", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Amazon impassable 6", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Amazon impassable 7", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Amazon impassable 8", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Amazonas", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Amur", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Anhui", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Ankara", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Antalya", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Antofagasta", "color": "#ca828b", "owner_name": "Chile"},
        {"name": "Aquitaine", "color": "#4993ff", "owner_name": "France"},
        {"name": "Araucania", "color": "#ca828b", "owner_name": "Chile"},
        {"name": "Arequipa", "color": "#fff6ff", "owner_name": "Peru"},
        {"name": "Arica y Tarapaca", "color": "#ca828b", "owner_name": "Chile"},
        {"name": "Arizona", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Arkansas", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Arkhangelsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Armenia", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Arunachal Pradesh", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Ashkhabad", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Asir Makkah", "color": "#def7c6", "owner_name": "Saudi Arabia"},
        {"name": "Assam", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Astrakhan", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Asturias", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Aswan", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Atacama", "color": "#ca828b", "owner_name": "Chile"},
        {"name": "Attica", "color": "#79ebff", "owner_name": "Kingdom of Greece"},
        {"name": "Aukstaitija", "color": "#ffff9b", "owner_name": "Lithuania"},
        {"name": "Auvergne", "color": "#4993ff", "owner_name": "France"},
        {"name": "Ayaguz", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Aysen", "color": "#ca828b", "owner_name": "Chile"},
        {"name": "Azerbaijan", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Baghdad", "color": "#e79481", "owner_name": "Iraq"},
        {"name": "Bahia", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Bahr al Ghazal", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Baja California", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "Balakovo", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Bale", "color": "#c3a5f5", "owner_name": "Ethiopia"},
        {"name": "Balta Tiraspol", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Baluchistan", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Bamako", "color": "#4993ff", "owner_name": "France"},
        {"name": "Banat", "color": "#9e9e00", "owner_name": "Romania"},
        {"name": "Bechuanaland", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Begemder", "color": "#c3a5f5", "owner_name": "Ethiopia"},
        {"name": "Beijing", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Beja", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Belgorod", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Benghasi", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Benue", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Bessarabia", "color": "#9e9e00", "owner_name": "Romania"},
        {"name": "Bhutan", "color": "#ac7a58", "owner_name": "Bhutan"},
        {"name": "Bialystok", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Bihar", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Birobidzhan", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Bismarck", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "Blue Nile", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Bobruysk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Bodaybo", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Bohemia", "color": "#46d8cb", "owner_name": "Czechoslovakia"},
        {"name": "Bohuslan", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "Bolivar", "color": "#70b626", "owner_name": "Venezuela"},
        {"name": "Bombay", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Borkou Ennedi Tibesti", "color": "#4993ff", "owner_name": "France"},
        {"name": "Borno", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Bosnia", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "Bouches du Rhone", "color": "#4993ff", "owner_name": "France"},
        {"name": "Bourgogne", "color": "#4993ff", "owner_name": "France"},
        {"name": "Brabant", "color": "#ffb35f", "owner_name": "Netherlands"},
        {"name": "Brandenburg", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Bratsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "British Columbia", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "British Guyana", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "British Honduras", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "British Somaliland", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Brittany", "color": "#4993ff", "owner_name": "France"},
        {"name": "Bryansk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Bucovina", "color": "#9e9e00", "owner_name": "Romania"},
        {"name": "Bukhara", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Burgas", "color": "#329a00", "owner_name": "Bulgaria"},
        {"name": "Burgos", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Burma", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Bursa", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Burundi", "color": "#fbdf0a", "owner_name": "Belgium"},
        {"name": "Buryatia", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Cairo", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Calabria", "color": "#56a552", "owner_name": "Italy"},
        {"name": "California", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Cambodia", "color": "#4993ff", "owner_name": "France"},
        {"name": "Cameroon", "color": "#4993ff", "owner_name": "France"},
        {"name": "Campania", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Cape", "color": "#be96fa", "owner_name": "South Africa"},
        {"name": "Carpathian Ruthenia", "color": "#46d8cb", "owner_name": "Czechoslovakia"},
        {"name": "Casablanca", "color": "#4993ff", "owner_name": "France"},
        {"name": "Cataluna", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Ceara", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Cebu", "color": "#b496e6", "owner_name": "Philippines"},
        {"name": "Central Australia", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "Central Islands", "color": "#b496e6", "owner_name": "Philippines"},
        {"name": "Central Macedonia", "color": "#79ebff", "owner_name": "Kingdom of Greece"},
        {"name": "Centre", "color": "#4993ff", "owner_name": "France"},
        {"name": "Centre Sud", "color": "#4993ff", "owner_name": "France"},
        {"name": "Cerro Largo", "color": "#abbe99", "owner_name": "Uruguay"},
        {"name": "Ceylon", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Chaco Austral", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Chaco Boreal", "color": "#4696fa", "owner_name": "Republic of Paraguay"},
        {"name": "Chad", "color": "#4993ff", "owner_name": "France"},
        {"name": "Chahar", "color": "#a5e684", "owner_name": "Mengkukuo"},
        {"name": "Champagne", "color": "#4993ff", "owner_name": "France"},
        {"name": "Changde", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Chechnya Ingushetia", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Chelyabinsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Cherkasy", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Chernigov", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Chiapas", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "Chihuahua", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "Chita", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Chubut", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Chugoku", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Chukchi Peninsula", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Chukotka", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Chuvashia", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Ciudad Real", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Coahuila", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "Colorado", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Connaught", "color": "#68cf75", "owner_name": "Ireland"},
        {"name": "Constantine", "color": "#4993ff", "owner_name": "France"},
        {"name": "Coquilhatville", "color": "#fbdf0a", "owner_name": "Belgium"},
        {"name": "Cordoba", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Corsica", "color": "#4993ff", "owner_name": "France"},
        {"name": "Costa Rica", "color": "#927a30", "owner_name": "Costa Rica"},
        {"name": "Costermansville", "color": "#fbdf0a", "owner_name": "Belgium"},
        {"name": "Cote Nord", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Crimea", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Crisana", "color": "#9e9e00", "owner_name": "Romania"},
        {"name": "Croatia", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "Cuba", "color": "#8b40a6", "owner_name": "Cuba"},
        {"name": "Cumbria", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Cundinamarca", "color": "#fff375", "owner_name": "Colombia"},
        {"name": "Cyprus", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Cyrenaica", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Dabancheng", "color": "#3fb08d", "owner_name": "Sinkiang"},
        {"name": "Dagestan", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Dahomey", "color": "#4993ff", "owner_name": "France"},
        {"name": "Dalarna", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "Dali", "color": "#698948", "owner_name": "Yunnan"},
        {"name": "Dalian", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Dalmatia", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "Damascus", "color": "#4993ff", "owner_name": "France"},
        {"name": "Dammam", "color": "#def7c6", "owner_name": "Saudi Arabia"},
        {"name": "Danzig", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Deir az Zur", "color": "#4993ff", "owner_name": "France"},
        {"name": "Delhi", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Derna", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Districts of Ontario", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Diyarbakir", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Dnipropetrovsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Dobrudja", "color": "#9e9e00", "owner_name": "Romania"},
        {"name": "Dominican Republic", "color": "#bea0f0", "owner_name": "Dominican Republic"},
        {"name": "Dornod", "color": "#5a771d", "owner_name": "Mongolia"},
        {"name": "Dudinka", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Durango", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "Dzungaria", "color": "#3fb08d", "owner_name": "Sinkiang"},
        {"name": "East Anglia", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "East Bengal", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "East Hebei", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "East Midlands", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Easter Island", "color": "#ca828b", "owner_name": "Chile"},
        {"name": "Eastern Aragon", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Eastern Desert", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Eastern Slovakia", "color": "#46d8cb", "owner_name": "Czechoslovakia"},
        {"name": "Eastern Sudetenland", "color": "#46d8cb", "owner_name": "Czechoslovakia"},
        {"name": "Eastern Swiss Alps", "color": "#c15151", "owner_name": "Switzerland"},
        {"name": "Ecuador", "color": "#ffbe7f", "owner_name": "Ecuador"},
        {"name": "Edirne", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "El Agheila", "color": "#56a552", "owner_name": "Italy"},
        {"name": "El Salvador", "color": "#fabe78", "owner_name": "El Salvador"},
        {"name": "Elisabethville", "color": "#fbdf0a", "owner_name": "Belgium"},
        {"name": "Emilia Romagna", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Engels Marxstadt", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Epirus", "color": "#79ebff", "owner_name": "Kingdom of Greece"},
        {"name": "Equatorial Africa", "color": "#4993ff", "owner_name": "France"},
        {"name": "Equatorial Guinea", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Eritrea", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Ermland Masuren", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Espirito Santo", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Extremadura", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Fars", "color": "#5c927e", "owner_name": "Iran"},
        {"name": "Fiji", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Finnmark", "color": "#623c3c", "owner_name": "Norway"},
        {"name": "Florida", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Formosa", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Franche Comte", "color": "#4993ff", "owner_name": "France"},
        {"name": "Franken", "color": "#525252", "owner_name": "German Reich"},
        {"name": "French Guiana", "color": "#4993ff", "owner_name": "France"},
        {"name": "French India", "color": "#4993ff", "owner_name": "France"},
        {"name": "French Somaliland", "color": "#4993ff", "owner_name": "France"},
        {"name": "Friesland", "color": "#ffb35f", "owner_name": "Netherlands"},
        {"name": "Fujian", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Gabes", "color": "#4993ff", "owner_name": "France"},
        {"name": "Gabon", "color": "#4993ff", "owner_name": "France"},
        {"name": "Galicia", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Gambia", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Gannan", "color": "#685b84", "owner_name": "Xibei San Ma"},
        {"name": "Gansu", "color": "#685b84", "owner_name": "Xibei San Ma"},
        {"name": "Ganzi", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Gao", "color": "#4993ff", "owner_name": "France"},
        {"name": "Garissa", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Gavleborg", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "Gdynia", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Georgia", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Georgia US", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Ghana", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Gibraltar", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Gilan", "color": "#5c927e", "owner_name": "Iran"},
        {"name": "Gloucestershire", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Goa", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Gobi", "color": "#5a771d", "owner_name": "Mongolia"},
        {"name": "Goias", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Gojjam", "color": "#c3a5f5", "owner_name": "Ethiopia"},
        {"name": "Golog", "color": "#685b84", "owner_name": "Xibei San Ma"},
        {"name": "Gomel", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Gorky", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Gotland", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "Granada", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Greater London Area", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Greenland", "color": "#e25c0e", "owner_name": "Denmark"},
        {"name": "Guadalajara", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Guangdong", "color": "#8a9a74", "owner_name": "Guangxi Clique"},
        {"name": "Guangxi", "color": "#8a9a74", "owner_name": "Guangxi Clique"},
        {"name": "Guangzhou", "color": "#8a9a74", "owner_name": "Guangxi Clique"},
        {"name": "Guangzhouwan", "color": "#4993ff", "owner_name": "France"},
        {"name": "Guapore", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Guarda", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Guatemala", "color": "#473070", "owner_name": "Guatemala"},
        {"name": "Guerrero", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "Guinea", "color": "#4993ff", "owner_name": "France"},
        {"name": "Guizhou", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Gujarat", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Guryev", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Haida Gwaii", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Hainan", "color": "#8a9a74", "owner_name": "Guangxi Clique"},
        {"name": "Haiti", "color": "#ab6f72", "owner_name": "Haiti"},
        {"name": "Haixi", "color": "#685b84", "owner_name": "Xibei San Ma"},
        {"name": "Hakkari", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Hamadan", "color": "#5c927e", "owner_name": "Iran"},
        {"name": "Hame", "color": "#ffffff", "owner_name": "Finland"},
        {"name": "Hannover", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Hararghe", "color": "#c3a5f5", "owner_name": "Ethiopia"},
        {"name": "Harju", "color": "#63cdfe", "owner_name": "Estonia"},
        {"name": "Hatay", "color": "#4993ff", "owner_name": "France"},
        {"name": "Hawaii", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Hebei", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Heilungkiang", "color": "#ff7847", "owner_name": "Manchukuo"},
        {"name": "Helgeland", "color": "#623c3c", "owner_name": "Norway"},
        {"name": "Henan", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Herat", "color": "#53d0d9", "owner_name": "Afghanistan"},
        {"name": "Herzegovina", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "Hessen", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Hinterpommern", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Hokkaido", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Hokuriku", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Holland", "color": "#ffb35f", "owner_name": "Netherlands"},
        {"name": "Holstein", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Honduras", "color": "#B6E01F", "owner_name": "Honduras"},
        {"name": "Huangshan", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Hubei", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Hulunbuir", "color": "#ff7847", "owner_name": "Manchukuo"},
        {"name": "Hunan", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Hyderabad", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Iceland", "color": "#c79779", "owner_name": "Iceland"},
        {"name": "Idaho", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Ile de France", "color": "#4993ff", "owner_name": "France"},
        {"name": "Illinois", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Illubabor Kaffa", "color": "#c3a5f5", "owner_name": "Ethiopia"},
        {"name": "Indiana", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Indore", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Iowa", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Irkutsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Isan", "color": "#d7f0c8", "owner_name": "Siam"},
        {"name": "Isfahan", "color": "#5c927e", "owner_name": "Iran"},
        {"name": "Istanbul", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Istria", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Ivanovo", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Ivory Coast", "color": "#4993ff", "owner_name": "France"},
        {"name": "Iwo Jima", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Izmir", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Izmit", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Jabalpur", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Jalisco", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "Jamaica", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Jamtland", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "Java", "color": "#5b21e2", "owner_name": "Dutch East Indies"},
        {"name": "Jawf", "color": "#def7c6", "owner_name": "Saudi Arabia"},
        {"name": "Jehol", "color": "#ff7847", "owner_name": "Manchukuo"},
        {"name": "Jiangsu", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Jiangxi", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Jiuquan", "color": "#685b84", "owner_name": "Xibei San Ma"},
        {"name": "Jordan", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Jubaland", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Jura Mountains", "color": "#c15151", "owner_name": "Switzerland"},
        {"name": "Jylland", "color": "#e25c0e", "owner_name": "Denmark"},
        {"name": "Kabardino Balkaria", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kabul", "color": "#53d0d9", "owner_name": "Afghanistan"},
        {"name": "Kalimantan", "color": "#5b21e2", "owner_name": "Dutch East Indies"},
        {"name": "Kalinin", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kalmykia", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kaluga", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kamchatka", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kansai", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Kansas", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Kanto", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Karagandy", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Karakalpakstan", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Karas", "color": "#be96fa", "owner_name": "South Africa"},
        {"name": "Kargopol", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Karjala", "color": "#ffffff", "owner_name": "Finland"},
        {"name": "Kashmir", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Kassala", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Kastamonu", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Katowice", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Kaunas", "color": "#ffff9b", "owner_name": "Lithuania"},
        {"name": "Kayes Koulikoro", "color": "#4993ff", "owner_name": "France"},
        {"name": "Kayseri", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Kazan", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kentucky", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Kerman", "color": "#5c927e", "owner_name": "Iran"},
        {"name": "Khabarovsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Khakassia", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kharkov", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Khartoum", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Khatangsky", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kherson", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Khiva", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Khmelnytskyi", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Khomas", "color": "#be96fa", "owner_name": "South Africa"},
        {"name": "Khorasan", "color": "#5c927e", "owner_name": "Iran"},
        {"name": "Khovd", "color": "#5a771d", "owner_name": "Mongolia"},
        {"name": "Khovsgol", "color": "#5a771d", "owner_name": "Mongolia"},
        {"name": "Khuzestan", "color": "#5c927e", "owner_name": "Iran"},
        {"name": "Kielce", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Kirensk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kirin", "color": "#ff7847", "owner_name": "Manchukuo"},
        {"name": "Kirov", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kolyma", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Konigsberg", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Konya", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Koshinetsu", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Kosovo", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "Kostanay", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kotlas", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Krakow", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Krasnodar", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Krasnoyarsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kunene", "color": "#be96fa", "owner_name": "South Africa"},
        {"name": "Kunlun Shan", "color": "#3fb08d", "owner_name": "Sinkiang"},
        {"name": "Kuopio", "color": "#ffffff", "owner_name": "Finland"},
        {"name": "Kurdistan", "color": "#5c927e", "owner_name": "Iran"},
        {"name": "Kurdufan", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Kursk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kurzeme", "color": "#7b7cb8", "owner_name": "Latvia"},
        {"name": "Kuwait", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Kuybyshev", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kyiv", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Kymi", "color": "#ffffff", "owner_name": "Finland"},
        {"name": "Kyushu", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Kyzyl Orda", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "La Libertad", "color": "#fff375", "owner_name": "Colombia"},
        {"name": "La Paz", "color": "#ffeab1", "owner_name": "Bolivian Republic"},
        {"name": "Labrador", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Lagos", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Lanark", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Lancashire", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Languedoc", "color": "#4993ff", "owner_name": "France"},
        {"name": "Lanna", "color": "#d7f0c8", "owner_name": "Siam"},
        {"name": "Laos", "color": "#4993ff", "owner_name": "France"},
        {"name": "Lappi", "color": "#ffffff", "owner_name": "Finland"},
        {"name": "Latgale", "color": "#7b7cb8", "owner_name": "Latvia"},
        {"name": "Lazio", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Lebanon", "color": "#4993ff", "owner_name": "France"},
        {"name": "Leinster", "color": "#68cf75", "owner_name": "Ireland"},
        {"name": "Leningrad", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Leon", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Leopoldville", "color": "#fbdf0a", "owner_name": "Belgium"},
        {"name": "Lesser Sunda Islands", "color": "#5b21e2", "owner_name": "Dutch East Indies"},
        {"name": "Liangshan", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Liaoning", "color": "#ff7847", "owner_name": "Manchukuo"},
        {"name": "Liaotung", "color": "#ff7847", "owner_name": "Manchukuo"},
        {"name": "Liberia", "color": "#cdafff", "owner_name": "Liberia"},
        {"name": "Libyan Desert", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Lima", "color": "#fff6ff", "owner_name": "Peru"},
        {"name": "Limousin", "color": "#4993ff", "owner_name": "France"},
        {"name": "Lipetsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Lisbon", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Litorale", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Ljubljana", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "Lodz", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Loire", "color": "#4993ff", "owner_name": "France"},
        {"name": "Lombardia", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Loreto", "color": "#fff6ff", "owner_name": "Peru"},
        {"name": "Los Andes", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Lothian", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Louisiana", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Lourenco Marques", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Lower Austria", "color": "#a999f0", "owner_name": "Austria"},
        {"name": "Luanda", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Lublin", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Lucknow", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Luga", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Lusambo", "color": "#fbdf0a", "owner_name": "Belgium"},
        {"name": "Luxembourg", "color": "#8adba2", "owner_name": "Luxembourg"},
        {"name": "Luzon", "color": "#b496e6", "owner_name": "Philippines"},
        {"name": "Lwow", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Macedonia", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "Madagascar", "color": "#4993ff", "owner_name": "France"},
        {"name": "Madinah", "color": "#def7c6", "owner_name": "Saudi Arabia"},
        {"name": "Madras", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Madrid", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Madurai", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Magadan", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Magallanes", "color": "#ca828b", "owner_name": "Chile"},
        {"name": "Magnitogorsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Malatya", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Malawi", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Mandalay", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Manica e Sofala", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Manila", "color": "#b496e6", "owner_name": "Philippines"},
        {"name": "Manitoba", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Maranhao", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Mari El", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Marrakech", "color": "#4993ff", "owner_name": "France"},
        {"name": "Maryland", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Mato Grosso", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Matrouh", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Maurice", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Mauritania", "color": "#4993ff", "owner_name": "France"},
        {"name": "Mauritanian Desert", "color": "#4993ff", "owner_name": "France"},
        {"name": "Mecklenburg", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Memel", "color": "#ffff9b", "owner_name": "Lithuania"},
        {"name": "Mendoza", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Mersin", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Mesopotamia", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Meta", "color": "#fff375", "owner_name": "Colombia"},
        {"name": "Mexico City", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "Michigan", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Middle Congo", "color": "#4993ff", "owner_name": "France"},
        {"name": "Midi Pyrenees", "color": "#4993ff", "owner_name": "France"},
        {"name": "Mikhaylovka", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Mikkeli", "color": "#ffffff", "owner_name": "Finland"},
        {"name": "Millerovo", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Minas Gerais", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Mindanao", "color": "#b496e6", "owner_name": "Philippines"},
        {"name": "Minnesota", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Minsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Miranda", "color": "#70b626", "owner_name": "Venezuela"},
        {"name": "Mississippi", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Missouri", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Moesia", "color": "#329a00", "owner_name": "Bulgaria"},
        {"name": "Moldova", "color": "#9e9e00", "owner_name": "Romania"},
        {"name": "Mombasa", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Montana", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Montenegro", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "Morava", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "Moravia", "color": "#46d8cb", "owner_name": "Czechoslovakia"},
        {"name": "Moscow", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Moselland", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Mosul", "color": "#e79481", "owner_name": "Iraq"},
        {"name": "Mozyr", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Munster", "color": "#68cf75", "owner_name": "Ireland"},
        {"name": "Muntenia", "color": "#9e9e00", "owner_name": "Romania"},
        {"name": "Murcia", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Murmansk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Mykolaiv", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Mysore", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Nagqu", "color": "#456722", "owner_name": "Tibet"},
        {"name": "Nairobi", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Najiran", "color": "#def7c6", "owner_name": "Saudi Arabia"},
        {"name": "Nanning", "color": "#8a9a74", "owner_name": "Guangxi Clique"},
        {"name": "Natal", "color": "#be96fa", "owner_name": "South Africa"},
        {"name": "Navarra", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Navoi", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Nebraska", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Nejd", "color": "#def7c6", "owner_name": "Saudi Arabia"},
        {"name": "Nenets", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Nepal", "color": "#c8aafa", "owner_name": "Nepal"},
        {"name": "Nevada", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Nevel", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "New Brunswick", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "New Caledonia", "color": "#4993ff", "owner_name": "France"},
        {"name": "New England", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "New Jersey", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "New Mexico", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "New South Wales", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "New York", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Newfoundland", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Ngari", "color": "#456722", "owner_name": "Tibet"},
        {"name": "Nicaragua", "color": "#92b2bf", "owner_name": "Nicaragua"},
        {"name": "Niederbayern", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Niederschlesien", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Niger", "color": "#4993ff", "owner_name": "France"},
        {"name": "Nikolayevsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Ningxia", "color": "#685b84", "owner_name": "Xibei San Ma"},
        {"name": "Nord du Quebec", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Nord Pas de Calais", "color": "#4993ff", "owner_name": "France"},
        {"name": "Nordland", "color": "#623c3c", "owner_name": "Norway"},
        {"name": "Normandy", "color": "#4993ff", "owner_name": "France"},
        {"name": "Norrbotten", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "North Angola", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "North Borneo", "color": "#e623d5", "owner_name": "British Malaya"},
        {"name": "North Carolina", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "North Dakota", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "North Darfur", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "North Island", "color": "#b99beb", "owner_name": "New Zealand"},
        {"name": "North Korea", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "North Ossetia", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "North Queensland", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "North Sakhalin", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "North Slovenia", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "North Transylvania", "color": "#9e9e00", "owner_name": "Romania"},
        {"name": "North West Australia", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "Northern Epirus", "color": "#c23b85", "owner_name": "Albania"},
        {"name": "Northern Hungary", "color": "#ffa47f", "owner_name": "Kingdom of Hungary"},
        {"name": "Northern Ireland", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Northern Kashmir", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Northern Malay", "color": "#d7f0c8", "owner_name": "Siam"},
        {"name": "Northern Manitoba", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Northern Ontario", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Northern Saskatchewan", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Northern Territory", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "Northern Urals", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Northumberland", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Northwest Territories", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Nova Scotia", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Novgorod", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Novosibirsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Nowogrodek", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Nunavut", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Nyanza Rift Valley", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Oaxaca", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "Oberbayern", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Oberschlesien", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Odessa", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Ohio", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Okhotsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Okinawa", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Oklahoma", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Olonets", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Oltenia", "color": "#9e9e00", "owner_name": "Romania"},
        {"name": "Oman", "color": "#905c5c", "owner_name": "Oman"},
        {"name": "Omsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Onega", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Opplandene", "color": "#623c3c", "owner_name": "Norway"},
        {"name": "Ordos", "color": "#651e29", "owner_name": "Shanxi"},
        {"name": "Oregon", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Orel", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Orenburg", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Orissa", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Oslofjord", "color": "#623c3c", "owner_name": "Norway"},
        {"name": "Ostergotland", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "Ostmark", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Otjozondjupa", "color": "#be96fa", "owner_name": "South Africa"},
        {"name": "Ouest du Quebec", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Oulu", "color": "#ffffff", "owner_name": "Finland"},
        {"name": "Oyrot Region", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Pais Vasco", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Palestine", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Pamir", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Pampas", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Panama", "color": "#9e8add", "owner_name": "Panama"},
        {"name": "Panama Canal", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Papua", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "Para", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Paraguay", "color": "#4696fa", "owner_name": "Republic of Paraguay"},
        {"name": "Parana", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Parnu", "color": "#63cdfe", "owner_name": "Estonia"},
        {"name": "Pastaza", "color": "#ffbe7f", "owner_name": "Ecuador"},
        {"name": "Pavlodar", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Paysandu", "color": "#abbe99", "owner_name": "Uruguay"},
        {"name": "Pechora", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Peloponnese", "color": "#79ebff", "owner_name": "Kingdom of Greece"},
        {"name": "Pennsylvania", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Penza", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Perm", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Pernambuco", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Peshawar", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Petsamo", "color": "#ffffff", "owner_name": "Finland"},
        {"name": "Piaui", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Picardy", "color": "#4993ff", "owner_name": "France"},
        {"name": "Piemonte", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Plock", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Plovdiv", "color": "#329a00", "owner_name": "Bulgaria"},
        {"name": "Poitou", "color": "#4993ff", "owner_name": "France"},
        {"name": "Polesie", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Poltava", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Porto", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Portuguese Guinea", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Portuguese Timor", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Poznan", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Pskov", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Puglia", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Punjab", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Punta Pora", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Pyrenees Atlantiques", "color": "#4993ff", "owner_name": "France"},
        {"name": "Qatar", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Qingdao", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Qinghai", "color": "#685b84", "owner_name": "Xibei San Ma"},
        {"name": "Queensland", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "Quetta", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Rajahsthan", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Region Mesopotamica", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Rhineland", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Rhodesia", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Rhone", "color": "#4993ff", "owner_name": "France"},
        {"name": "Riga", "color": "#7b7cb8", "owner_name": "Latvia"},
        {"name": "Rio Branco", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Rio de Janeiro", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Rio de Oro", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Rio Grande do Norte", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Rio Grande do Sul", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Rio Negro", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Roslavl", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Rostov", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Rub al Khali", "color": "#def7c6", "owner_name": "Saudi Arabia"},
        {"name": "Rwanda", "color": "#fbdf0a", "owner_name": "Belgium"},
        {"name": "Ryazan", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Rzhev", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Sachsen", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Saguenay", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Saint Lawrence", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Salamanca", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Salekhard", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Salla", "color": "#ffffff", "owner_name": "Finland"},
        {"name": "Samar", "color": "#b496e6", "owner_name": "Philippines"},
        {"name": "Samsun", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "San Juan y La Rioja", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "San Luis y La Pampa", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Santa Catarina", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Santa Cruz", "color": "#ffeab1", "owner_name": "Bolivian Republic"},
        {"name": "Santa Cruz AR", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Santarem", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Santiago", "color": "#ca828b", "owner_name": "Chile"},
        {"name": "Sao Paulo", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Saratov", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Sardegna", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Saskatchewan", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Savoy", "color": "#4993ff", "owner_name": "France"},
        {"name": "Schleswig", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Scottish Highlands", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Semipalatinsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Semnan", "color": "#5c927e", "owner_name": "Iran"},
        {"name": "Senegal", "color": "#4993ff", "owner_name": "France"},
        {"name": "Serbia", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "Sevilla", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Shaanxi", "color": "#b2233b", "owner_name": "Communist China"},
        {"name": "Shandong", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Shanghai", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Shanxi", "color": "#651e29", "owner_name": "Shanxi"},
        {"name": "Shewa", "color": "#c3a5f5", "owner_name": "Ethiopia"},
        {"name": "Shigatse", "color": "#456722", "owner_name": "Tibet"},
        {"name": "Shikoku", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Shkoder", "color": "#c23b85", "owner_name": "Albania"},
        {"name": "Siam", "color": "#d7f0c8", "owner_name": "Siam"},
        {"name": "Sichuan", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Sicilia", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Sidamo", "color": "#c3a5f5", "owner_name": "Ethiopia"},
        {"name": "Sidi Ifni", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Sierra Leone", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Sinai", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Sind", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "Singapore", "color": "#e623d5", "owner_name": "British Malaya"},
        {"name": "Sirte", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Sistan", "color": "#5c927e", "owner_name": "Iran"},
        {"name": "Sivas", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Sjaelland", "color": "#e25c0e", "owner_name": "Denmark"},
        {"name": "Skane", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "Smaland", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "Smolensk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Sochi", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Sodermalm", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "Sofia", "color": "#329a00", "owner_name": "Bulgaria"},
        {"name": "Sokoto", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Solomon Islands", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "Somaliland", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Sonderjylland", "color": "#e25c0e", "owner_name": "Denmark"},
        {"name": "Sonora", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "South Australia", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "South Carolina", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "South Chahar", "color": "#a5e684", "owner_name": "Mengkukuo"},
        {"name": "South Dakota", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "South Darfur", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "South Georgia", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "South Island", "color": "#b99beb", "owner_name": "New Zealand"},
        {"name": "South Korea", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "South Sakhalin", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "South West Angola", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "South West Australia", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "South West England", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Southern Bessarabia", "color": "#9e9e00", "owner_name": "Romania"},
        {"name": "Southern Indochina", "color": "#4993ff", "owner_name": "France"},
        {"name": "Southern Ontario", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Southern Sahara", "color": "#4993ff", "owner_name": "France"},
        {"name": "Southern Serbia", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "Southern Slovakia", "color": "#46d8cb", "owner_name": "Czechoslovakia"},
        {"name": "Southwest Queensland", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "Spanish Africa", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Stalinabad", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Stalingrad", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Stalino", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Stanislawow", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Stanleyville", "color": "#fbdf0a", "owner_name": "Belgium"},
        {"name": "Stavropol", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Sudetenland", "color": "#46d8cb", "owner_name": "Czechoslovakia"},
        {"name": "Suduva", "color": "#ffff9b", "owner_name": "Lithuania"},
        {"name": "Suez", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Suiyuan", "color": "#651e29", "owner_name": "Shanxi"},
        {"name": "Sulawesi", "color": "#5b21e2", "owner_name": "Dutch East Indies"},
        {"name": "Sumatra", "color": "#5b21e2", "owner_name": "Dutch East Indies"},
        {"name": "Sumy", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Sungkiang", "color": "#ff7847", "owner_name": "Manchukuo"},
        {"name": "Surgut", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Suriname", "color": "#ffb35f", "owner_name": "Netherlands"},
        {"name": "Sussex", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Sverdlovsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Swiss Plateau", "color": "#c15151", "owner_name": "Switzerland"},
        {"name": "Syktyvkar", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Tabuk", "color": "#def7c6", "owner_name": "Saudi Arabia"},
        {"name": "Tacna Moquegua", "color": "#fff6ff", "owner_name": "Peru"},
        {"name": "Taiwan", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Taklamakan", "color": "#3fb08d", "owner_name": "Sinkiang"},
        {"name": "Tamaulipas", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "Tambov", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Tanganyika", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Tannu Tuva", "color": "#e94a4a", "owner_name": "Tannu Tuva"},
        {"name": "Tartu", "color": "#63cdfe", "owner_name": "Estonia"},
        {"name": "Tashauz", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Tashkent", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Tasmania", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "Tehran", "color": "#5c927e", "owner_name": "Iran"},
        {"name": "Telemark", "color": "#623c3c", "owner_name": "Norway"},
        {"name": "Tennessee", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Texas", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "The Moluccas", "color": "#5b21e2", "owner_name": "Dutch East Indies"},
        {"name": "Thrace", "color": "#79ebff", "owner_name": "Kingdom of Greece"},
        {"name": "Thuringen", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Tibriz", "color": "#5c927e", "owner_name": "Iran"},
        {"name": "Ticino", "color": "#c15151", "owner_name": "Switzerland"},
        {"name": "Tierra del Fuego", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Tigray", "color": "#c3a5f5", "owner_name": "Ethiopia"},
        {"name": "Tikhvin", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Tlemcen", "color": "#4993ff", "owner_name": "France"},
        {"name": "Tobolsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Tocantins", "color": "#62bd52", "owner_name": "Second Brazilian Republic"},
        {"name": "Togo", "color": "#4993ff", "owner_name": "France"},
        {"name": "Tohoku", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Tokai", "color": "#fee8c8", "owner_name": "Japan"},
        {"name": "Tombouctou", "color": "#4993ff", "owner_name": "France"},
        {"name": "Tomsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Tonkin", "color": "#4993ff", "owner_name": "France"},
        {"name": "Toscana", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Trabzon", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Transdanubia", "color": "#ffa47f", "owner_name": "Kingdom of Hungary"},
        {"name": "Transvaal", "color": "#be96fa", "owner_name": "South Africa"},
        {"name": "Transylvania", "color": "#9e9e00", "owner_name": "Romania"},
        {"name": "Trentino", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Tripoli", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Tripolitania", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Troms", "color": "#623c3c", "owner_name": "Norway"},
        {"name": "Trondelag", "color": "#623c3c", "owner_name": "Norway"},
        {"name": "Tucuman", "color": "#bdccff", "owner_name": "Argentina"},
        {"name": "Tula", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Tunceli", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Tunisia", "color": "#4993ff", "owner_name": "France"},
        {"name": "Turku", "color": "#ffffff", "owner_name": "Finland"},
        {"name": "Tyrol", "color": "#a999f0", "owner_name": "Austria"},
        {"name": "Tyumen", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Ucayali", "color": "#fff6ff", "owner_name": "Peru"},
        {"name": "Udachny", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Udmurtia", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Ufa", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Uganda", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Ulaanbaatar", "color": "#5a771d", "owner_name": "Mongolia"},
        {"name": "Ulyanovsky", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Upper Austria", "color": "#a999f0", "owner_name": "Austria"},
        {"name": "Upper British Columbia", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Upper Nile", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Upper Volta", "color": "#4993ff", "owner_name": "France"},
        {"name": "Uralsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Uruguay", "color": "#abbe99", "owner_name": "Uruguay"},
        {"name": "Urumqi", "color": "#3fb08d", "owner_name": "Sinkiang"},
        {"name": "Ust Urt", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Utah", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Uusimaa", "color": "#ffffff", "owner_name": "Finland"},
        {"name": "Vaasa", "color": "#ffffff", "owner_name": "Finland"},
        {"name": "Valencia", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Valladolid", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Van", "color": "#c7e9b4", "owner_name": "Turkey"},
        {"name": "Vancouver Island", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Var", "color": "#4993ff", "owner_name": "France"},
        {"name": "Varmland", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "Vasterbotten", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "Vastergotland", "color": "#2eadff", "owner_name": "Sweden"},
        {"name": "Veneto", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Veracruz", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "Verkhoyansk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Vestlandet", "color": "#623c3c", "owner_name": "Norway"},
        {"name": "Victoria", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "Vidzeme", "color": "#7b7cb8", "owner_name": "Latvia"},
        {"name": "Vinnytsia", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Virginia", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Virumaa", "color": "#63cdfe", "owner_name": "Estonia"},
        {"name": "Vitebsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Vlaanderen", "color": "#fbdf0a", "owner_name": "Belgium"},
        {"name": "Vladivostok", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Vojvodina", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "Volgodonsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Volkhov", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Vologda", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Vorarlberg", "color": "#a999f0", "owner_name": "Austria"},
        {"name": "Voronezh", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Voroshilovgrad", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Vorpommern", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Wales", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Wallonie", "color": "#fbdf0a", "owner_name": "Belgium"},
        {"name": "Warszawa", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Washington", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Welega", "color": "#c3a5f5", "owner_name": "Ethiopia"},
        {"name": "Wello", "color": "#c3a5f5", "owner_name": "Ethiopia"},
        {"name": "Weser Ems", "color": "#525252", "owner_name": "German Reich"},
        {"name": "West Banat", "color": "#5e5ea4", "owner_name": "Yugoslavia"},
        {"name": "West Bengal", "color": "#c80a0a", "owner_name": "British Raj"},
        {"name": "West Midlands", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "West Papua", "color": "#5b21e2", "owner_name": "Dutch East Indies"},
        {"name": "West Virginia", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Western Aragon", "color": "#ffff79", "owner_name": "Spain"},
        {"name": "Western Australia", "color": "#49bb7e", "owner_name": "Australia"},
        {"name": "Western Desert", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Western Slovakia", "color": "#46d8cb", "owner_name": "Czechoslovakia"},
        {"name": "Western Swiss Alps", "color": "#c15151", "owner_name": "Switzerland"},
        {"name": "Westfalen", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Wilejka", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Wilno", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Wisconsin", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Wolyn", "color": "#ff7789", "owner_name": "Poland"},
        {"name": "Wurttemberg", "color": "#525252", "owner_name": "German Reich"},
        {"name": "Wyoming", "color": "#57a1ff", "owner_name": "United States"},
        {"name": "Xian", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Xikang", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Yakutsk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Yamalia", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Yarkand", "color": "#3fb08d", "owner_name": "Sinkiang"},
        {"name": "Yaroslavl", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Yemen", "color": "#905d5d", "owner_name": "Yemen"},
        {"name": "Yeniseisk", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Yorkshire", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Yucatan", "color": "#86c66c", "owner_name": "Mexico"},
        {"name": "Yukon Territory", "color": "#9b3e33", "owner_name": "Dominion of Canada"},
        {"name": "Yunnan", "color": "#698948", "owner_name": "Yunnan"},
        {"name": "Zambesi", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Zambezia Mocambique", "color": "#33965b", "owner_name": "Portugal"},
        {"name": "Zambia", "color": "#ff4879", "owner_name": "United Kingdom"},
        {"name": "Zaolzie", "color": "#46d8cb", "owner_name": "Czechoslovakia"},
        {"name": "Zaporozhe", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Zara", "color": "#56a552", "owner_name": "Italy"},
        {"name": "Zemaitija", "color": "#ffff9b", "owner_name": "Lithuania"},
        {"name": "Zemgale", "color": "#7b7cb8", "owner_name": "Latvia"},
        {"name": "Zhejiang", "color": "#dfe5a0", "owner_name": "China"},
        {"name": "Zhytomyr", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Zlatoust", "color": "#a3101f", "owner_name": "Soviet Union"},
        {"name": "Zulia", "color": "#70b626", "owner_name": "Venezuela"},
        {"name": "Zunyi", "color": "#dfe5a0", "owner_name": "China"},
    ]

    # Preload Nations for this game_id into a dict: name -> Nations instance
    nations_qs = Nations.objects.filter(game=game_id)
    nations_dict = {nation.name: nation for nation in nations_qs}

    map_obj = Map.objects.get(number=game_id, game__id=game_id)
    j = 0
    squares_to_create = []

    for data in squares_data:
        owner = nations_dict.get(data["owner_name"])
        if not owner:
            # handle missing owner if needed
            continue

        square = Square(
            map=map_obj,
            number=j,
            owner=owner,
            name=data["name"],
            color=data["color"],
        )
        squares_to_create.append(square)
        j += 1

    # Bulk create all squares in one DB hit
    Square.objects.bulk_create(squares_to_create)

    
    neighbors_data = [
    {"name": "Aberdeenshire", "neighbors": ["Lothian", "Lanark", "Scottish Highlands"]},
    {"name": "Abkhazia", "neighbors": ["Sochi", "Kabardino Balkaria", "Georgia"]},
    {"name": "Abruzzo", "neighbors": ["Puglia", "Campania", "Lazio", "Toscana", "Emilia Romagna"]},
    {"name": "Abu Dhabi", "neighbors": ["Oman", "Rub al Khali"]},
    {"name": "Acre", "neighbors": ["Ucayali", "Santa Cruz", "Amazon impassable 4", "Amazon impassable 3", "Amazonas"]},
    {"name": "Aden", "neighbors": ["Yemen", "Najiran", "Oman", "Rub al Khali"]},
    {"name": "Afar", "neighbors": ["French Somaliland", "Eritrea", "Tigray", "Wello", "Shewa", "Hararghe"]},
    {"name": "Afyon", "neighbors": ["Konya", "Ankara", "Bursa", "Izmir", "Antalya"]},
    {"name": "Agder", "neighbors": ["Telemark", "Vestlandet"]},
    {"name": "Akhtubinsk", "neighbors": ["Ust Urt", "Karakalpakstan", "Navoi", "Kyzyl Orda", "Karagandy", "Kostanay", "Magnitogorsk", "Orenburg", "Uralsk", "Guryev"]},
    {"name": "Akmolinsk", "neighbors": ["Chelyabinsk", "Tyumen", "Omsk", "Pavlodar", "Semipalatinsk", "Ayaguz", "Karagandy", "Kostanay"]},
    {"name": "Al Hajara", "neighbors": ["Kuwait", "Baghdad", "Mosul", "Deir az Zur", "Damascus", "Jordan", "Jawf", "Al Qassim", "Dammam"]},
    {"name": "Al Qassim", "neighbors": ["Kuwait", "Baghdad", "Jawf", "Tabuk", "Madinah", "Nejd", "Dammam"]},
    {"name": "Alabama", "neighbors": ["Florida", "Georgia US", "Tennessee", "Mississippi"]},
    {"name": "Alaska", "neighbors": ["Yukon Territory", "Upper British Columbia"]},
    {"name": "Albania", "neighbors": ["Shkoder", "Macedonia", "Northern Epirus"]},
    {"name": "Alberta", "neighbors": ["Northwest Territories", "Upper British Columbia", "British Columbia", "Montana", "Saskatchewan", "Northern Saskatchewan"]},
    {"name": "Aleppo", "neighbors": ["Hatay", "Malatya", "Deir az Zur", "Damascus", "Lebanon"]},
    {"name": "Alexandria", "neighbors": ["Cairo", "Western Desert", "Matrouh"]},
    {"name": "Alfold", "neighbors": ["Transdanubia", "Northern Hungary", "Southern Slovakia", "Carpathian Ruthenia", "North Transylvania", "Crisana", "Banat", "West Banat", "Vojvodina"]},
    {"name": "Algerian Desert", "neighbors": ["Gabes", "Tlemcen", "Marrakech", "Rio de Oro", "Mauritanian Desert", "Tombouctou", "Southern Sahara", "Libyan Desert"]},
    {"name": "Algiers", "neighbors": ["Constantine", "Tlemcen", "Casablanca", "Spanish Africa"]},
    {"name": "Alma Ata", "neighbors": ["Ayaguz", "Karagandy", "Kyzyl Orda", "Pamir", "Urumqi"]},
    {"name": "Alpes", "neighbors": ["Rhone", "Savoy", "Bouches du Rhone"]},
    {"name": "Alsace Lorraine", "neighbors": ["Wallonie", "Luxembourg", "Moselland", "Wurttemberg", "Jura Mountains", "Franche Comte", "Champagne"]},
    {"name": "Altai Krai", "neighbors": ["Semipalatinsk", "Oyrot Region", "Khakassia", "Novosibirsk", "Pavlodar"]},
    {"name": "Alto Adige", "neighbors": ["Veneto", "Tyrol", "Vorarlberg", "Eastern Swiss Alps", "Lombardia", "Trentino"]},
    {"name": "Amapa", "neighbors": ["Para", "French Guiana", "Amazon impassable 8"]},
    {"name": "Amasya", "neighbors": ["Kayseri", "Sivas", "Samsun", "Kastamonu", "Ankara", "Konya"]},
    {"name": "Amazon impassable 1", "neighbors": ["Meta", "Amazonas"]},
    {"name": "Amazon impassable 2", "neighbors": ["Amazonas"]},
    {"name": "Amazon impassable 3", "neighbors": ["Acre", "Amazonas", "Santa Cruz"]},
    {"name": "Amazon impassable 4", "neighbors": ["Ucayali", "Loreto", "Amazonas", "Acre"]},
    {"name": "Amazon impassable 5", "neighbors": ["Guapore", "Mato Grosso", "Amazonas"]},
    {"name": "Amazon impassable 6", "neighbors": ["Amazonas", "Mato Grosso", "Para"]},
    {"name": "Amazon impassable 7", "neighbors": ["Rio Branco", "Bolivar", "Amazonas"]},
    {"name": "Amazon impassable 8", "neighbors": ["Amazonas", "Para", "Rio Branco", "Suriname", "Amapa", "British Guyana", "French Guiana"]},
    {"name": "Amazonas", "neighbors": ["Amazon impassable 1", "Amazon impassable 2", "Amazon impassable 3", "Amazon impassable 4", "Amazon impassable 5", "Amazon impassable 6", "Amazon impassable 7", "Amazon impassable 8", "Rio Branco", "Bolivar", "Meta", "Loreto", "Acre", "Santa Cruz", "Guapore", "Mato Grosso", "Para"]},
    {"name": "Amur", "neighbors": ["Okhotsk", "Yakutsk", "Chita", "Hulunbuir", "Heilungkiang", "Birobidzhan", "Nikolayevsk"]},
    {"name": "Anhui", "neighbors": ["Huangshan", "Shanghai", "Jiangsu", "Henan", "Hubei"]},
    {"name": "Ankara", "neighbors": ["Amasya", "Kastamonu", "Izmit", "Bursa", "Afyon", "Konya"]},
    {"name": "Antalya", "neighbors": ["Mersin", "Konya", "Afyon", "Izmir"]},
    {"name": "Antofagasta", "neighbors": ["Tucuman", "Atacama", "La Paz", "Los Andes", "Arica y Tarapaca"]},
    {"name": "Aquitaine", "neighbors": ["Pyrenees Atlantiques", "Midi Pyrenees", "Limousin", "Poitou"]},
    {"name": "Araucania", "neighbors": ["Aysen", "Chubut", "Rio Negro", "Santiago"]},
    {"name": "Arequipa", "neighbors": ["Lima", "Ucayali", "La Paz", "Tacna Moquegua"]},
    {"name": "Arica y Tarapaca", "neighbors": ["Antofagasta", "La Paz", "Tacna Moquegua"]},
    {"name": "Arizona", "neighbors": ["Sonora", "New Mexico", "Colorado", "Utah", "Nevada", "California", "Baja California"]},
    {"name": "Arkansas", "neighbors": ["Tennessee", "Missouri", "Oklahoma", "Texas", "Louisiana"]},
    {"name": "Arkhangelsk", "neighbors": ["Onega", "Kargopol", "Kotlas", "Pechora", "Nenets"]},
    {"name": "Armenia", "neighbors": ["Georgia", "Azerbaijan", "Tibriz", "Van", "Trabzon"]},
    {"name": "Arunachal Pradesh", "neighbors": ["Assam", "Mandalay", "Xikang", "Shigatse", "Bhutan"]},
    {"name": "Ashkhabad", "neighbors": ["Ust Urt", "Karakalpakstan", "Tashauz", "Bukhara", "Kabul", "Herat", "Khorasan", "Tehran"]},
    {"name": "Asir Makkah", "neighbors": ["Madinah", "Nejd", "Najiran", "Yemen"]},
    {"name": "Assam", "neighbors": ["East Bengal", "West Bengal", "Bhutan", "Arunachal Pradesh", "Mandalay", "Burma"]},
    {"name": "Astrakhan", "neighbors": ["Guryev", "Uralsk", "Stalingrad", "Kalmykia"]},
    {"name": "Asturias", "neighbors": ["Galicia", "Leon", "Valladolid", "Burgos", "Pais Vasco"]},
    {"name": "Aswan", "neighbors": ["Eastern Desert", "Western Desert", "Cairo", "Khartoum"]},
    {"name": "Atacama", "neighbors": ["Santiago", "Antofagasta", "Tucuman", "San Juan y La Rioja"]},
    {"name": "Attica", "neighbors": ["Peloponnese", "Epirus", "Central Macedonia"]},
    {"name": "Aukstaitija", "neighbors": ["Kaunas", "Wilno", "Zemgale", "Zemaitija"]},
    {"name": "Auvergne", "neighbors": ["Languedoc", "Rhone", "Bourgogne", "Centre", "Centre Sud", "Limousin"]},
    {"name": "Ayaguz", "neighbors": ["Karagandy", "Akmolinsk", "Semipalatinsk", "Dzungaria", "Urumqi", "Alma Ata"]},
    {"name": "Aysen", "neighbors": ["Araucania", "Santa Cruz AR", "Chubut", "Magallanes"]},
    {"name": "Azerbaijan", "neighbors": ["Dagestan", "Georgia", "Armenia", "Tibriz", "Gilan"]},
    {"name": "Baghdad", "neighbors": ["Kuwait", "Kurdistan", "Al Hajara", "Mosul", "Khuzestan"]},
    {"name": "Bahia", "neighbors": ["Piaui", "Pernambuco", "Minas Gerais", "Espirito Santo", "Tocantins"]},
    {"name": "Bahr al Ghazal", "neighbors": ["Stanleyville", "Uganda", "Upper Nile", "Kurdufan", "Equatorial Africa", "South Darfur"]},
    {"name": "Baja California", "neighbors": ["California", "Arizona", "Sonora"]},
    {"name": "Balakovo", "neighbors": ["Uralsk", "Orenburg", "Engels Marxstadt", "Kuybyshev", "Saratov"]},
    {"name": "Bale", "neighbors": ["Somaliland", "Jubaland", "Hararghe", "Sidamo", "Shewa"]},
    {"name": "Balta Tiraspol", "neighbors": ["Bessarabia", "Odessa", "Southern Bessarabia", "Cherkasy", "Vinnytsia"]},
    {"name": "Baluchistan", "neighbors": ["Sind", "Quetta", "Herat", "Kerman", "Sistan"]},
    {"name": "Bamako", "neighbors": ["Guinea", "Ivory Coast", "Upper Volta", "Gao", "Kayes Koulikoro"]},
    {"name": "Banat", "neighbors": ["West Banat", "Transylvania", "Crisana", "Alfold", "Serbia", "Morava", "Oltenia"]},
    {"name": "Bechuanaland", "neighbors": ["Khomas", "Karas", "Cape", "Transvaal", "Zambia", "Rhodesia", "Otjozondjupa"]},
    {"name": "Begemder", "neighbors": ["Gojjam", "Blue Nile", "Wello", "Eritrea", "Tigray", "Kassala"]},
    {"name": "Beijing", "neighbors": ["Hebei", "Shanxi", "East Hebei", "Jehol", "South Chahar"]},
    {"name": "Beja", "neighbors": ["Lisbon", "Sevilla", "Extremadura", "Santarem"]},
    {"name": "Belgorod", "neighbors": ["Kursk", "Kharkov", "Sumy", "Voronezh", "Voroshilovgrad"]},
    {"name": "Benghasi", "neighbors": ["Derna", "Sirte", "Cyrenaica", "El Agheila"]},
    {"name": "Benue", "neighbors": ["Cameroon", "Borno", "Sokoto", "Lagos"]},
    {"name": "Bessarabia", "neighbors": ["Moldova", "Southern Bessarabia", "Muntenia", "Balta Tiraspol", "Vinnytsia", "Lwow", "Bucovina", "Khmelnytskyi"]},
    {"name": "Bhutan", "neighbors": ["West Bengal", "East Bengal", "Assam", "Arunachal Pradesh", "Shigatse"]},
    {"name": "Bialystok", "neighbors": ["Konigsberg", "Suduva", "Nowogrodek", "Polesie", "Lublin", "Plock", "Warszawa", "Ermland Masuren"]},
    {"name": "Bihar", "neighbors": ["West Bengal", "Nepal", "Lucknow", "Jabalpur", "Orissa"]},
    {"name": "Birobidzhan", "neighbors": ["Nikolayevsk", "Khabarovsk", "Sungkiang", "Heilungkiang", "Amur"]},
    {"name": "Bismarck", "neighbors": []},
    {"name": "Blue Nile", "neighbors": ["Upper Nile", "Kurdufan", "Kassala", "Welega", "Gojjam", "Begemder", "Khartoum"]},
    {"name": "Bobruysk", "neighbors": ["Minsk", "Gomel", "Mozyr", "Polesie", "Nowogrodek"]},
    {"name": "Bodaybo", "neighbors": ["Yakutsk", "Chita", "Buryatia", "Kirensk"]},
    {"name": "Bohemia", "neighbors": ["Sudetenland", "Eastern Sudetenland", "Moravia", "Niederschlesien"]},
    {"name": "Bohuslan", "neighbors": ["Oslofjord", "Varmland", "Vastergotland"]},
    {"name": "Bolivar", "neighbors": ["Miranda", "Meta", "Amazonas", "Rio Branco", "British Guyana", "Amazon impassable 7"]},
    {"name": "Bombay", "neighbors": ["Gujarat", "Indore", "Jabalpur", "Hyderabad", "Mysore"]},
    {"name": "Borkou Ennedi Tibesti", "neighbors": ["Libyan Desert", "North Darfur", "South Darfur", "Chad", "Southern Sahara"]},
    {"name": "Borno", "neighbors": ["Sokoto", "Benue", "Southern Sahara", "Cameroon"]},
    {"name": "Bosnia", "neighbors": ["Croatia", "Dalmatia", "Herzegovina", "Montenegro", "Morava", "Serbia"]},
    {"name": "Bouches du Rhone", "neighbors": ["Alpes", "Savoy", "Rhone", "Var", "Languedoc"]},
    {"name": "Bourgogne", "neighbors": ["Champagne", "Ile de France", "Centre", "Centre Sud", "Auvergne", "Rhone", "Franche Comte"]},
    {"name": "Brabant", "neighbors": ["Rhineland", "Friesland", "Holland", "Wallonie", "Vlaanderen"]},
    {"name": "Brandenburg", "neighbors": ["Hannover", "Ostmark", "Vorpommern", "Mecklenburg", "Thuringen", "Sachsen"]},
    {"name": "Bratsk", "neighbors": ["Kirensk", "Yeniseisk", "Krasnoyarsk", "Tannu Tuva", "Buryatia", "Irkutsk"]},
    {"name": "British Columbia", "neighbors": ["Idaho", "Washington", "Montana", "Alberta", "Upper British Columbia"]},
    {"name": "British Guyana", "neighbors": ["Bolivar", "Rio Branco", "Suriname", "Amazon impassable 8"]},
    {"name": "British Honduras", "neighbors": ["Guatemala", "Yucatan"]},
    {"name": "British Somaliland", "neighbors": ["Somaliland", "French Somaliland", "Hararghe"]},
    {"name": "Brittany", "neighbors": ["Normandy", "Loire", "Poitou"]},
    {"name": "Bryansk", "neighbors": ["Gomel", "Roslavl", "Kaluga", "Kursk", "Orel", "Sumy", "Chernigov"]},
    {"name": "Bucovina", "neighbors": ["Moldova", "North Transylvania", "Stanislawow", "Lwow"]},
    {"name": "Bukhara", "neighbors": ["Navoi", "Tashkent", "Stalinabad", "Tashkent", "Ashkhabad", "Tashauz"]},
    {"name": "Burgas", "neighbors": ["Moesia", "Edirne", "Dobrudja", "Thrace", "Plovdiv"]},
    {"name": "Burgos", "neighbors": ["Asturias", "Navarra", "Western Aragon", "Guadalajara", "Madrid", "Valladolid"]},
    {"name": "Burma", "neighbors": ["Northern Malay", "Siam", "Lanna", "Mandalay", "Assam", "East Bengal"]},
    {"name": "Bursa", "neighbors": ["Istanbul", "Izmir", "Ankara", "Afyon", "Izmit"]},
    {"name": "Burundi", "neighbors": ["Costermansville", "Rwanda", "Tanganyika"]},
    {"name": "Buryatia", "neighbors": ["Chita", "Bodaybo", "Kirensk", "Ulaanbaatar", "Khovsgol", "Tannu Tuva", "Irkutsk", "Bratsk"]},
    {"name": "Cairo", "neighbors": ["Aswan", "Suez", "Eastern Desert", "Alexandria"]},
    {"name": "Calabria", "neighbors": ["Campania"]},
    {"name": "California", "neighbors": ["Arizona", "Oregon", "Nevada", "Baja California"]},
    {"name": "Cambodia", "neighbors": ["Siam", "Isan", "Laos", "Southern Indochina"]},
    {"name": "Cameroon", "neighbors": ["Benue", "Borno", "Chad", "Gabon", "Middle Congo", "Equatorial Africa", "Equatorial Guinea"]},
    {"name": "Campania", "neighbors": ["Lazio", "Abruzzo", "Puglia", "Calabria"]},
    {"name": "Cape", "neighbors": ["Karas", "Natal", "Transvaal", "Bechuanaland"]},
    {"name": "Carpathian Ruthenia", "neighbors": ["Stanislawow", "Alfold", "North Transylvania", "Krakow", "Southern Slovakia", "Eastern Slovakia"]},
    {"name": "Casablanca", "neighbors": ["Spanish Africa", "Algiers", "Tlemcen", "Marrakech"]},
    {"name": "Cataluna", "neighbors": ["Eastern Aragon", "Valencia", "Midi Pyrenees"]},
    {"name": "Ceara", "neighbors": ["Piaui", "Pernambuco", "Rio Grande do Norte"]},
    {"name": "Cebu", "neighbors": []},
    {"name": "Central Australia", "neighbors": ["New South Wales", "Southwest Queensland", "Queensland", "North Queensland", "Northern Territory", "South Australia", "South West Australia", "Western Australia", "North West Australia"]},
    {"name": "Central Islands", "neighbors": ["Manila"]},
    {"name": "Central Macedonia", "neighbors": ["Attica", "Epirus", "Macedonia", "Plovdiv", "Thrace"]},
    {"name": "Centre", "neighbors": ["Centre Sud", "Loire", "Poitou", "Ile de France", "Bourgogne"]},
    {"name": "Centre Sud", "neighbors": ["Centre", "Poitou", "Limousin", "Auvergne"]},
    {"name": "Cerro Largo", "neighbors": ["Paysandu", "Rio Grande do Sul", "Uruguay"]},
    {"name": "Ceylon", "neighbors": []},
    {"name": "Chaco Austral", "neighbors": ["Formosa", "Paraguay", "Mesopotamia", "Region Mesopotamica", "San Luis y La Pampa", "San Juan y La Rioja", "Tucuman", "Los Andes"]},
    {"name": "Chaco Boreal", "neighbors": ["Formosa", "Paraguay", "La Paz", "Santa Cruz", "Punta Pora"]},
    {"name": "Chad", "neighbors": ["Southern Sahara", "Cameroon", "South Darfur", "Equatorial Africa", "Borkou Ennedi Tibesti"]},
    {"name": "Chahar", "neighbors": ["Jehol", "Dornod", "South Chahar", "Gobi", "Suiyuan", "Liaoning", "Hulunbuir", "Heilungkiang"]},
    {"name": "Champagne", "neighbors": ["Alsace Lorraine", "Franche Comte", "Bourgogne", "Ile de France", "Picardy", "Wallonie"]},
    {"name": "Changde", "neighbors": ["Sichuan", "Zunyi", "Hunan", "Hubei", "Guizhou"]},
    {"name": "Chechnya Ingushetia", "neighbors": ["Georgia", "North Ossetia", "Dagestan", "Stavropol"]},
    {"name": "Chelyabinsk", "neighbors": ["Zlatoust", "Kostanay", "Tyumen", "Akmolinsk", "Sverdlovsk", "Magnitogorsk"]},
    {"name": "Cherkasy", "neighbors": ["Odessa", "Kyiv", "Poltava", "Vinnytsia", "Chernigov", "Balta Tiraspol", "Mykolaiv", "Dnipropetrovsk"]},
    {"name": "Chernigov", "neighbors": ["Cherkasy", "Kyiv", "Mozyr", "Gomel", "Poltava", "Sumy", "Bryansk"]},
    {"name": "Chiapas", "neighbors": ["Oaxaca", "Yucatan", "Guatemala"]},
    {"name": "Chihuahua", "neighbors": ["Sonora", "Texas", "New Mexico", "Coahuila", "Durango"]},
    {"name": "Chita", "neighbors": ["Amur", "Hulunbuir", "Dornod", "Ulaanbaatar", "Buryatia", "Bodaybo", "Yakutsk"]},
    {"name": "Chubut", "neighbors": ["Araucania", "Aysen", "Rio Negro", "Santa Cruz AR"]},
    {"name": "Chugoku", "neighbors": ["Kansai"]},
    {"name": "Chukchi Peninsula", "neighbors": []},
    {"name": "Chukotka", "neighbors": ["Kolyma", "Kamchatka", "Magadan"]},
    {"name": "Chuvashia", "neighbors": ["Mari El", "Kazan", "Ulyanovsky", "Gorky"]},
    {"name": "Ciudad Real", "neighbors": ["Murcia", "Guadalajara", "Madrid", "Extremadura", "Cordoba"]},
    {"name": "Coahuila", "neighbors": ["Tamaulipas", "Texas", "Durango", "Chihuahua"]},
    {"name": "Colorado", "neighbors": ["Wyoming", "Nebraska", "Kansas", "Oklahoma", "New Mexico", "Arizona", "Utah"]},
    {"name": "Connaught", "neighbors": ["Northern Ireland", "Leinster", "Munster"]},
    {"name": "Constantine", "neighbors": ["Tunisia", "Tlemcen", "Algiers"]},
    {"name": "Coquilhatville", "neighbors": ["Equatorial Africa", "Stanleyville", "Costermansville", "Lusambo", "Leopoldville", "Middle Congo"]},
    {"name": "Cordoba", "neighbors": ["Granada", "Murcia", "Ciudad Real", "Extremadura", "Sevilla"]},
    {"name": "Corsica", "neighbors": []},
    {"name": "Costa Rica", "neighbors": ["Nicaragua", "Panama"]},
    {"name": "Costermansville", "neighbors": ["Stanleyville", "Coquilhatville", "Lusambo", "Elisabethville", "Tanganyika", "Burundi", "Rwanda", "Uganda"]},
    {"name": "Cote Nord", "neighbors": ["Nord du Quebec", "Labrador", "Saguenay", "Maurice"]},
    {"name": "Crimea", "neighbors": ["Kherson"]},
    {"name": "Crisana", "neighbors": ["Alfold", "Banat", "Transylvania", "North Transylvania"]},
    {"name": "Croatia", "neighbors": ["Bosnia", "Serbia", "West Banat", "Vojvodina", "Transdanubia", "North Slovenia", "Ljubljana", "Dalmatia"]},
    {"name": "Cuba", "neighbors": []},
    {"name": "Cumbria", "neighbors": ["Lancashire", "Yorkshire", "Northumberland", "Lothian", "Lanark"]},
    {"name": "Cundinamarca", "neighbors": ["Ecuador", "Zulia", "Miranda", "Meta", "La Libertad"]},
    {"name": "Cyprus", "neighbors": []},
    {"name": "Cyrenaica", "neighbors": ["Matrouh", "Derna", "Benghasi", "Sirte", "Libyan Desert"]},
    {"name": "Dabancheng", "neighbors": ["Kunlun Shan", "Jiuquan", "Gobi", "Khovd", "Dzungaria", "Urumqi"]},
    {"name": "Dagestan", "neighbors": ["Azerbaijan", "Georgia", "Chechnya Ingushetia", "Stavropol", "Kalmykia"]},
    {"name": "Dahomey", "neighbors": ["Togo", "Upper Volta", "Niger", "Lagos"]},
    {"name": "Dalarna", "neighbors": ["Sodermalm", "Gavleborg", "Jamtland", "Trondelag", "Opplandene", "Varmland"]},
    {"name": "Dali", "neighbors": ["Mandalay", "Laos", "Yunnan", "Liangshan", "Ganzi", "Xikang"]},
    {"name": "Dalian", "neighbors": ["Liaotung"]},
    {"name": "Dalmatia", "neighbors": ["Montenegro", "Herzegovina", "Bosnia", "Croatia", "Ljubljana", "Litorale", "Istria"]},
    {"name": "Damascus", "neighbors": ["Deir az Zur", "Aleppo", "Lebanon", "Palestine", "Jordan"]},
    {"name": "Dammam", "neighbors": ["Qatar", "Rub al Khali", "Nejd", "Al Qassim", "Kuwait"]},
    {"name": "Danzig", "neighbors": ["Ermland Masuren", "Gdynia"]},
    {"name": "Deir az Zur", "neighbors": ["Diyarbakir", "Hakkari", "Mosul", "Al Hajara", "Jordan", "Damascus", "Aleppo"]},
    {"name": "Delhi", "neighbors": ["Kashmir", "Ngari", "Nepal", "Lucknow", "Rajahsthan", "Punjab"]},
    {"name": "Derna", "neighbors": ["Benghasi", "Cyrenaica", "Matrouh"]},
    {"name": "Districts of Ontario", "neighbors": ["Manitoba", "Northern Manitoba", "Northern Ontario"]},
    {"name": "Diyarbakir", "neighbors": ["Hakkari", "Tunceli", "Malatya", "Aleppo", "Deir az Zur"]},
    {"name": "Dnipropetrovsk", "neighbors": ["Stalino", "Kharkov", "Poltava", "Cherkasy", "Mykolaiv", "Kherson", "Zaporozhe"]},
    {"name": "Dobrudja", "neighbors": ["Burgas", "Moesia", "Muntenia"]},
    {"name": "Dominican Republic", "neighbors": ["Haiti"]},
    {"name": "Dornod", "neighbors": ["Gobi", "Chahar", "Hulunbuir", "Chita", "Ulaanbaatar"]},
    {"name": "Dudinka", "neighbors": ["Yamalia", "Surgut", "Yeniseisk", "Khatangsky"]},
    {"name": "Durango", "neighbors": ["Sonora", "Chihuahua", "Coahuila", "Tamaulipas", "Jalisco"]},
    {"name": "Dzungaria", "neighbors": ["Oyrot Region", "Khovd", "Dabancheng", "Urumqi", "Ayaguz", "Semipalatinsk"]},
    {"name": "East Anglia", "neighbors": ["East Midlands", "Greater London Area"]},
    {"name": "East Bengal", "neighbors": ["West Bengal", "Assam", "Burma"]},
    {"name": "East Hebei", "neighbors": ["Jehol", "Beijing"]},
    {"name": "East Midlands", "neighbors": ["East Anglia", "Greater London Area", "Gloucestershire", "West Midlands", "Yorkshire"]},
    {"name": "Easter Island", "neighbors": []},
    {"name": "Eastern Aragon", "neighbors": ["Midi Pyrenees", "Cataluna", "Valencia", "Guadalajara", "Western Aragon"]},
    {"name": "Eastern Desert", "neighbors": ["Kassala", "Khartoum", "Aswan", "Cairo", "Suez"]},
    {"name": "Eastern Slovakia", "neighbors": ["Zaolzie", "Krakow", "Carpathian Ruthenia", "Southern Slovakia", "Western Slovakia"]},
    {"name": "Eastern Sudetenland", "neighbors": ["Niederschlesien", "Oberschlesien", "Katowice", "Zaolzie", "Moravia", "Bohemia"]},
    {"name": "Eastern Swiss Alps", "neighbors": ["Ticino", "Lombardia", "Alto Adige", "Tyrol", "Vorarlberg", "Swiss Plateau", "Western Swiss Alps"]},
    {"name": "Ecuador", "neighbors": ["Cundinamarca", "Meta", "Lima", "Loreto", "Pastaza"]},
    {"name": "Edirne", "neighbors": ["Thrace", "Burgas", "Istanbul"]},
    {"name": "El Agheila", "neighbors": ["Benghasi", "Sirte", "Tripolitania", "Tripoli"]},
    {"name": "El Salvador", "neighbors": ["Guatemala", "Honduras"]},
    {"name": "Elisabethville", "neighbors": ["Costermansville", "Lusambo", "Luanda", "Zambesi", "Zambia", "Tanganyika"]},
    {"name": "Emilia Romagna", "neighbors": ["Abruzzo", "Toscana", "Piemonte", "Lombardia", "Veneto"]},
    {"name": "Engels Marxstadt", "neighbors": ["Saratov", "Balakovo", "Uralsk", "Stalingrad", "Mikhaylovka"]},
    {"name": "Epirus", "neighbors": ["Northern Epirus", "Macedonia", "Central Macedonia", "Attica"]},
    {"name": "Equatorial Africa", "neighbors": ["Uganda", "Stanleyville", "Coquilhatville", "Middle Congo", "Cameroon", "Chad", "South Darfur", "Kurdufan", "Upper Nile"]},
    {"name": "Equatorial Guinea", "neighbors": ["Cameroon", "Gabon"]},
    {"name": "Eritrea", "neighbors": ["Kassala", "Begemder", "Tigray", "Afar", "French Somaliland"]},
    {"name": "Ermland Masuren", "neighbors": ["Konigsberg", "Bialystok", "Plock", "Gdynia", "Danzig"]},
    {"name": "Espirito Santo", "neighbors": ["Minas Gerais", "Rio de Janeiro", "Bahia"]},
    {"name": "Extremadura", "neighbors": ["Salamanca", "Madrid", "Ciudad Real", "Cordoba", "Sevilla", "Beja", "Santarem", "Guarda"]},
    {"name": "Fars", "neighbors": ["Khuzestan", "Isfahan", "Kerman", "Sistan"]},
    {"name": "Finnmark", "neighbors": ["Troms", "Lappi", "Petsamo"]},
    {"name": "Florida", "neighbors": ["Mississippi", "Alabama", "Georgia US"]},
    {"name": "Formosa", "neighbors": ["Chaco Boreal", "Chaco Austral", "La Paz", "Los Andes", "Paraguay"]},
    {"name": "Franche Comte", "neighbors": ["Alsace Lorraine", "Champagne", "Bourgogne", "Rhone", "Jura Mountains"]},
    {"name": "Franken", "neighbors": ["Sudetenland", "Sachsen", "Thuringen", "Hessen", "Wurttemberg", "Oberbayern", "Niederbayern"]},
    {"name": "French Guiana", "neighbors": ["Suriname", "Amapa", "Amazon impassable 8"]},
    {"name": "French India", "neighbors": ["Madurai"]},
    {"name": "French Somaliland", "neighbors": ["British Somaliland", "Hararghe", "Afar", "Eritrea"]},
    {"name": "Friesland", "neighbors": ["Weser Ems", "Westfalen", "Rhineland", "Brabant", "Holland"]},
    {"name": "Fujian", "neighbors": ["Zhejiang", "Jiangxi", "Guangdong"]},
    {"name": "Gabes", "neighbors": ["Tunisia", "Tlemcen", "Algerian Desert", "Libyan Desert", "Tripolitania", "Tripoli"]},
    {"name": "Gabon", "neighbors": ["Middle Congo", "Cameroon", "Equatorial Guinea"]},
    {"name": "Galicia", "neighbors": ["Asturias", "Leon", "Porto"]},
    {"name": "Gambia", "neighbors": ["Senegal"]},
    {"name": "Gannan", "neighbors": ["Gansu", "Golog", "Ganzi", "Liangshan", "Sichuan"]},
    {"name": "Gansu", "neighbors": ["Ningxia", "Shaanxi", "Xian", "Sichuan", "Gannan", "Golog"]},
    {"name": "Ganzi", "neighbors": ["Dali", "Liangshan", "Gannan", "Golog", "Xikang"]},
    {"name": "Gao", "neighbors": ["Tombouctou", "Mauritanian Desert", "Kayes Koulikoro", "Bamako", "Upper Volta", "Niger", "Southern Sahara"]},
    {"name": "Garissa", "neighbors": ["Mombasa", "Nairobi", "Sidamo", "Jubaland"]},
    {"name": "Gavleborg", "neighbors": ["Sodermalm", "Dalarna", "Jamtland", "Vasterbotten"]},
    {"name": "Gdynia", "neighbors": ["Danzig", "Ermland Masuren", "Plock", "Lodz", "Poznan", "Hinterpommern"]},
    {"name": "Georgia", "neighbors": ["Abkhazia", "Kabardino Balkaria", "North Ossetia", "Chechnya Ingushetia", "Dagestan", "Azerbaijan", "Armenia", "Trabzon"]},
    {"name": "Georgia US", "neighbors": ["Florida", "Alabama", "Tennessee", "North Carolina", "South Carolina"]},
    {"name": "Ghana", "neighbors": ["Ivory Coast", "Upper Volta", "Togo"]},
    {"name": "Gibraltar", "neighbors": ["Granada", "Sevilla"]},
    {"name": "Gilan", "neighbors": ["Tehran", "Hamadan", "Kurdistan", "Tibriz", "Azerbaijan"]},
    {"name": "Gloucestershire", "neighbors": ["Wales", "East Midlands", "West Midlands", "Greater London Area", "Sussex", "South West England"]},
    {"name": "Goa", "neighbors": ["Mysore"]},
    {"name": "Gobi", "neighbors": ["Chahar", "Dornod", "Ulaanbaatar", "Khovd", "Dabancheng", "Jiuquan", "Suiyuan"]},
    {"name": "Goias", "neighbors": ["Mato Grosso", "Tocantins", "Minas Gerais"]},
    {"name": "Gojjam", "neighbors": ["Wello", "Shewa", "Welega", "Blue Nile", "Begemder"]},
    {"name": "Golog", "neighbors": ["Ganzi", "Gannan", "Gansu", "Ningxia", "Haixi", "Qinghai", "Xikang"]},
    {"name": "Gomel", "neighbors": ["Chernigov", "Bryansk", "Roslavl", "Vitebsk", "Minsk", "Bobruysk", "Mozyr", "Smolensk"]},
    {"name": "Gorky", "neighbors": ["Ulyanovsky", "Chuvashia", "Mari El", "Kirov", "Vologda", "Ivanovo", "Ryazan", "Penza"]},
    {"name": "Gotland", "neighbors": []},
    {"name": "Granada", "neighbors": ["Gibraltar", "Sevilla", "Cordoba", "Murcia"]},
    {"name": "Greater London Area", "neighbors": ["Sussex", "Gloucestershire", "East Midlands", "East Anglia"]},
    {"name": "Greenland", "neighbors": []},
    {"name": "Guadalajara", "neighbors": ["Valladolid", "Madrid", "Ciudad Real", "Burgos", "Valencia", "Murcia", "Western Aragon", "Eastern Aragon"]},
    {"name": "Guangdong", "neighbors": ["Hunan", "Jiangxi", "Fujian", "Guangxi", "Guangzhou"]},
    {"name": "Guangxi", "neighbors": ["Yunnan", "Hunan", "Tonkin", "Nanning", "Guangzhou", "Guangdong", "Guizhou"]},
    {"name": "Guangzhou", "neighbors": ["Guangxi", "Guangdong", "Nanning", "Guangzhouwan"]},
    {"name": "Guangzhouwan", "neighbors": ["Guangzhou", "Nanning", "Hainan"]},
    {"name": "Guapore", "neighbors": ["Amazonas", "Santa Cruz", "Mato Grosso", "Amazon impassable 5"]},
    {"name": "Guarda", "neighbors": ["Lisbon", "Porto", "Salamanca", "Santarem", "Extremadura"]},
    {"name": "Guatemala", "neighbors": ["El Salvador", "Honduras", "British Honduras", "Yucatan", "Chiapas"]},
    {"name": "Guerrero", "neighbors": ["Jalisco", "Oaxaca", "Mexico City", "Veracruz"]},
    {"name": "Guinea", "neighbors": ["Sierra Leone", "Senegal", "Liberia", "Ivory Coast", "Bamako", "Kayes Koulikoro", "Portuguese Guinea"]},
    {"name": "Guizhou", "neighbors": ["Yunnan", "Guangxi", "Hunan", "Changde", "Zunyi", "Liangshan"]},
    {"name": "Gujarat", "neighbors": ["Bombay", "Indore", "Sind", "Rajahsthan"]},
    {"name": "Guryev", "neighbors": ["Uralsk", "Ust Urt", "Astrakhan", "Akhtubinsk"]},
    {"name": "Haida Gwaii", "neighbors": []},
    {"name": "Hainan", "neighbors": ["Nanning", "Guangzhou", "Guangzhouwan"]},
    {"name": "Haiti", "neighbors": ["Dominican Republic"]},
    {"name": "Haixi", "neighbors": ["Qinghai", "Golog", "Ningxia", "Jiuquan", "Kunlun Shan"]},
    {"name": "Hakkari", "neighbors": ["Tunceli", "Van", "Tibriz", "Mosul", "Deir az Zur", "Diyarbakir"]},
    {"name": "Hamadan", "neighbors": ["Gilan", "Tehran", "Semnan", "Isfahan", "Khuzestan", "Kurdistan"]},
    {"name": "Hame", "neighbors": ["Turku", "Vaasa", "Uusimaa", "Mikkeli"]},
    {"name": "Hannover", "neighbors": ["Mecklenburg", "Brandenburg", "Hessen", "Westfalen", "Weser Ems", "Holstein"]},
    {"name": "Hararghe", "neighbors": ["Shewa", "Bale", "Afar", "Somaliland", "French Somaliland", "British Somaliland"]},
    {"name": "Harju", "neighbors": ["Para", "Virumaa"]},
    {"name": "Hatay", "neighbors": ["Aleppo", "Malatya"]},
    {"name": "Hawaii", "neighbors": []},
    {"name": "Hebei", "neighbors": ["Shandong", "Henan", "Shanxi", "Beijing"]},
    {"name": "Heilungkiang", "neighbors": ["Chahar", "Kirin", "Amur", "Hulunbuir", "Liaoning", "Sungkiang", "Birobidzhan"]},
    {"name": "Helgeland", "neighbors": ["Nordland", "Trondelag", "Jamtland", "Vasterbotten"]},
    {"name": "Henan", "neighbors": ["Hebei", "Hubei", "Anhui", "Shaanxi", "Shanxi", "Xian", "Jiangsu", "Shandong"]},
    {"name": "Herat", "neighbors": ["Kerman", "Quetta", "Kabul", "Peshawar", "Baluchistan", "Khorasan", "Ashkhabad"]},
    {"name": "Herzegovina", "neighbors": ["Dalmatia", "Bosnia", "Montenegro"]},
    {"name": "Hessen", "neighbors": ["Rhineland", "Westfalen", "Hannover", "Franken", "Moselland", "Thuringen", "Wurttemberg"]},
    {"name": "Hinterpommern", "neighbors": ["Vorpommern", "Ostmark", "Poznan", "Gdynia"]},
    {"name": "Hokkaido", "neighbors": ["Hokkaido"]},
    {"name": "Hokuriku", "neighbors": ["Koshinetsu", "Kanto", "Tohoku"]},
    {"name": "Holland", "neighbors": ["Brabant", "Friesland"]},
    {"name": "Holstein", "neighbors": ["Hannover", "Mecklenburg", "Schleswig"]},
    {"name": "Honduras", "neighbors": ["El Salvador", "Nicaragua", "Guatemala"]},
    {"name": "Huangshan", "neighbors": ["Hubei", "Anhui", "Shanghai", "Zhejiang", "Jiangxi"]},
    {"name": "Hubei", "neighbors": ["Sichuan", "Henan", "Xian", "Changde", "Hunan", "Jiangxi", "Anhui", "Huangshan"]},
    {"name": "Hulunbuir", "neighbors": ["Chita", "Amur", "Dornod", "Chahar", "Heilungkiang"]},
    {"name": "Hunan", "neighbors": ["Hubei", "Changde", "Jiangxi", "Guangdong", "Guangxi", "Guizhou"]},
    {"name": "Hyderabad", "neighbors": ["Orissa", "Madras", "Mysore", "Bombay", "Jabalpur"]},
    {"name": "Iceland", "neighbors": []},
    {"name": "Idaho", "neighbors": ["British Columbia", "Washington", "Oregon", "Nevada", "Utah", "Wyoming", "Montana"]},
    {"name": "Ile de France", "neighbors": ["Centre", "Loire", "Normandy", "Picardy", "Bourgogne", "Champagne"]},
    {"name": "Illinois", "neighbors": ["Indiana", "Iowa", "Missouri", "Kentucky", "Wisconsin"]},
    {"name": "Illubabor Kaffa", "neighbors": ["Upper Nile", "Sidamo", "Welega", "Shewa"]},
    {"name": "Indiana", "neighbors": ["Illinois", "Michigan", "Ohio", "Kentucky"]},
    {"name": "Indore", "neighbors": ["Bombay", "Jabalpur", "Lucknow", "Gujarat", "Rajahsthan"]},
    {"name": "Iowa", "neighbors": ["Nebraska", "South Dakota", "Minnesota", "Wisconsin", "Illinois", "Missouri"]},
    {"name": "Irkutsk", "neighbors": ["Buryatia", "Bratsk", "Kirensk"]},
    {"name": "Isan", "neighbors": ["Siam", "Laos", "Cambodia"]},
    {"name": "Isfahan", "neighbors": ["Fars", "Kerman", "Hamadan", "Semnan", "Khuzestan"]},
    {"name": "Istanbul", "neighbors": ["Edirne", "Izmit"]},
    {"name": "Istria", "neighbors": ["Litorale", "Dalmatia"]},
    {"name": "Ivanovo", "neighbors": ["Yaroslavl", "Vologda", "Gorky", "Moscow", "Ryazan"]},
    {"name": "Ivory Coast", "neighbors": ["Ghana", "Guinea", "Liberia", "Bamako", "Upper Volta"]},
    {"name": "Iwo Jima", "neighbors": []},
    {"name": "Izmir", "neighbors": ["Bursa", "Afyon", "Antalya"]},
    {"name": "Izmit", "neighbors": ["Istanbul", "Bursa", "Ankara", "Kastamonu"]},
    {"name": "Jabalpur", "neighbors": ["Bombay", "Hyderabad", "Orissa", "Bihar", "Lucknow", "Indore"]},
    {"name": "Jalisco", "neighbors": ["Durango", "Guerrero", "Mexico City", "Tamaulipas"]},
    {"name": "Jamaica", "neighbors": []},
    {"name": "Jamtland", "neighbors": ["Helgeland", "Trondelag", "Vasterbotten", "Dalarna", "Gavleborg"]},
    {"name": "Java", "neighbors": ["Lesser Sunda Islands"]},
    {"name": "Jawf", "neighbors": ["Jordan", "Tabuk", "Al Qassim", "Al Hajara"]},
    {"name": "Jehol", "neighbors": ["East Hebei", "Beijing", "South Chahar", "Chahar", "Liaoning", "Liaotung"]},
    {"name": "Jiangsu", "neighbors": ["Anhui", "Henan", "Shanghai", "Shandong"]},
    {"name": "Jiangxi", "neighbors": ["Huangshan", "Hubei", "Hunan", "Guangdong", "Fujian", "Zhejiang"]},
    {"name": "Jiuquan", "neighbors": ["Gobi", "Haixi", "Ningxia", "Kunlun Shan", "Suiyuan", "Dabancheng"]},
    {"name": "Jordan", "neighbors": ["Jawf", "Al Hajara", "Palestine", "Damascus", "Tabuk", "Deir az Zur"]},
    {"name": "Jubaland", "neighbors": ["Bale", "Sidamo", "Garissa", "Somaliland"]},
    {"name": "Jura Mountains", "neighbors": ["Rhone", "Savoy", "Alsace Lorraine", "Franche Comte", "Swiss Plateau", "Wurttemberg"]},
    {"name": "Jylland", "neighbors": ["Sonderjylland"]},
    {"name": "Kabardino Balkaria", "neighbors": ["Georgia", "Sochi", "North Ossetia", "Abkhazia", "Stavropol"]},
    {"name": "Kabul", "neighbors": ["Herat", "Peshawar", "Ashkhabad", "Bukhara", "Stalinabad", "Yarkand", "Northern Kashmir"]},
    {"name": "Kalimantan", "neighbors": ["North Borneo"]},
    {"name": "Kalinin", "neighbors": ["Yaroslavl", "Moscow", "Rzhev", "Tikhvin"]},
    {"name": "Kalmykia", "neighbors": ["Astrakhan", "Dagestan", "Stavropol", "Stalingrad", "Volgodonsk"]},
    {"name": "Kaluga", "neighbors": ["Bryansk", "Tula", "Orel", "Moscow", "Roslavl", "Smolensk"]},
    {"name": "Kamchatka", "neighbors": ["Chukotka", "Magadan"]},
    {"name": "Kansai", "neighbors": ["Chugoku", "Tokai", "Koshinetsu"]},
    {"name": "Kansas", "neighbors": ["Oklahoma", "Missouri", "Colorado", "Nebraska"]},
    {"name": "Kanto", "neighbors": ["Tohoku", "Hokuriku", "Koshinetsu", "Tokai"]},
    {"name": "Karagandy", "neighbors": ["Ayaguz", "Akmolinsk", "Alma Ata", "Kyzyl Orda", "Kostanay", "Akhtubinsk"]},
    {"name": "Karakalpakstan", "neighbors": ["Ashkhabad", "Akhtubinsk", "Khiva", "Tashauz", "Ust Urt", "Navoi"]},
    {"name": "Karas", "neighbors": ["Khomas", "Cape", "Bechuanaland"]},
    {"name": "Kargopol", "neighbors": ["Onega", "Vologda", "Kotlas", "Arkhangelsk"]},
    {"name": "Karjala", "neighbors": ["Kuopio", "Kymi", "Onega", "Olonets", "Leningrad"]},
    {"name": "Kashmir", "neighbors": ["Yarkand", "Taklamakan", "Ngari", "Delhi", "Punjab", "Northern Kashmir"]},
    {"name": "Kassala", "neighbors": ["Eastern Desert", "Blue Nile", "Eritrea", "Begemder", "Khartoum"]},
    {"name": "Kastamonu", "neighbors": ["Izmit", "Ankara", "Samsun", "Amasya"]},
    {"name": "Katowice", "neighbors": ["Kielce", "Lodz", "Krakow", "Zaolzie", "Oberschlesien"]},
    {"name": "Kaunas", "neighbors": ["Wilno", "Suduva", "Zemaitija", "Aukstaitija"]},
    {"name": "Kayes Koulikoro", "neighbors": ["Senegal", "Guinea", "Bamako", "Gao", "Mauritanian Desert", "Mauritania"]},
    {"name": "Kayseri", "neighbors": ["Amasya", "Sivas", "Malatya", "Mersin", "Konya"]},
    {"name": "Kazan", "neighbors": ["Mari El", "Kirov", "Ufa", "Orenburg", "Udmurtia", "Chuvashia", "Ulyanovsky", "Kuybyshev"]},
    {"name": "Kentucky", "neighbors": ["Virginia", "West Virginia", "Tennessee", "Ohio", "Illinois", "Missouri", "Indiana"]},
    {"name": "Kerman", "neighbors": ["Sistan", "Semnan", "Herat", "Fars", "Isfahan", "Khorasan"]},
    {"name": "Khabarovsk", "neighbors": ["Vladivostok", "Sungkiang", "Birobidzhan", "Nikolayevsk"]},
    {"name": "Khakassia", "neighbors": ["Tannu Tuva", "Altai Krai", "Tomsk", "Novosibirsk", "Krasnoyarsk", "Oyrot Region"]},
    {"name": "Kharkov", "neighbors": ["Sumy", "Belgorod", "Stalino", "Dnipropetrovsk", "Poltava", "Voroshilovgrad"]},
    {"name": "Khartoum", "neighbors": ["Kassala", "Aswan", "Blue Nile", "Eastern Desert", "Western Desert", "North Darfur", "Kurdufan"]},
    {"name": "Khatangsky", "neighbors": ["Dudinka", "Kirensk", "Yeniseisk", "Udachny"]},
    {"name": "Kherson", "neighbors": ["Crimea", "Odessa", "Mykolaiv", "Dnipropetrovsk", "Zaporozhe"]},
    {"name": "Khiva", "neighbors": ["Tashauz", "Karakalpakstan"]},
    {"name": "Khmelnytskyi", "neighbors": ["Lwow", "Wolyn", "Vinnytsia", "Zhytomyr", "Bessarabia"]},
    {"name": "Khomas", "neighbors": ["Kunene", "Karas", "Otjozondjupa", "Bechuanaland"]},
    {"name": "Khorasan", "neighbors": ["Tehran", "Semnan", "Kerman", "Herat", "Ashkhabad"]},
    {"name": "Khovd", "neighbors": ["Tannu Tuva", "Gobi", "Ulaanbaatar", "Oyrot Region", "Khovsgol", "Dabancheng", "Dzungaria"]},
    {"name": "Khovsgol", "neighbors": ["Khovd", "Ulaanbaatar", "Tannu Tuva", "Buryatia"]},
    {"name": "Khuzestan", "neighbors": ["Fars", "Isfahan", "Baghdad", "Hamadan", "Kurdistan"]},
    {"name": "Kielce", "neighbors": ["Lodz", "Katowice", "Krakow", "Warszawa", "Lublin"]},
    {"name": "Kirensk", "neighbors": ["Bratsk", "Irkutsk", "Buryatia", "Bodaybo", "Yakutsk", "Udachny", "Yeniseisk", "Khatangsky"]},
    {"name": "Kirin", "neighbors": ["North Korea", "Sungkiang", "Heilungkiang", "Liaotung", "Liaoning"]},
    {"name": "Kirov", "neighbors": ["Vologda", "Kotlas", "Perm", "Kazan", "Mari El", "Gorky", "Udmurtia", "Syktyvkar"]},
    {"name": "Kolyma", "neighbors": ["Verkhoyansk", "Okhotsk", "Magadan", "Chukotka"]},
    {"name": "Konigsberg", "neighbors": ["Ermland Masuren", "Bialystok", "Suduva", "Memel", "Zemaitija"]},
    {"name": "Konya", "neighbors": ["Amasya", "Antalya", "Ankara", "Afyon", "Kayseri", "Mersin"]},
    {"name": "Koshinetsu", "neighbors": ["Hokuriku", "Kanto", "Tokai", "Kansai"]},
    {"name": "Kosovo", "neighbors": ["Southern Serbia", "Macedonia", "Morava", "Montenegro", "Shkoder"]},
    {"name": "Kostanay", "neighbors": ["Magnitogorsk", "Akmolinsk", "Karagandy", "Akhtubinsk", "Chelyabinsk"]},
    {"name": "Kotlas", "neighbors": ["Vologda", "Kirov", "Kargopol", "Pechora", "Arkhangelsk", "Syktyvkar"]},
    {"name": "Krakow", "neighbors": ["Katowice", "Kielce", "Zaolzie", "Lublin", "Lwow", "Eastern Slovakia", "Carpathian Ruthenia", "Stanislawow"]},
    {"name": "Krasnodar", "neighbors": ["Rostov", "Volgodonsk", "Stavropol", "Sochi"]},
    {"name": "Krasnoyarsk", "neighbors": ["Tomsk", "Bratsk", "Tannu Tuva", "Yeniseisk", "Khakassia"]},
    {"name": "Kunene", "neighbors": ["South West Angola", "Khomas", "Otjozondjupa"]},
    {"name": "Kunlun Shan", "neighbors": ["Urumqi", "Haixi", "Qinghai", "Nagqu", "Jiuquan", "Dabancheng", "Taklamakan"]},
    {"name": "Kuopio", "neighbors": ["Onega", "Oulu", "Vaasa", "Mikkeli", "Kymi", "Karjala"]},
    {"name": "Kurdistan", "neighbors": ["Mosul", "Tibriz", "Gilan", "Hamadan", "Baghdad", "Khuzestan"]},
    {"name": "Kurdufan", "neighbors": ["North Darfur", "South Darfur", "Blue Nile", "Upper Nile", "Khartoum", "Bahr al Ghazal"]},
    {"name": "Kursk", "neighbors": ["Bryansk", "Sumy", "Belgorod", "Orel", "Voronezh", "Lipetsk"]},
    {"name": "Kurzeme", "neighbors": ["Zemgale", "Zemaitija"]},
    {"name": "Kuwait", "neighbors": ["Dammam", "Al Hajara", "Al Qassim", "Baghdad"]},
    {"name": "Kuybyshev", "neighbors": ["Saratov", "Balakovo", "Orenburg", "Kazan", "Ulyanovsky"]},
    {"name": "Kyiv", "neighbors": ["Mozyr", "Chernigov", "Cherkasy", "Vinnytsia", "Zhytomyr"]},
    {"name": "Kymi", "neighbors": ["Mikkeli", "Uusimaa", "Karjala", "Kuopio"]},
    {"name": "Kyushu", "neighbors": []},
    {"name": "Kyzyl Orda", "neighbors": ["Akhtubinsk", "Karagandy", "Alma Ata", "Pamir", "Tashkent", "Navoi"]},
    {"name": "La Libertad", "neighbors": ["Cundinamarca", "Zulia", "Panama"]},
    {"name": "La Paz", "neighbors": ["Tacna Moquegua", "Arequipa", "Santa Cruz", "Formosa", "Antofagasta", "Ucayali", "Los Andes", "Arica y Tarapaca"]},
    {"name": "Labrador", "neighbors": ["Cote Nord", "Nord du Quebec"]},
    {"name": "Lagos", "neighbors": ["Benue", "Sokoto", "Dahomey"]},
    {"name": "Lanark", "neighbors": ["Scottish Highlands", "Aberdeenshire", "Lothian", "Cumbria"]},
    {"name": "Lancashire", "neighbors": ["Cumbria", "Yorkshire", "West Midlands", "Wales"]},
    {"name": "Languedoc", "neighbors": ["Midi Pyrenees", "Limousin", "Bouches du Rhone", "Auvergne", "Rhone"]},
    {"name": "Lanna", "neighbors": ["Laos", "Mandalay", "Burma", "Siam"]},
    {"name": "Laos", "neighbors": ["Yunnan", "Dali", "Mandalay", "Lanna", "Siam", "Isan", "Cambodia", "Southern Indochina", "Tonkin"]},
    {"name": "Lappi", "neighbors": ["Oulu", "Salla", "Murmansk", "Petsamo", "Finnmark", "Troms", "Norrbotten"]},
    {"name": "Latgale", "neighbors": ["Pskov", "Tartu", "Vidzeme", "Riga", "Zemgale", "Wilejka", "Vitebsk", "Nevel"]},
    {"name": "Lazio", "neighbors": ["Toscana", "Abruzzo", "Campania"]},
    {"name": "Lebanon", "neighbors": ["Aleppo", "Damascus", "Palestine"]},
    {"name": "Leinster", "neighbors": ["Northern Ireland", "Connaught", "Munster"]},
    {"name": "Leningrad", "neighbors": ["Karjala", "Luga", "Volkhov"]},
    {"name": "Leon", "neighbors": ["Asturias", "Valladolid", "Salamanca", "Porto", "Galicia"]},
    {"name": "Leopoldville", "neighbors": ["Middle Congo", "Coquilhatville", "Lusambo", "Luanda", "North Angola"]},
    {"name": "Lesser Sunda Islands", "neighbors": ["Java", "Portuguese Timor"]},
    {"name": "Liangshan", "neighbors": ["Gannan", "Sichuan", "Zunyi", "Guizhou", "Yunnan", "Dali", "Ganzi"]},
    {"name": "Liaoning", "neighbors": ["Heilungkiang", "Kirin", "Liaotung", "Jehol", "Chahar"]},
    {"name": "Liaotung", "neighbors": ["Dalian", "North Korea", "Kirin", "Liaoning", "Jehol"]},
    {"name": "Liberia", "neighbors": ["Sierra Leone", "Guinea", "Ivory Coast"]},
    {"name": "Libyan Desert", "neighbors": ["Gabes", "Tripolitania", "Sirte", "Cyrenaica", "Matrouh", "Western Desert", "North Darfur", "Borkou Ennedi Tibesti", "Southern Sahara", "Algerian Desert"]},
    {"name": "Lima", "neighbors": ["Arequipa", "Ucayali", "Pastaza", "Loreto", "Ecuador"]},
    {"name": "Limousin", "neighbors": ["Midi Pyrenees", "Languedoc", "Auvergne", "Centre Sud", "Poitou", "Aquitaine"]},
    {"name": "Lipetsk", "neighbors": ["Ryazan", "Tambov", "Voronezh", "Kursk", "Orel", "Tula"]},
    {"name": "Lisbon", "neighbors": ["Porto", "Guarda", "Santarem", "Beja"]},
    {"name": "Litorale", "neighbors": ["Istria", "Dalmatia", "Ljubljana", "North Slovenia", "Upper Austria", "Tyrol", "Veneto"]},
    {"name": "Ljubljana", "neighbors": ["Dalmatia", "North Slovenia", "Croatia", "Litorale", "Istria"]},
    {"name": "Lodz", "neighbors": ["Gdynia", "Poznan", "Oberschlesien", "Katowice", "Kielce", "Warszawa", "Plock"]},
    {"name": "Loire", "neighbors": ["Brittany", "Normandy", "Ile de France", "Centre", "Poitou"]},
    {"name": "Lombardia", "neighbors": ["Veneto", "Trentino", "Alto Adige", "Eastern Swiss Alps", "Ticino", "Piemonte", "Emilia Romagna"]},
    {"name": "Loreto", "neighbors": ["Ucayali", "Pastaza", "Lima", "Ecuador", "Meta", "Amazonas", "Amazon impassable 4"]},
    {"name": "Los Andes", "neighbors": ["Chaco Austral", "Formosa", "Tucuman", "Antofagasta", "La Paz"]},
    {"name": "Lothian", "neighbors": ["Aberdeenshire", "Lanark", "Cumbria", "Northumberland"]},
    {"name": "Louisiana", "neighbors": ["Mississippi", "Arkansas", "Texas"]},
    {"name": "Lourenco Marques", "neighbors": ["Natal", "Transvaal", "Rhodesia", "Manica e Sofala"]},
    {"name": "Lower Austria", "neighbors": ["Sudetenland", "Upper Austria", "North Slovenia", "Transdanubia", "Southern Slovakia"]},
    {"name": "Luanda", "neighbors": ["Leopoldville", "Lusambo", "Elisabethville", "Zambesi", "South West Angola"]},
    {"name": "Lublin", "neighbors": ["Bialystok", "Warszawa", "Kielce", "Krakow", "Lwow", "Wolyn", "Polesie"]},
    {"name": "Lucknow", "neighbors": ["Jabalpur", "Bihar", "Nepal", "Delhi", "Rajahsthan", "Indore", "Jabalpur"]},
    {"name": "Luga", "neighbors": ["Leningrad", "Volkhov", "Novgorod", "Pskov", "Virumaa"]},
    {"name": "Lusambo", "neighbors": ["Costermansville", "Coquilhatville", "Leopoldville", "Luanda", "Elisabethville"]},
    {"name": "Luxembourg", "neighbors": ["Wallonie", "Moselland", "Alsace Lorraine", "Champagne"]},
    {"name": "Luzon", "neighbors": ["Manila"]},
    {"name": "Lwow", "neighbors": ["Khmelnytskyi", "Wolyn", "Lublin", "Krakow", "Stanislawow", "Bucovina", "Bessarabia"]},
    {"name": "Macedonia", "neighbors": ["Sofia", "Plovdiv", "Central Macedonia", "Epirus", "Northern Epirus", "Albania", "Shkoder", "Kosovo", "Southern Serbia"]},
    {"name": "Madagascar", "neighbors": []},
    {"name": "Madinah", "neighbors": ["Tabuk", "Al Qassim", "Nejd", "Asir Makkah"]},
    {"name": "Madras", "neighbors": ["Orissa", "Hyderabad", "Mysore", "Madurai"]},
    {"name": "Madrid", "neighbors": ["Valladolid", "Guadalajara", "Ciudad Real", "Extremadura", "Salamanca"]},
    {"name": "Madurai", "neighbors": ["French India", "Madras", "Mysore"]},
    {"name": "Magadan", "neighbors": ["Okhotsk", "Kolyma", "Chukotka", "Kamchatka"]},
    {"name": "Magallanes", "neighbors": ["Tierra del Fuego", "Aysen", "Santa Cruz AR"]},
    {"name": "Magnitogorsk", "neighbors": ["Chelyabinsk", "Kostanay", "Akhtubinsk", "Orenburg", "Ufa", "Zlatoust"]},
    {"name": "Malatya", "neighbors": ["Mersin", "Kayseri", "Sivas", "Tunceli", "Diyarbakir", "Aleppo", "Hatay"]},
    {"name": "Malawi", "neighbors": ["Zambezia Mocambique", "Manica e Sofala", "Zambia", "Tanganyika"]},
    {"name": "Mandalay", "neighbors": ["Burma", "Assam", "Arunachal Pradesh", "Xikang", "Dali", "Yunnan", "Laos", "Lanna"]},
    {"name": "Manica e Sofala", "neighbors": ["Zambezia Mocambique", "Malawi", "Zambia", "Rhodesia", "Lourenco Marques"]},
    {"name": "Manila", "neighbors": ["Luzon", "Central Islands"]},
    {"name": "Manitoba", "neighbors": ["Northern Ontario", "Minnesota", "North Dakota", "Saskatchewan", "Northern Manitoba"]},
    {"name": "Maranhao", "neighbors": ["Piaui", "Tocantins", "Para"]},
    {"name": "Mari El", "neighbors": ["Kazan", "Chuvashia", "Gorky", "Kirov"]},
    {"name": "Marrakech", "neighbors": ["Casablanca", "Tlemcen", "Algerian Desert", "Rio de Oro", "Sidi Ifni"]},
    {"name": "Maryland", "neighbors": ["West Virginia", "Virginia", "Pennsylvania"]},
    {"name": "Mato Grosso", "neighbors": ["Goias", "Tocantins", "Sao Paulo", "Santa Cruz", "Minas Gerais", "Punta Pora", "Guapore", "Para", "Amazonas", "Amazon impassable 5", "Amazon impassable 6"]},
    {"name": "Matrouh", "neighbors": ["Libyan Desert", "Alexandria", "Derna", "Western Desert", "Cyrenaica"]},
    {"name": "Maurice", "neighbors": ["Ouest du Quebec", "Saint Lawrence", "Cote Nord", "Saguenay"]},
    {"name": "Mauritania", "neighbors": ["Mauritanian Desert", "Senegal", "Rio de Oro", "Kayes Koulikoro"]},
    {"name": "Mauritanian Desert", "neighbors": ["Rio de Oro", "Gao", "Mauritania", "Kayes Koulikoro", "Tombouctou", "Algerian Desert"]},
    {"name": "Mecklenburg", "neighbors": ["Brandenburg", "Hannover", "Holstein", "Vorpommern"]},
    {"name": "Memel", "neighbors": ["Konigsberg", "Zemaitija"]},
    {"name": "Mendoza", "neighbors": ["Atacama", "Santiago", "Rio Negro", "San Luis y La Pampa"]},
    {"name": "Mersin", "neighbors": ["Antalya", "Konya", "Malatya", "Kayseri"]},
    {"name": "Mesopotamia", "neighbors": ["Chaco Austral", "San Luis y La Pampa", "Pampas", "Region Mesopotamica"]},
    {"name": "Meta", "neighbors": ["Loreto", "Ecuador", "Cundinamarca", "Miranda", "Amazonas", "Amazon impassable 1", "Bolivar"]},
    {"name": "Mexico City", "neighbors": ["Guerrero", "Veracruz", "Jalisco", "Tamaulipas"]},
    {"name": "Michigan", "neighbors": ["Indiana", "Ohio", "Wisconsin", "Southern Ontario"]},
    {"name": "Middle Congo", "neighbors": ["Gabon", "Cameroon", "Equatorial Africa", "Leopoldville", "Coquilhatville"]},
    {"name": "Midi Pyrenees", "neighbors": ["Cataluna", "Navarra", "Eastern Aragon", "Western Aragon", "Pyrenees Atlantiques", "Aquitaine", "Languedoc", "Limousin"]},
    {"name": "Mikhaylovka", "neighbors": ["Stalingrad", "Saratov", "Millerovo", "Voronezh", "Engels Marxstadt"]},
    {"name": "Mikkeli", "neighbors": ["Kymi", "Hame", "Uusimaa", "Kuopio", "Vaasa"]},
    {"name": "Millerovo", "neighbors": ["Mikhaylovka", "Stalingrad", "Volgodonsk", "Rostov", "Voroshilovgrad", "Voronezh"]},
    {"name": "Minas Gerais", "neighbors": ["Tocantins", "Goias", "Mato Grosso", "Rio de Janeiro", "Sao Paulo", "Bahia", "Espirito Santo"]},
    {"name": "Mindanao", "neighbors": []},
    {"name": "Minnesota", "neighbors": ["North Dakota", "South Dakota", "Iowa", "Wisconsin", "Manitoba", "Northern Ontario"]},
    {"name": "Minsk", "neighbors": ["Vitebsk", "Gomel", "Bobruysk", "Wilejka", "Nowogrodek"]},
    {"name": "Miranda", "neighbors": ["Bolivar", "Meta", "Cundinamarca", "Zulia"]},
    {"name": "Mississippi", "neighbors": ["Alabama", "Louisiana", "Arkansas", "Tennessee"]},
    {"name": "Missouri", "neighbors": ["Iowa", "Nebraska", "Kansas", "Oklahoma", "Arkansas", "Tennessee", "Kentucky", "Illinois"]},
    {"name": "Moesia", "neighbors": ["Burgas", "Sofia", "Plovdiv", "Oltenia", "Muntenia", "Dobrudja"]},
    {"name": "Moldova", "neighbors": ["Muntenia", "Transylvania", "North Transylvania", "Bessarabia", "Southern Bessarabia", "Bucovina"]},
    {"name": "Mombasa", "neighbors": ["Garissa", "Nairobi", "Nyanza Rift Valley", "Tanganyika"]},
    {"name": "Montana", "neighbors": ["Idaho", "Wyoming", "North Dakota", "South Dakota", "Saskatchewan", "Alberta", "British Columbia"]},
    {"name": "Montenegro", "neighbors": ["Morava", "Kosovo", "Bosnia", "Dalmatia", "Shkoder", "Herzegovina"]},
    {"name": "Morava", "neighbors": ["Bosnia", "Montenegro", "Kosovo", "Serbia", "Southern Serbia", "Sofia", "Banat", "Oltenia"]},
    {"name": "Moravia", "neighbors": ["Zaolzie", "Bohemia", "Sudetenland", "Eastern Sudetenland", "Western Slovakia"]},
    {"name": "Moscow", "neighbors": ["Ivanovo", "Ryazan", "Tula", "Kaluga", "Smolensk", "Rzhev", "Yaroslavl", "Kalinin"]},
    {"name": "Moselland", "neighbors": ["Luxembourg", "Hessen", "Rhineland", "Alsace Lorraine", "Wurttemberg", "Wallonie"]},
    {"name": "Mosul", "neighbors": ["Tibriz", "Al Hajara", "Kurdistan", "Baghdad", "Deir az Zur", "Hakkari"]},
    {"name": "Mozyr", "neighbors": ["Wolyn", "Gomel", "Polesie", "Chernigov", "Bobruysk", "Kyiv", "Zhytomyr"]},
    {"name": "Munster", "neighbors": ["Leinster", "Connaught"]},
    {"name": "Muntenia", "neighbors": ["Moesia", "Transylvania", "Oltenia", "Dobrudja", "Moldova", "Southern Bessarabia"]},
    {"name": "Murcia", "neighbors": ["Granada", "Ciudad Real", "Valencia", "Guadalajara", "Cordoba"]},
    {"name": "Murmansk", "neighbors": ["Salla", "Lappi", "Onega", "Petsamo"]},
    {"name": "Mykolaiv", "neighbors": ["Odessa", "Dnipropetrovsk", "Kherson", "Cherkasy"]},
    {"name": "Mysore", "neighbors": ["Goa", "Bombay", "Hyderabad", "Madurai", "Madras"]},
    {"name": "Nagqu", "neighbors": ["Taklamakan", "Ngari", "Shigatse", "Xikang", "Qinghai", "Kunlun Shan"]},
    {"name": "Nairobi", "neighbors": ["Mombasa", "Garissa", "Sidamo", "Nyanza Rift Valley"]},
    {"name": "Najiran", "neighbors": ["Rub al Khali", "Nejd", "Asir Makkah", "Yemen", "Aden"]},
    {"name": "Nanning", "neighbors": ["Guangxi", "Tonkin", "Guangzhou", "Guangzhouwan", "Hainan"]},
    {"name": "Natal", "neighbors": ["Cape", "Transvaal", "Lourenco Marques"]},
    {"name": "Navarra", "neighbors": ["Pyrenees Atlantiques", "Western Aragon", "Burgos", "Pais Vasco"]},
    {"name": "Navoi", "neighbors": ["Kyzyl Orda", "Akhtubinsk", "Karakalpakstan", "Tashauz", "Bukhara", "Tashkent"]},
    {"name": "Nebraska", "neighbors": ["Missouri", "Iowa", "South Dakota", "Wyoming", "Colorado", "Kansas"]},
    {"name": "Nejd", "neighbors": ["Dammam", "Al Qassim", "Madinah", "Asir Makkah", "Najiran", "Rub al Khali"]},
    {"name": "Nenets", "neighbors": ["Salekhard", "Northern Urals", "Pechora", "Arkhangelsk"]},
    {"name": "Nepal", "neighbors": ["West Bengal", "Bihar", "Lucknow", "Delhi", "Ngari", "Shigatse"]},
    {"name": "Nevada", "neighbors": ["Arizona", "Utah", "Idaho", "Oregon", "California"]},
    {"name": "Nevel", "neighbors": ["Novgorod", "Pskov", "Latgale", "Vitebsk", "Smolensk", "Rzhev"]},
    {"name": "New Brunswick", "neighbors": ["Nova Scotia", "Saint Lawrence", "New England"]},
    {"name": "New Caledonia", "neighbors": []},
    {"name": "New England", "neighbors": ["New Brunswick", "Saint Lawrence", "New York"]},
    {"name": "New Jersey", "neighbors": ["New York", "Pennsylvania"]},
    {"name": "New Mexico", "neighbors": ["Arizona", "Colorado", "Oklahoma", "Texas", "Chihuahua", "Sonora"]},
    {"name": "New South Wales", "neighbors": ["Queensland", "Southwest Queensland", "Central Australia", "South Australia", "Victoria"]},
    {"name": "New York", "neighbors": ["New England", "Saint Lawrence", "Southern Ontario", "Pennsylvania", "New Jersey"]},
    {"name": "Newfoundland", "neighbors": []},
    {"name": "Ngari", "neighbors": ["Taklamakan", "Kashmir", "Delhi", "Nepal", "Shigatse", "Nagqu"]},
    {"name": "Nicaragua", "neighbors": ["Honduras", "Costa Rica"]},
    {"name": "Niederbayern", "neighbors": ["Oberbayern", "Franken", "Sudetenland", "Upper Austria"]},
    {"name": "Niederschlesien", "neighbors": ["Eastern Sudetenland", "Bohemia", "Sudetenland", "Sachsen", "Ostmark", "Poznan", "Oberschlesien"]},
    {"name": "Niger", "neighbors": ["Lagos", "Sokoto", "Southern Sahara", "Gao", "Upper Volta", "Dahomey"]},
    {"name": "Nikolayevsk", "neighbors": ["Khabarovsk", "Birobidzhan", "Amur", "Okhotsk"]},
    {"name": "Ningxia", "neighbors": ["Shaanxi", "Ordos", "Suiyuan", "Jiuquan", "Haixi", "Golog", "Gansu"]},
    {"name": "Nord du Quebec", "neighbors": ["Labrador", "Cote Nord", "Saguenay", "Ouest du Quebec"]},
    {"name": "Nord Pas de Calais", "neighbors": ["Picardy", "Wallonie", "Vlaanderen"]},
    {"name": "Nordland", "neighbors": ["Troms", "Norrbotten", "Vasterbotten", "Helgeland"]},
    {"name": "Normandy", "neighbors": ["Picardy", "Ile de France", "Loire", "Brittany"]},
    {"name": "Norrbotten", "neighbors": ["Lappi", "Troms", "Nordland", "Vasterbotten"]},
    {"name": "North Angola", "neighbors": ["Leopoldville", "Middle Congo"]},
    {"name": "North Borneo", "neighbors": ["Kalimantan"]},
    {"name": "North Carolina", "neighbors": ["South Carolina", "Georgia US", "Tennessee", "Virginia"]},
    {"name": "North Dakota", "neighbors": ["Montana", "South Dakota", "Minnesota", "Manitoba", "Saskatchewan"]},
    {"name": "North Darfur", "neighbors": ["Kurdufan", "Western Desert", "Libyan Desert", "South Darfur", "Khartoum", "Borkou Ennedi Tibesti"]},
    {"name": "North Island", "neighbors": []},
    {"name": "North Korea", "neighbors": ["South Korea"]},
    {"name": "North Ossetia", "neighbors": ["Georgia", "Stavropol", "Kabardino Balkaria", "Chechnya Ingushetia"]},
    {"name": "North Queensland", "neighbors": ["Northern Territory", "Central Australia", "Queensland"]},
    {"name": "North Sakhalin", "neighbors": ["South Sakhalin"]},
    {"name": "North Slovenia", "neighbors": ["Tyrol", "Litorale", "Croatia", "Upper Austria", "Lower Austria", "Transdanubia", "Ljubljana"]},
    {"name": "North Transylvania", "neighbors": ["Moldova", "Crisana", "Alfold", "Bucovina", "Transylvania", "Stanislawow", "Carpathian Ruthenia"]},
    {"name": "North West Australia", "neighbors": ["Western Australia", "Central Australia", "Northern Territory"]},
    {"name": "Northern Epirus", "neighbors": ["Albania", "Macedonia", "Epirus"]},
    {"name": "Northern Hungary", "neighbors": ["Transdanubia", "Alfold", "Southern Slovakia"]},
    {"name": "Northern Ireland", "neighbors": ["Leinster", "Connaught"]},
    {"name": "Northern Kashmir", "neighbors": ["Punjab", "Kabul", "Kashmir", "Peshawar", "Yarkand", "Stalinabad"]},
    {"name": "Northern Malay", "neighbors": ["Singapore", "Burma", "Siam"]},
    {"name": "Northern Manitoba", "neighbors": ["Nunavut", "Districts of Ontario", "Manitoba", "Northern Saskatchewan"]},
    {"name": "Northern Ontario", "neighbors": ["Michigan", "Minnesota", "Manitoba", "Districts of Ontario", "Southern Ontario", "Ouest du Quebec"]},
    {"name": "Northern Saskatchewan", "neighbors": ["Alberta", "Saskatchewan", "Northern Manitoba", "Northwest Territories"]},
    {"name": "Northern Territory", "neighbors": ["North West Australia", "Central Australia", "North Queensland"]},
    {"name": "Northern Urals", "neighbors": ["Perm", "Pechora", "Nenets", "Salekhard", "Tobolsk", "Syktyvkar"]},
    {"name": "Northumberland", "neighbors": ["Yorkshire", "Cumbria", "Lothian"]},
    {"name": "Northwest Territories", "neighbors": ["Yukon Territory", "Nunavut", "Upper British Columbia", "Alberta", "Northern Saskatchewan"]},
    {"name": "Nova Scotia", "neighbors": ["New Brunswick"]},
    {"name": "Novgorod", "neighbors": ["Pskov", "Rzhev", "Nevel", "Luga", "Volkhov", "Tikhvin"]},
    {"name": "Novosibirsk", "neighbors": ["Omsk", "Tomsk", "Pavlodar", "Khakassia", "Altai Krai"]},
    {"name": "Nowogrodek", "neighbors": ["Wilno", "Suduva", "Minsk", "Bobruysk", "Polesie", "Bialystok", "Wilejka"]},
    {"name": "Nunavut", "neighbors": ["Northwest Territories", "Northern Manitoba"]},
    {"name": "Nyanza Rift Valley", "neighbors": ["Uganda", "Upper Nile", "Sidamo", "Nairobi", "Mombasa", "Tanganyika"]},
    {"name": "Oaxaca", "neighbors": ["Veracruz", "Chiapas", "Guerrero"]},
    {"name": "Oberbayern", "neighbors": ["Vorarlberg", "Tyrol", "Upper Austria", "Niederbayern", "Franken", "Wurttemberg"]},
    {"name": "Oberschlesien", "neighbors": ["Lodz", "Poznan", "Niederschlesien", "Eastern Sudetenland", "Zaolzie", "Katowice"]},
    {"name": "Odessa", "neighbors": ["Mykolaiv", "Cherkasy", "Balta Tiraspol", "Southern Bessarabia"]},
    {"name": "Ohio", "neighbors": ["Pennsylvania", "Kentucky", "Michigan", "Indiana", "West Virginia"]},
    {"name": "Okhotsk", "neighbors": ["Magadan", "Kolyma", "Verkhoyansk", "Yakutsk", "Amur", "Nikolayevsk"]},
    {"name": "Okinawa", "neighbors": []},
    {"name": "Oklahoma", "neighbors": ["Texas", "Kansas", "Arkansas", "Missouri", "Colorado", "New Mexico"]},
    {"name": "Olonets", "neighbors": ["Karjala", "Onega", "Kargopol", "Tikhvin"]},
    {"name": "Oltenia", "neighbors": ["Muntenia", "Transylvania", "Banat", "Morava", "Sofia", "Moesia"]},
    {"name": "Oman", "neighbors": ["Abu Dhabi", "Rub al Khali", "Aden"]},
    {"name": "Omsk", "neighbors": ["Tyumen", "Tomsk", "Novosibirsk", "Pavlodar", "Akmolinsk"]},
    {"name": "Onega", "neighbors": ["Arkhangelsk", "Kargopol", "Olonets", "Karjala", "Kuopio", "Oulu", "Salla", "Murmansk"]},
    {"name": "Opplandene", "neighbors": ["Oslofjord", "Varmland", "Dalarna", "Trondelag", "Vestlandet", "Telemark"]},
    {"name": "Ordos", "neighbors": ["Shaanxi", "Shanxi", "Suiyuan", "Ningxia"]},
    {"name": "Oregon", "neighbors": ["Washington", "California", "Idaho", "Nevada"]},
    {"name": "Orel", "neighbors": ["Kursk", "Lipetsk", "Tula", "Kaluga", "Bryansk"]},
    {"name": "Orenburg", "neighbors": ["Balakovo", "Uralsk", "Akhtubinsk", "Magnitogorsk", "Ufa", "Kazan", "Kuybyshev"]},
    {"name": "Orissa", "neighbors": ["Madras", "Hyderabad", "Jabalpur", "Bihar", "West Bengal"]},
    {"name": "Oslofjord", "neighbors": ["Telemark", "Opplandene", "Varmland", "Bohuslan"]},
    {"name": "Ostergotland", "neighbors": ["Smaland", "Vastergotland", "Sodermalm"]},
    {"name": "Ostmark", "neighbors": ["Niederschlesien", "Poznan", "Hinterpommern", "Vorpommern", "Brandenburg", "Sachsen"]},
    {"name": "Otjozondjupa", "neighbors": ["Bechuanaland", "Zambia", "Zambesi", "South West Angola", "Kunene", "Khomas"]},
    {"name": "Ouest du Quebec", "neighbors": ["Nord du Quebec", "Northern Ontario", "Southern Ontario", "Saint Lawrence", "Maurice"]},
    {"name": "Oulu", "neighbors": ["Lappi", "Salla", "Onega", "Kuopio", "Vaasa"]},
    {"name": "Oyrot Region", "neighbors": ["Khakassia", "Tannu Tuva", "Khovd", "Dzungaria", "Semipalatinsk", "Altai Krai"]},
    {"name": "Pais Vasco", "neighbors": ["Pyrenees Atlantiques", "Navarra", "Burgos", "Asturias"]},
    {"name": "Palestine", "neighbors": ["Lebanon", "Damascus", "Jordan", "Sinai"]},
    {"name": "Pamir", "neighbors": ["Stalinabad", "Tashkent", "Kyzyl Orda", "Alma Ata", "Urumqi", "Yarkand"]},
    {"name": "Pampas", "neighbors": ["Region Mesopotamica", "Mesopotamia", "San Luis y La Pampa", "Rio Negro"]},
    {"name": "Panama", "neighbors": ["Costa Rica", "La Libertad", "Panama Canal"]},
    {"name": "Panama Canal", "neighbors": ["Panama"]},
    {"name": "Papua", "neighbors": ["West Papua"]},
    {"name": "Para", "neighbors": ["Maranhao", "Tocantins", "Mato Grosso", "Amazon impassable 6", "Amazon impassable 8", "Amazonas", "Amapa"]},
    {"name": "Paraguay", "neighbors": ["Formosa", "Chaco Boreal", "Punta Pora", "Parana", "Region Mesopotamica", "Chaco Austral"]},
    {"name": "Parana", "neighbors": ["Region Mesopotamica", "Paraguay", "Punta Pora", "Sao Paulo", "Santa Catarina"]},
    {"name": "Parnu", "neighbors": ["Harju", "Virumaa", "Tartu", "Vidzeme"]},
    {"name": "Pastaza", "neighbors": ["Loreto", "Ecuador", "Lima"]},
    {"name": "Pavlodar", "neighbors": ["Omsk", "Altai Krai", "Novosibirsk", "Akmolinsk", "Semipalatinsk"]},
    {"name": "Paysandu", "neighbors": ["Cerro Largo", "Rio Grande do Sul", "Region Mesopotamica", "Uruguay"]},
    {"name": "Pechora", "neighbors": ["Syktyvkar", "Northern Urals", "Nenets", "Arkhangelsk", "Kotlas"]},
    {"name": "Peloponnese", "neighbors": ["Attica"]},
    {"name": "Pennsylvania", "neighbors": ["Maryland", "New Jersey", "New York", "Ohio", "West Virginia"]},
    {"name": "Penza", "neighbors": ["Saratov", "Ulyanovsky", "Gorky", "Ryazan", "Tambov"]},
    {"name": "Perm", "neighbors": ["Zlatoust", "Sverdlovsk", "Tobolsk", "Northern Urals", "Syktyvkar", "Kirov", "Udmurtia", "Ufa"]},
    {"name": "Pernambuco", "neighbors": ["Rio Grande do Norte", "Ceara", "Piaui", "Bahia"]},
    {"name": "Peshawar", "neighbors": ["Northern Kashmir", "Punjab", "Quetta", "Herat", "Kabul"]},
    {"name": "Petsamo", "neighbors": ["Murmansk", "Lappi", "Finnmark"]},
    {"name": "Piaui", "neighbors": ["Ceara", "Pernambuco", "Bahia", "Tocantins", "Maranhao"]},
    {"name": "Picardy", "neighbors": ["Nord Pas de Calais", "Wallonie", "Champagne", "Ile de France", "Normandy"]},
    {"name": "Piemonte", "neighbors": ["Savoy", "Western Swiss Alps", "Ticino", "Lombardia", "Emilia Romagna", "Toscana"]},
    {"name": "Plock", "neighbors": ["Gdynia", "Ermland Masuren", "Bialystok", "Warszawa", "Lodz"]},
    {"name": "Plovdiv", "neighbors": ["Thrace", "Central Macedonia", "Macedonia", "Sofia", "Moesia", "Burgas"]},
    {"name": "Poitou", "neighbors": ["Loire", "Centre", "Centre Sud", "Limousin", "Aquitaine"]},
    {"name": "Polesie", "neighbors": ["Wolyn", "Mozyr", "Bobruysk", "Nowogrodek", "Bialystok", "Lublin"]},
    {"name": "Poltava", "neighbors": ["Kharkov", "Sumy", "Chernigov", "Cherkasy", "Dnipropetrovsk"]},
    {"name": "Porto", "neighbors": ["Galicia", "Leon", "Salamanca", "Guarda", "Lisbon"]},
    {"name": "Portuguese Guinea", "neighbors": ["Guinea", "Senegal"]},
    {"name": "Portuguese Timor", "neighbors": ["Lesser Sunda Islands"]},
    {"name": "Poznan", "neighbors": ["Oberschlesien", "Niederschlesien", "Ostmark", "Hinterpommern", "Gdynia", "Lodz"]},
    {"name": "Pskov", "neighbors": ["Luga", "Novgorod", "Nevel", "Latgale", "Tartu", "Virumaa"]},
    {"name": "Puglia", "neighbors": ["Campania", "Abruzzo"]},
    {"name": "Punjab", "neighbors": ["Sind", "Rajahsthan", "Delhi", "Kashmir", "Northern Kashmir", "Peshawar", "Quetta"]},
    {"name": "Punta Pora", "neighbors": ["Mato Grosso", "Santa Cruz", "Chaco Boreal", "Paraguay", "Parana", "Sao Paulo"]},
    {"name": "Pyrenees Atlantiques", "neighbors": ["Aquitaine", "Midi Pyrenees", "Western Aragon", "Navarra", "Pais Vasco"]},
    {"name": "Qatar", "neighbors": ["Rub al Khali", "Dammam"]},
    {"name": "Qingdao", "neighbors": ["Shandong"]},
    {"name": "Qinghai", "neighbors": ["Xikang", "Ganzi", "Golog", "Haixi", "Kunlun Shan", "Nagqu"]},
    {"name": "Queensland", "neighbors": ["New South Wales", "Southwest Queensland", "Central Australia", "North Queensland"]},
    {"name": "Quetta", "neighbors": ["Peshawar", "Punjab", "Sind", "Baluchistan", "Herat"]},
    {"name": "Rajahsthan", "neighbors": ["Lucknow", "Indore", "Gujarat", "Sind", "Punjab", "Delhi"]},
    {"name": "Region Mesopotamica", "neighbors": ["Paysandu", "Rio Grande do Sul", "Santa Catarina", "Parana", "Paraguay", "Chaco Austral", "Mesopotamia", "Pampas"]},
    {"name": "Rhineland", "neighbors": ["Friesland", "Westfalen", "Hessen", "Moselland", "Wallonie", "Brabant"]},
    {"name": "Rhodesia", "neighbors": ["Zambia", "Manica e Sofala", "Lourenco Marques", "Transvaal", "Bechuanaland"]},
    {"name": "Rhone", "neighbors": ["Franche Comte", "Jura Mountains", "Savoy", "Alpes", "Bouches du Rhone", "Languedoc", "Auvergne", "Bourgogne"]},
    {"name": "Riga", "neighbors": ["Vidzeme", "Latgale", "Zemgale"]},
    {"name": "Rio Branco", "neighbors": ["British Guyana", "Bolivar", "Amazonas", "Amazon impassable 8", "Amazon impassable 7"]},
    {"name": "Rio de Janeiro", "neighbors": ["Espirito Santo", "Minas Gerais", "Sao Paulo"]},
    {"name": "Rio de Oro", "neighbors": ["Marrakech", "Algerian Desert", "Mauritanian Desert", "Mauritania"]},
    {"name": "Rio Grande do Norte", "neighbors": ["Ceara", "Pernambuco"]},
    {"name": "Rio Grande do Sul", "neighbors": ["Cerro Largo", "Paysandu", "Region Mesopotamica", "Santa Catarina"]},
    {"name": "Rio Negro", "neighbors": ["Chubut", "Araucania", "Santiago", "Mendoza", "San Luis y La Pampa", "Pampas"]},
    {"name": "Roslavl", "neighbors": ["Smolensk", "Kaluga", "Bryansk", "Gomel"]},
    {"name": "Rostov", "neighbors": ["Stalino", "Voroshilovgrad", "Millerovo", "Volgodonsk", "Krasnodar"]},
    {"name": "Rub al Khali", "neighbors": ["Qatar", "Dammam", "Nejd", "Najiran", "Aden", "Oman", "Abu Dhabi"]},
    {"name": "Rwanda", "neighbors": ["Tanganyika", "Burundi", "Costermansville", "Uganda"]},
    {"name": "Ryazan", "neighbors": ["Moscow", "Ivanovo", "Gorky", "Penza", "Tambov", "Lipetsk", "Tula"]},
    {"name": "Rzhev", "neighbors": ["Kalinin", "Tikhvin", "Novgorod", "Nevel", "Smolensk", "Moscow"]},
    {"name": "Sachsen", "neighbors": ["Franken", "Thuringen", "Brandenburg", "Ostmark", "Niederschlesien", "Sudetenland"]},
    {"name": "Saguenay", "neighbors": ["Nord du Quebec", "Cote Nord", "Maurice"]},
    {"name": "Saint Lawrence", "neighbors": ["Maurice", "Ouest du Quebec", "Southern Ontario", "New England", "New Brunswick", "New York"]},
    {"name": "Salamanca", "neighbors": ["Valladolid", "Madrid", "Extremadura", "Guarda", "Porto", "Leon"]},
    {"name": "Salekhard", "neighbors": ["Yamalia", "Surgut", "Tobolsk", "Northern Urals", "Nenets"]},
    {"name": "Salla", "neighbors": ["Murmansk", "Onega", "Oulu", "Lappi"]},
    {"name": "Samar", "neighbors": []},
    {"name": "Samsun", "neighbors": ["Trabzon", "Sivas", "Amasya", "Kastamonu"]},
    {"name": "San Juan y La Rioja", "neighbors": ["Mendoza", "Santiago", "Atacama", "Tucuman", "Chaco Austral", "San Luis y La Pampa"]},
    {"name": "San Luis y La Pampa", "neighbors": ["Chaco Austral", "Mesopotamia", "Pampas", "Rio Negro", "Mendoza", "San Juan y La Rioja"]},
    {"name": "Santa Catarina", "neighbors": ["Parana", "Region Mesopotamica", "Rio Grande do Sul"]},
    {"name": "Santa Cruz", "neighbors": ["Amazonas", "Amazon impassable 3", "Acre", "Ucayali", "La Paz", "Chaco Boreal", "Punta Pora", "Mato Grosso", "Guapore"]},
    {"name": "Santa Cruz AR", "neighbors": ["Chubut", "Aysen", "Magallanes"]},
    {"name": "Santarem", "neighbors": ["Lisbon", "Guarda", "Extremadura", "Beja"]},
    {"name": "Santiago", "neighbors": ["Atacama", "San Juan y La Rioja", "Mendoza", "Rio Negro", "Araucania"]},
    {"name": "Sao Paulo", "neighbors": ["Rio de Janeiro", "Minas Gerais", "Mato Grosso", "Punta Pora", "Parana"]},
    {"name": "Saratov", "neighbors": ["Balakovo", "Kuybyshev", "Ulyanovsky", "Penza", "Tambov", "Voronezh", "Mikhaylovka", "Engels Marxstadt"]},
    {"name": "Sardegna", "neighbors": []},
    {"name": "Saskatchewan", "neighbors": ["Manitoba", "North Dakota", "Montana", "Alberta", "Northern Saskatchewan"]},
    {"name": "Savoy", "neighbors": ["Piemonte", "Western Swiss Alps", "Swiss Plateau", "Jura Mountains", "Rhone", "Alpes", "Bouches du Rhone", "Var"]},
    {"name": "Schleswig", "neighbors": ["Sonderjylland", "Holstein"]},
    {"name": "Scottish Highlands", "neighbors": ["Aberdeenshire", "Lanark"]},
    {"name": "Semipalatinsk", "neighbors": ["Dzungaria", "Oyrot Region", "Altai Krai", "Pavlodar", "Akmolinsk", "Ayaguz"]},
    {"name": "Semnan", "neighbors": ["Tehran", "Hamadan", "Isfahan", "Kerman", "Khorasan"]},
    {"name": "Senegal", "neighbors": ["Gambia", "Mauritania", "Kayes Koulikoro", "Guinea", "Portuguese Guinea"]},
    {"name": "Serbia", "neighbors": ["Banat", "West Banat", "Croatia", "Bosnia", "Morava"]},
    {"name": "Sevilla", "neighbors": ["Beja", "Extremadura", "Cordoba", "Granada", "Gibraltar"]},
    {"name": "Shaanxi", "neighbors": ["Xian", "Henan", "Shanxi", "Ordos", "Ningxia", "Gansu"]},
    {"name": "Shandong", "neighbors": ["Qingdao", "Jiangsu", "Henan", "Hebei"]},
    {"name": "Shanghai", "neighbors": ["Zhejiang", "Huangshan", "Anhui", "Jiangsu"]},
    {"name": "Shanxi", "neighbors": ["Shaanxi", "Ordos", "Hebei", "Henan", "Beijing", "Suiyuan", "South Chahar"]},
    {"name": "Shewa", "neighbors": ["Wello", "Afar", "Bale", "Sidamo", "Welega", "Gojjam", "Illubabor Kaffa", "Hararghe"]},
    {"name": "Shigatse", "neighbors": ["West Bengal", "Nepal", "Bhutan", "Arunachal Pradesh", "Xikang", "Nagqu", "Ngari"]},
    {"name": "Shikoku", "neighbors": []},
    {"name": "Shkoder", "neighbors": ["Montenegro", "Kosovo", "Macedonia", "Albania"]},
    {"name": "Siam", "neighbors": ["Cambodia", "Laos", "Isan", "Lanna", "Burma", "Northern Malay"]},
    {"name": "Sichuan", "neighbors": ["Gansu", "Xian", "Gannan", "Hubei", "Zunyi", "Liangshan", "Changde"]},
    {"name": "Sicilia", "neighbors": []},
    {"name": "Sidamo", "neighbors": ["Shewa", "Bale", "Garissa", "Nairobi", "Jubaland", "Nyanza Rift Valley", "Upper Nile", "Illubabor Kaffa"]},
    {"name": "Sidi Ifni", "neighbors": ["Marrakech"]},
    {"name": "Sierra Leone", "neighbors": ["Guinea", "Liberia"]},
    {"name": "Sinai", "neighbors": ["Palestine", "Suez"]},
    {"name": "Sind", "neighbors": ["Gujarat", "Quetta", "Punjab", "Rajahsthan", "Baluchistan"]},
    {"name": "Singapore", "neighbors": ["Northern Malay"]},
    {"name": "Sirte", "neighbors": ["Libyan Desert", "Cyrenaica", "Benghasi", "Tripolitania", "El Agheila"]},
    {"name": "Sistan", "neighbors": ["Baluchistan", "Kerman", "Fars"]},
    {"name": "Sivas", "neighbors": ["Samsun", "Trabzon", "Amasya", "Malatya", "Tunceli", "Kayseri"]},
    {"name": "Sjaelland", "neighbors": []},
    {"name": "Skane", "neighbors": ["Vastergotland", "Smaland"]},
    {"name": "Smaland", "neighbors": ["Vastergotland", "Ostergotland", "Skane"]},
    {"name": "Smolensk", "neighbors": ["Rzhev", "Moscow", "Kaluga", "Roslavl", "Gomel", "Vitebsk", "Nevel"]},
    {"name": "Sochi", "neighbors": ["Krasnodar", "Stavropol", "Kabardino Balkaria", "Abkhazia"]},
    {"name": "Sodermalm", "neighbors": ["Gavleborg", "Dalarna", "Varmland", "Vastergotland", "Ostergotland"]},
    {"name": "Sofia", "neighbors": ["Plovdiv", "Moesia", "Oltenia", "Morava", "Southern Serbia", "Macedonia"]},
    {"name": "Sokoto", "neighbors": ["Southern Sahara", "Borno", "Benue", "Lagos", "Niger"]},
    {"name": "Solomon Islands", "neighbors": []},
    {"name": "Somaliland", "neighbors": ["Jubaland", "Bale", "Hararghe", "British Somaliland"]},
    {"name": "Sonderjylland", "neighbors": ["Schleswig", "Jylland"]},
    {"name": "Sonora", "neighbors": ["Baja California", "Arizona", "New Mexico", "Chihuahua", "Durango"]},
    {"name": "South Australia", "neighbors": ["South West Australia", "Central Australia", "New South Wales", "Victoria"]},
    {"name": "South Carolina", "neighbors": ["Georgia US", "North Carolina"]},
    {"name": "South Chahar", "neighbors": ["Shanxi", "Beijing", "Jehol", "Chahar", "Suiyuan"]},
    {"name": "South Dakota", "neighbors": ["North Dakota", "Montana", "Wyoming", "Nebraska", "Iowa", "Minnesota"]},
    {"name": "South Darfur", "neighbors": ["Borkou Ennedi Tibesti", "North Darfur", "Kurdufan", "Bahr al Ghazal", "Equatorial Africa", "Chad"]},
    {"name": "South Georgia", "neighbors": []},
    {"name": "South Island", "neighbors": []},
    {"name": "South Korea", "neighbors": ["North Korea"]},
    {"name": "South Sakhalin", "neighbors": ["North Sakhalin"]},
    {"name": "South West Angola", "neighbors": ["Luanda", "Zambesi", "Otjozondjupa", "Kunene"]},
    {"name": "South West Australia", "neighbors": ["Western Australia", "South Australia", "Central Australia"]},
    {"name": "South West England", "neighbors": ["Gloucestershire", "Sussex"]},
    {"name": "Southern Bessarabia", "neighbors": ["Muntenia", "Moldova", "Bessarabia", "Balta Tiraspol", "Odessa"]},
    {"name": "Southern Indochina", "neighbors": ["Tonkin", "Laos", "Cambodia"]},
    {"name": "Southern Ontario", "neighbors": ["Northern Ontario", "Ouest du Quebec", "Saint Lawrence", "Michigan", "New York"]},
    {"name": "Southern Sahara", "neighbors": ["Libyan Desert", "Algerian Desert", "Tombouctou", "Gao", "Niger", "Sokoto", "Borno", "Chad", "Borkou Ennedi Tibesti"]},
    {"name": "Southern Serbia", "neighbors": ["Morava", "Sofia", "Macedonia", "Kosovo"]},
    {"name": "Southern Slovakia", "neighbors": ["Transdanubia", "Northern Hungary", "Alfold", "Carpathian Ruthenia", "Lower Austria", "Eastern Slovakia", "Western Slovakia"]},
    {"name": "Southwest Queensland", "neighbors": ["Central Australia", "Queensland", "New South Wales"]},
    {"name": "Spanish Africa", "neighbors": ["Casablanca"]},
    {"name": "Stalinabad", "neighbors": ["Pamir", "Yarkand", "Kabul", "Bukhara", "Tashkent"]},
    {"name": "Stalingrad", "neighbors": ["Engels Marxstadt", "Mikhaylovka", "Millerovo", "Volgodonsk", "Kalmykia", "Astrakhan", "Uralsk"]},
    {"name": "Stalino", "neighbors": ["Voroshilovgrad", "Rostov", "Kharkov", "Dnipropetrovsk", "Zaporozhe"]},
    {"name": "Stanislawow", "neighbors": ["Lwow", "Bucovina", "North Transylvania", "Carpathian Ruthenia", "Krakow"]},
    {"name": "Stanleyville", "neighbors": ["Bahr al Ghazal", "Equatorial Africa", "Coquilhatville", "Costermansville", "Uganda"]},
    {"name": "Stavropol", "neighbors": ["Chechnya Ingushetia", "Dagestan", "Kalmykia", "Volgodonsk", "Krasnodar", "Sochi", "Kabardino Balkaria", "North Ossetia"]},
    {"name": "Sudetenland", "neighbors": ["Western Slovakia", "Lower Austria", "Upper Austria", "Niederbayern", "Franken", "Sachsen", "Niederschlesien", "Bohemia", "Moravia"]},
    {"name": "Suduva", "neighbors": ["Bialystok", "Nowogrodek", "Wilno", "Kaunas", "Zemaitija", "Konigsberg"]},
    {"name": "Suez", "neighbors": ["Sinai", "Eastern Desert", "Cairo"]},
    {"name": "Suiyuan", "neighbors": ["Shanxi", "South Chahar", "Chahar", "Gobi", "Jiuquan", "Ningxia", "Ordos"]},
    {"name": "Sulawesi", "neighbors": []},
    {"name": "Sumatra", "neighbors": []},
    {"name": "Sumy", "neighbors": ["Kursk", "Belgorod", "Kharkov", "Poltava", "Chernigov", "Bryansk"]},
    {"name": "Sungkiang", "neighbors": ["Kirin", "Heilungkiang", "Birobidzhan", "Khabarovsk", "Vladivostok", "North Korea"]},
    {"name": "Surgut", "neighbors": ["Tobolsk", "Yamalia", "Salekhard", "Tomsk", "Dudinka", "Yeniseisk", "Tyumen"]},
    {"name": "Suriname", "neighbors": ["French Guiana", "Amazon impassable 8", "British Guyana"]},
    {"name": "Sussex", "neighbors": ["Greater London Area", "Gloucestershire", "South West England"]},
    {"name": "Sverdlovsk", "neighbors": ["Zlatoust", "Perm", "Tobolsk", "Tyumen", "Chelyabinsk"]},
    {"name": "Swiss Plateau", "neighbors": ["Wurttemberg", "Vorarlberg", "Eastern Swiss Alps", "Western Swiss Alps", "Jura Mountains"]},
    {"name": "Syktyvkar", "neighbors": ["Northern Urals", "Perm", "Kirov", "Kotlas", "Pechora"]},
    {"name": "Tabuk", "neighbors": ["Jordan", "Jawf", "Al Qassim", "Madinah"]},
    {"name": "Tacna Moquegua", "neighbors": ["Arequipa", "La Paz", "Arica y Tarapaca"]},
    {"name": "Taiwan", "neighbors": []},
    {"name": "Taklamakan", "neighbors": ["Nagqu", "Kunlun Shan", "Urumqi", "Yarkand", "Kashmir", "Ngari"]},
    {"name": "Tamaulipas", "neighbors": ["Veracruz", "Mexico City", "Jalisco", "Durango", "Coahuila", "Texas"]},
    {"name": "Tambov", "neighbors": ["Saratov", "Penza", "Ryazan", "Lipetsk", "Voronezh"]},
    {"name": "Tanganyika", "neighbors": ["Zambezia Mocambique", "Malawi", "Zambia", "Burundi", "Rwanda", "Uganda", "Nyanza Rift Valley", "Mombasa"]},
    {"name": "Tannu Tuva", "neighbors": ["Buryatia", "Bratsk", "Krasnoyarsk", "Khakassia", "Oyrot Region", "Khovd", "Khovsgol"]},
    {"name": "Tartu", "neighbors": ["Vidzeme", "Parnu", "Virumaa", "Pskov", "Latgale"]},
    {"name": "Tashauz", "neighbors": ["Karakalpakstan", "Khiva", "Ashkhabad", "Bukhara", "Navoi"]},
    {"name": "Tashkent", "neighbors": ["Kyzyl Orda", "Stalinabad", "Pamir", "Bukhara", "Navoi"]},
    {"name": "Tasmania", "neighbors": []},
    {"name": "Tehran", "neighbors": ["Semnan", "Hamadan", "Gilan", "Ashkhabad", "Khorasan"]},
    {"name": "Telemark", "neighbors": ["Agder", "Opplandene", "Vestlandet", "Oslofjord"]},
    {"name": "Tennessee", "neighbors": ["Mississippi", "Alabama", "Arkansas", "Missouri", "Kentucky", "Virginia", "North Carolina", "Georgia US"]},
    {"name": "Texas", "neighbors": ["Louisiana", "Arkansas", "Oklahoma", "New Mexico", "Chihuahua", "Tamaulipas", "Coahuila"]},
    {"name": "The Moluccas", "neighbors": []},
    {"name": "Thrace", "neighbors": ["Plovdiv", "Burgas", "Central Macedonia", "Edirne"]},
    {"name": "Thuringen", "neighbors": ["Franken", "Hessen", "Hannover", "Brandenburg", "Sachsen"]},
    {"name": "Tibriz", "neighbors": ["Gilan", "Kurdistan", "Mosul", "Van", "Hakkari", "Armenia", "Azerbaijan"]},
    {"name": "Ticino", "neighbors": ["Lombardia", "Piemonte", "Eastern Swiss Alps", "Western Swiss Alps"]},
    {"name": "Tierra del Fuego", "neighbors": ["Magallanes"]},
    {"name": "Tigray", "neighbors": ["Eritrea", "Begemder", "Afar", "Wello"]},
    {"name": "Tikhvin", "neighbors": ["Yaroslavl", "Vologda", "Olonets", "Novgorod", "Volkhov", "Rzhev", "Kalinin"]},
    {"name": "Tlemcen", "neighbors": ["Algiers", "Constantine", "Tunisia", "Gabes", "Algerian Desert", "Marrakech", "Casablanca"]},
    {"name": "Tobolsk", "neighbors": ["Sverdlovsk", "Perm", "Northern Urals", "Salekhard", "Surgut", "Tyumen"]},
    {"name": "Tocantins", "neighbors": ["Maranhao", "Piaui", "Bahia", "Para", "Minas Gerais", "Goias", "Mato Grosso"]},
    {"name": "Togo", "neighbors": ["Ghana", "Upper Volta", "Dahomey"]},
    {"name": "Tohoku", "neighbors": ["Hokuriku", "Kanto"]},
    {"name": "Tokai", "neighbors": ["Koshinetsu", "Kansai", "Kanto"]},
    {"name": "Tombouctou", "neighbors": ["Gao", "Mauritanian Desert", "Algerian Desert", "Southern Sahara"]},
    {"name": "Tomsk", "neighbors": ["Surgut", "Yeniseisk", "Tyumen", "Omsk", "Novosibirsk", "Khakassia", "Krasnoyarsk"]},
    {"name": "Tonkin", "neighbors": ["Nanning", "Guangxi", "Yunnan", "Laos", "Southern Indochina"]},
    {"name": "Toscana", "neighbors": ["Piemonte", "Emilia Romagna", "Abruzzo", "Lazio"]},
    {"name": "Trabzon", "neighbors": ["Samsun", "Sivas", "Tunceli", "Van", "Armenia", "Georgia"]},
    {"name": "Transdanubia", "neighbors": ["Lower Austria", "Southern Slovakia", "Northern Hungary", "North Slovenia", "Alfold", "Croatia", "Vojvodina"]},
    {"name": "Transvaal", "neighbors": ["Rhodesia", "Bechuanaland", "Cape", "Natal", "Lourenco Marques"]},
    {"name": "Transylvania", "neighbors": ["Crisana", "Banat", "North Transylvania", "Oltenia", "Muntenia", "Moldova"]},
    {"name": "Trentino", "neighbors": ["Alto Adige", "Veneto", "Lombardia"]},
    {"name": "Tripoli", "neighbors": ["El Agheila", "Gabes", "Tripolitania"]},
    {"name": "Tripolitania", "neighbors": ["Tripoli", "El Agheila", "Sirte", "Libyan Desert", "Gabes"]},
    {"name": "Troms", "neighbors": ["Finnmark", "Lappi", "Norrbotten", "Nordland"]},
    {"name": "Trondelag", "neighbors": ["Helgeland", "Jamtland", "Dalarna", "Opplandene", "Vestlandet"]},
    {"name": "Tucuman", "neighbors": ["Los Andes", "Chaco Austral", "San Juan y La Rioja", "Atacama", "Antofagasta"]},
    {"name": "Tula", "neighbors": ["Moscow", "Kaluga", "Orel", "Lipetsk", "Ryazan"]},
    {"name": "Tunceli", "neighbors": ["Trabzon", "Van", "Hakkari", "Diyarbakir", "Malatya", "Sivas"]},
    {"name": "Tunisia", "neighbors": ["Gabes", "Tlemcen", "Constantine"]},
    {"name": "Turku", "neighbors": ["Vaasa", "Hame", "Uusimaa"]},
    {"name": "Tyrol", "neighbors": ["North Slovenia", "Upper Austria", "Oberbayern", "Vorarlberg", "Eastern Swiss Alps", "Alto Adige", "Veneto", "Litorale"]},
    {"name": "Tyumen", "neighbors": ["Tomsk", "Surgut", "Tobolsk", "Sverdlovsk", "Chelyabinsk", "Akmolinsk", "Omsk"]},
    {"name": "Ucayali", "neighbors": ["Acre", "Santa Cruz", "La Paz", "Arequipa", "Lima", "Loreto", "Amazon impassable 4"]},
    {"name": "Udachny", "neighbors": ["Verkhoyansk", "Yakutsk", "Kirensk", "Khatangsky"]},
    {"name": "Udmurtia", "neighbors": ["Ufa", "Kazan", "Kirov", "Perm"]},
    {"name": "Ufa", "neighbors": ["Udmurtia", "Perm", "Zlatoust", "Magnitogorsk", "Orenburg", "Kazan"]},
    {"name": "Uganda", "neighbors": ["Nyanza Rift Valley", "Tanganyika", "Rwanda", "Costermansville", "Stanleyville", "Bahr al Ghazal", "Upper Nile"]},
    {"name": "Ulaanbaatar", "neighbors": ["Dornod", "Gobi", "Khovd", "Khovsgol", "Buryatia", "Chita"]},
    {"name": "Ulyanovsky", "neighbors": ["Kuybyshev", "Saratov", "Penza", "Gorky", "Chuvashia", "Kazan"]},
    {"name": "Upper Austria", "neighbors": ["Sudetenland", "Lower Austria", "North Slovenia", "Litorale", "Tyrol", "Oberbayern", "Niederbayern"]},
    {"name": "Upper British Columbia", "neighbors": ["Alaska", "Yukon Territory", "Northwest Territories", "Alberta", "British Columbia"]},
    {"name": "Upper Nile", "neighbors": ["Sidamo", "Illubabor Kaffa", "Welega", "Blue Nile", "Kurdufan", "Bahr al Ghazal", "Uganda", "Nyanza Rift Valley"]},
    {"name": "Upper Volta", "neighbors": ["Ghana", "Togo", "Dahomey", "Niger", "Gao", "Bamako", "Ivory Coast"]},
    {"name": "Uralsk", "neighbors": ["Orenburg", "Akhtubinsk", "Guryev", "Astrakhan", "Stalingrad", "Engels Marxstadt", "Balakovo"]},
    {"name": "Uruguay", "neighbors": ["Cerro Largo", "Paysandu"]},
    {"name": "Urumqi", "neighbors": ["Kunlun Shan", "Taklamakan", "Yarkand", "Pamir", "Alma Ata", "Ayaguz", "Dzungaria", "Dabancheng"]},
    {"name": "Ust Urt", "neighbors": ["Ashkhabad", "Karakalpakstan", "Akhtubinsk", "Guryev"]},
    {"name": "Utah", "neighbors": ["Arizona", "Nevada", "Idaho", "Wyoming", "Colorado"]},
    {"name": "Uusimaa", "neighbors": ["Kymi", "Mikkeli", "Hame", "Turku"]},
    {"name": "Vaasa", "neighbors": ["Oulu", "Kuopio", "Mikkeli", "Hame", "Turku"]},
    {"name": "Valencia", "neighbors": ["Cataluna", "Eastern Aragon", "Guadalajara", "Murcia"]},
    {"name": "Valladolid", "neighbors": ["Asturias", "Burgos", "Guadalajara", "Madrid", "Salamanca", "Leon"]},
    {"name": "Van", "neighbors": ["Armenia", "Tibriz", "Hakkari", "Tunceli", "Trabzon"]},
    {"name": "Vancouver Island", "neighbors": []},
    {"name": "Var", "neighbors": ["Bouches du Rhone", "Savoy"]},
    {"name": "Varmland", "neighbors": ["Sodermalm", "Vastergotland", "Bohuslan", "Oslofjord", "Opplandene", "Dalarna"]},
    {"name": "Vasterbotten", "neighbors": ["Norrbotten", "Nordland", "Helgeland", "Jamtland", "Gavleborg"]},
    {"name": "Vastergotland", "neighbors": ["Varmland", "Sodermalm", "Ostergotland", "Smaland", "Skane", "Bohuslan"]},
    {"name": "Veneto", "neighbors": ["Emilia Romagna", "Lombardia", "Trentino", "Alto Adige", "Tyrol", "Litorale"]},
    {"name": "Veracruz", "neighbors": ["Oaxaca", "Guerrero", "Mexico City", "Tamaulipas"]},
    {"name": "Verkhoyansk", "neighbors": ["Kolyma", "Okhotsk", "Yakutsk", "Udachny"]},
    {"name": "Vestlandet", "neighbors": ["Trondelag", "Opplandene", "Telemark", "Agder"]},
    {"name": "Victoria", "neighbors": ["New South Wales", "South Australia"]},
    {"name": "Vidzeme", "neighbors": ["Parnu", "Tartu", "Latgale", "Riga"]},
    {"name": "Vinnytsia", "neighbors": ["Cherkasy", "Kyiv", "Zhytomyr", "Khmelnytskyi", "Bessarabia", "Balta Tiraspol"]},
    {"name": "Virginia", "neighbors": ["Maryland", "West Virginia", "Kentucky", "Tennessee", "North Carolina"]},
    {"name": "Virumaa", "neighbors": ["Luga", "Pskov", "Tartu", "Parnu", "Harju"]},
    {"name": "Vitebsk", "neighbors": ["Latgale", "Wilejka", "Minsk", "Gomel", "Smolensk", "Nevel"]},
    {"name": "Vlaanderen", "neighbors": ["Brabant", "Wallonie", "Nord Pas de Calais"]},
    {"name": "Vladivostok", "neighbors": ["Khabarovsk", "Sungkiang", "North Korea"]},
    {"name": "Vojvodina", "neighbors": ["Alfold", "West Banat", "Croatia", "Transdanubia"]},
    {"name": "Volgodonsk", "neighbors": ["Kalmykia", "Stalingrad", "Millerovo", "Rostov", "Krasnodar", "Stavropol"]},
    {"name": "Volkhov", "neighbors": ["Tikhvin", "Novgorod", "Luga", "Leningrad"]},
    {"name": "Vologda", "neighbors": ["Gorky", "Kirov", "Kotlas", "Kargopol", "Olonets", "Tikhvin", "Yaroslavl", "Ivanovo"]},
    {"name": "Vorarlberg", "neighbors": ["Tyrol", "Oberbayern", "Wurttemberg", "Swiss Plateau", "Eastern Swiss Alps"]},
    {"name": "Voronezh", "neighbors": ["Saratov", "Mikhaylovka", "Millerovo", "Voroshilovgrad", "Belgorod", "Kursk", "Lipetsk", "Tambov"]},
    {"name": "Voroshilovgrad", "neighbors": ["Voronezh", "Millerovo", "Rostov", "Stalino", "Kharkov", "Belgorod"]},
    {"name": "Vorpommern", "neighbors": ["Hinterpommern", "Ostmark", "Brandenburg", "Mecklenburg"]},
    {"name": "Wales", "neighbors": ["Lancashire", "West Midlands", "Gloucestershire"]},
    {"name": "Wallonie", "neighbors": ["Vlaanderen", "Brabant", "Rhineland", "Moselland", "Luxembourg", "Alsace Lorraine", "Champagne", "Picardy", "Nord Pas de Calais"]},
    {"name": "Warszawa", "neighbors": ["Bialystok", "Lublin", "Kielce", "Lodz", "Plock"]},
    {"name": "Washington", "neighbors": ["British Columbia", "Idaho", "Oregon"]},
    {"name": "Welega", "neighbors": ["Blue Nile", "Upper Nile", "Illubabor Kaffa", "Shewa", "Gojjam"]},
    {"name": "Wello", "neighbors": ["Afar", "Shewa", "Gojjam", "Begemder", "Tigray"]},
    {"name": "Weser Ems", "neighbors": ["Hannover", "Westfalen", "Friesland"]},
    {"name": "West Banat", "neighbors": ["Vojvodina", "Alfold", "Banat", "Serbia", "Croatia"]},
    {"name": "West Bengal", "neighbors": ["East Bengal", "Assam", "Bhutan", "Shigatse", "Nepal", "Bihar", "Orissa"]},
    {"name": "West Midlands", "neighbors": ["East Midlands", "Yorkshire", "Lancashire", "Wales", "Gloucestershire"]},
    {"name": "West Papua", "neighbors": ["Papua"]},
    {"name": "West Virginia", "neighbors": ["Pennsylvania", "Virginia", "Maryland", "Kentucky", "Ohio"]},
    {"name": "Western Aragon", "neighbors": ["Midi Pyrenees", "Eastern Aragon", "Guadalajara", "Burgos", "Navarra", "Pyrenees Atlantiques"]},
    {"name": "Western Australia", "neighbors": ["North West Australia", "Central Australia", "South West Australia"]},
    {"name": "Western Desert", "neighbors": ["Matrouh", "Alexandria", "Cairo", "Aswan", "Khartoum", "North Darfur", "Libyan Desert"]},
    {"name": "Western Slovakia", "neighbors": ["Moravia", "Zaolzie", "Eastern Slovakia", "Southern Slovakia", "Lower Austria", "Sudetenland"]},
    {"name": "Western Swiss Alps", "neighbors": ["Swiss Plateau", "Eastern Swiss Alps", "Ticino", "Piemonte", "Savoy"]},
    {"name": "Westfalen", "neighbors": ["Weser Ems", "Hannover", "Hessen", "Rhineland", "Friesland"]},
    {"name": "Wilejka", "neighbors": ["Vitebsk", "Minsk", "Nowogrodek", "Wilno", "Zemgale", "Latgale"]},
    {"name": "Wilno", "neighbors": ["Zemgale", "Wilejka", "Nowogrodek", "Suduva", "Kaunas", "Aukstaitija"]},
    {"name": "Wisconsin", "neighbors": ["Minnesota", "Iowa", "Illinois", "Michigan"]},
    {"name": "Wolyn", "neighbors": ["Mozyr", "Polesie", "Lublin", "Lwow", "Khmelnytskyi", "Zhytomyr"]},
    {"name": "Wurttemberg", "neighbors": ["Oberbayern", "Franken", "Hessen", "Moselland", "Alsace Lorraine", "Jura Mountains", "Swiss Plateau", "Vorarlberg"]},
    {"name": "Wyoming", "neighbors": ["Montana", "South Dakota", "Nebraska", "Colorado", "Utah", "Idaho"]},
    {"name": "Xian", "neighbors": ["Sichuan", "Hubei", "Henan", "Shanxi", "Shaanxi", "Gansu"]},
    {"name": "Xikang", "neighbors": ["Golog", "Qinghai", "Nagqu", "Shigatse", "Arunachal Pradesh", "Mandalay", "Dali", "Ganzi"]},
    {"name": "Yakutsk", "neighbors": ["Okhotsk", "Verkhoyansk", "Udachny", "Kirensk", "Bodaybo", "Chita", "Amur"]},
    {"name": "Yamalia", "neighbors": ["Salekhard", "Surgut", "Dudinka"]},
    {"name": "Yarkand", "neighbors": ["Urumqi", "Pamir", "Stalinabad", "Kabul", "Northern Kashmir", "Kashmir", "Taklamakan"]},
    {"name": "Yaroslavl", "neighbors": ["Vologda", "Tikhvin", "Kalinin", "Moscow", "Ivanovo"]},
    {"name": "Yemen", "neighbors": ["Asir Makkah", "Najiran", "Aden"]},
    {"name": "Yeniseisk", "neighbors": ["Khatangsky", "Dudinka", "Surgut", "Tomsk", "Krasnoyarsk", "Bratsk", "Kirensk"]},
    {"name": "Yorkshire", "neighbors": ["Northumberland", "Cumbria", "Lancashire", "West Midlands", "East Midlands"]},
    {"name": "Yucatan", "neighbors": ["British Honduras", "Guatemala", "Chiapas"]},
    {"name": "Yukon Territory", "neighbors": ["Alaska", "Upper British Columbia", "Northwest Territories"]},
    {"name": "Yunnan", "neighbors": ["Liangshan", "Dali", "Mandalay", "Laos", "Tonkin", "Guizhou", "Guangxi"]},
    {"name": "Zambesi", "neighbors": ["South West Angola", "Luanda", "Elisabethville", "Zambia", "Otjozondjupa"]},
    {"name": "Zambezia Mocambique", "neighbors": ["Manica e Sofala", "Malawi", "Tanganyika"]},
    {"name": "Zambia", "neighbors": ["Zambesi", "Elisabethville", "Tanganyika", "Manica e Sofala", "Malawi", "Rhodesia", "Bechuanaland", "Otjozondjupa"]},
    {"name": "Zaolzie", "neighbors": ["Eastern Slovakia", "Krakow", "Katowice", "Oberschlesien", "Eastern Sudetenland", "Moravia", "Western Slovakia"]},
    {"name": "Zaporozhe", "neighbors": ["Kherson", "Stalino", "Dnipropetrovsk"]},
    {"name": "Zara", "neighbors": ["Dalmatia"]},
    {"name": "Zemaitija", "neighbors": ["Kurzeme", "Zemgale", "Aukstaitija", "Kaunas", "Suduva", "Memel"]},
    {"name": "Zemgale", "neighbors": ["Riga", "Latgale", "Wilejka", "Wilno", "Aukstaitija", "Zemaitija", "Kurzeme"]},
    {"name": "Zhejiang", "neighbors": ["Fujian", "Jiangxi", "Huangshan", "Shanghai"]},
    {"name": "Zhytomyr", "neighbors": ["Vinnytsia", "Kyiv", "Mozyr", "Wolyn", "Khmelnytskyi"]},
    {"name": "Zlatoust", "neighbors": ["Magnitogorsk", "Ufa", "Perm", "Sverdlovsk", "Chelyabinsk"]},
    {"name": "Zulia", "neighbors": ["Miranda", "Cundinamarca", "La Libertad"]},
    {"name": "Zunyi", "neighbors": ["Guizhou", "Changde", "Sichuan", "Liangshan"]},
    ]
    coastal_states =['Aberdeenshire', 'Abkhazia', 'Abruzzo', 'Abu Dhabi', 'Aden', 'Agder', 'Akhtubinsk', 'Alabama', 'Alaska', 'Albania', 'Aleppo', 'Alexandria', 'Algiers', 'Amapa', 'Antalya', 'Antofagasta', 'Aquitaine', 'Araucania', 'Arequipa', 'Arica y Tarapaca', 'Arkhangelsk', 'Asir Makkah', 'Astrakhan', 'Asturias', 'Atacama', 'Attica', 'Aysen', 'Bahia', 'Baja California', 'Beijing', 'Beja', 'Benghasi', 'Benue', 'Bismarck', 'Bohuslan', 'Bolivar', 'Bombay', 'Bouches du Rhone', 'Baluchistan', 'Brabant', 'British Columbia', 'British Guyana', 'British Honduras', 'British Somaliland', 'Brittany', 'Burgas', 'Burma', 'Bursa', 'Cairo', 'Calabria', 'California', 'Cameroon', 'Campania', 'Cape', 'Casablanca', 'Cataluna', 'Ceara', 'Cebu', 'Central Islands', 'Central Macedonia', 'Cerro Largo', 'Ceylon', 'Chiapas', 'Chubut', 'Chugoku', 'Chukchi Peninsula', 'Chukotka', 'Connaught', 'Constantine', 'Corsica', 'Costa Rica', 'Cote Nord', 'Crimea', 'Cuba', 'Cumbria', 'Cundinamarca', 'Cyprus', 'Dagestan', 'Dahomey', 'Dalian', 'Dalmatia', 'Dammam', 'Danzig', 'Derna', 'Durango', 'Districts of Ontario', 'Dominican Republic', 'East Anglia', 'East Bengal', 'East Hebei', 'East Midlands', 'Easter Island', 'Eastern Desert', 'Ecuador', 'Edirne', 'El Agheila', 'El Salvador', 'Emilia Romagna', 'Epirus', 'Equatorial Guinea', 'Eritrea', 'Ermland Masuren', 'Espirito Santo', 'Fars', 'Finnmark', 'Florida', 'French Guiana', 'French India', 'French Somaliland', 'Friesland', 'Fujian', 'Gabes', 'Gabon', 'Galicia', 'Gambia', 'Garissa', 'Gavleborg', 'Gdynia', 'Georgia', 'Georgia US', 'Ghana', 'Gibraltar', 'Gilan', 'Gloucestershire', 'Goa', 'Gotland', 'Granada', 'Greater London Area', 'Greenland', 'Guangdong', 'Guangzhou', 'Guangzhouwan', 'Guatemala', 'Guerrero', 'Guinea', 'Gujarat', 'Guryev', 'Haida Gwaii', 'Hainan', 'Haiti', 'Hannover', 'Harju', 'Hatay', 'Hawaii', 'Hebei', 'Helgeland', 'Hinterpommern', 'Hokkaido', 'Hokuriku', 'Holland', 'Holstein', 'Iceland', 'Illinois', 'Indiana', 'Istanbul', 'Istria', 'Ivory Coast', 'Iwo Jima', 'Izmir', 'Izmit', 'Jalisco', 'Jamaica', 'Java', 'Jehol', 'Jiangsu', 'Jubaland', 'Jylland', 'Kalimantan', 'Kalmykia', 'Kamchatka', 'Kansai', 'Kanto', 'Karakalpakstan', 'Karas', 'Karjala', 'Kassala', 'Kastamonu', 'Khabarovsk', 'Kherson', 'Khiva', 'Khomas', 'Khuzestan', 'Konigsberg', 'Koshinetsu', 'Kunene', 'Kuopio', 'Kurzeme', 'Kuwait', 'Kymi', 'Kyushu', 'Labrador', 'Lagos', 'Lanark', 'Lancashire', 'Languedoc', 'Lappi', 'Lebanon', 'Leinster', 'Leningrad', 'Lesser Sunda Islands', 'Liberia', 'Lima', 'Lisbon', 'Litorale', 'Loire', 'Lothian', 'Louisiana', 'Lourenco Marques', 'Luanda', 'Luga', 'Luzon', 'Madagascar', 'Madinah', 'Madras', 'Madurai', 'Manica e Sofala', 'Magallanes', 'Malatya', 'Manila', 'Maranhao', 'Maryland', 'Matrouh', 'Maurice', 'Mauritania', 'Mecklenburg', 'Memel', 'Mersin', 'Middle Congo', 'Midi Pyrenees', 'Mindanao', 'Miranda', 'Mississippi', 'Mombasa', 'Montenegro', 'Munster', 'Muntenia', 'Murcia', 'Murmansk', 'Mykolaiv', 'Mysore', 'Nanning', 'Nenets', 'New Brunswick', 'New Caledonia', 'New England', 'New Jersey', 'New South Wales', 'New York', 'Newfoundland', 'Nicaragua', 'Nikolayevsk', 'Nord du Quebec', 'Nord Pas de Calais', 'Nordland', 'Normandy', 'Norrbotten', 'North Angola', 'North Borneo', 'North Carolina', 'North Island', 'North Korea', 'North Queensland', 'North Sakhalin', 'North West Australia', 'Northern Epirus', 'Northern Ireland', 'Northern Malay', 'Northern Manitoba', 'Northern Ontario', 'Northern Territory', 'Northumberland', 'Nova Scotia', 'Nunavut', 'Oaxaca', 'Odessa', 'Okhotsk', 'Okinawa', 'Olonets', 'Oman', 'Onega', 'Orissa', 'Oslofjord', 'Ostergotland', 'Ouest du Quebec', 'Oulu', 'Pais Vasco', 'Palestine', 'Pampas', 'Panama', 'Panama Canal', 'Papua', 'Para', 'Parana', 'Parnu', 'Paysandu', 'Peloponnese', 'Pennsylvania', 'Pernambuco', 'Petsamo', 'Piaui', 'Picardy', 'Piemonte', 'Poitou', 'Porto', 'Portuguese Guinea', 'Portuguese Timor', 'Puglia', 'Pyrenees Atlantiques', 'Qatar', 'Qingdao', 'Queensland', 'Region Mesopotamica', 'Riga', 'Rio de Janeiro', 'Rio de Oro', 'Rio Grande do Norte', 'Rio Negro', 'Rostov', 'Rub al Khali', 'Saint Lawrence', 'Salekhard', 'Samar', 'Saguenay', 'Samsun', 'Santa Catarina', 'Santa Cruz AR', 'Santiago', 'Sao Paulo', 'Sardegna', 'Savoy', 'Schleswig', 'Scottish Highlands', 'Senegal', 'Sevilla', 'Shandong', 'Shanghai', 'Shikoku', 'Shkoder', 'Siam', 'Sicilia', 'Sidi Ifni', 'Sierra Leone', 'Sinai', 'Sind', 'Singapore', 'Sistan', 'Sjaelland', 'Skane', 'Smaland', 'Sochi', 'Sodermalm', 'Solomon Islands', 'Sonderjylland', 'Sonora', 'South Australia', 'South Carolina', 'South Georgia', 'South Island', 'South Korea', 'South Sakhalin', 'South West Angola', 'South West Australia', 'South West England', 'Southern Bessarabia', 'Southern Indochina', 'Spanish Africa', 'Suez', 'Sulawesi', 'Sumatra', 'Suriname', 'Sussex', 'Tabuk', 'Taiwan', 'Tamaulipas', 'Tanganyika', 'Tasmania', 'Tehran', 'Telemark', 'Texas', 'The Moluccas', 'Thrace', 'Tierra del Fuego', 'Togo', 'Tohoku', 'Tokai', 'Tonkin', 'Toscana', 'Trabzon', 'Tripoli', 'Troms', 'Trondelag', 'Tunisia', 'Turku', 'Upper British Columbia', 'Uruguay', 'Ust Urt', 'Uusimaa', 'Vaasa', 'Valencia', 'Vancouver Island', 'Var', 'Vasterbotten', 'Vastergotland', 'Veneto', 'Veracruz', 'Vestlandet', 'Victoria', 'Vidzeme', 'Virginia', 'Virumaa', 'Vlaanderen', 'Vladivostok', 'Vorpommern', 'Washington', 'Weser Ems', 'West Bengal', 'West Papua', 'Western Australia', 'Yamalia', 'Yorkshire', 'Yucatan', 'Zambezia Mocambique', 'Zaporozhe', 'Zara', 'Zemaitija', 'Zemgale', 'Zhejiang']

    all_squares = Square.objects.filter(map=map_obj)
    square_by_name = {s.name: s for s in all_squares}
    squares = Square.objects.filter(map=map_obj, name__in=coastal_states)
    for square in squares:
        square.coastal = True
    Square.objects.bulk_update(squares, ['coastal'])

    updates = []

    for entry in neighbors_data:
        square_name = entry["name"]
        neighbor_names = entry["neighbors"]
        square = square_by_name[square_name]
        neighbor_numbers = [
            square_by_name[n].number
            for n in neighbor_names
            if n in square_by_name
        ]
        square.neighbors = neighbor_numbers
        updates.append(square)

    # Bulk update only the `neighbors` field
    Square.objects.bulk_update(updates, ['neighbors'])
    

    announcements = Announcements.objects.create(text =f"The game starts", start_time = datetime.now(), game = Games.objects.get(id = game_id))
    
    def upload_pil_image_to_imgbb(pil_image, api_key):
        try:
            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG", optimize=True)
            encoded_image = base64.b64encode(buffer.getvalue())

            response = requests.post(
                "https://api.imgbb.com/1/upload",
                data={"key": api_key, "image": encoded_image}
            )
            result = response.json()
            if result.get("success"):
                return result["data"]["url"], result["data"]["delete_url"]
            else:
                raise Exception(result)
        except Exception as e:
            print(f"Image upload failed: {e}")
            raise

    final_image = Image.open("AWSDefcon1App/static/AWSDefcon1App/starting_image.png")
    try:
        image_url, delete_url = upload_pil_image_to_imgbb(final_image, api_key)
        map_instance = Map.objects.get(game_id=game_id)

        if map_instance.deleteURL:
            try:
                requests.get(map_instance.deleteURL)
            except requests.RequestException as e:
                print(f"Failed to delete old image: {e}")

        map_instance.URL = image_url
        map_instance.deleteURL = delete_url
        map_instance.save()
    except Exception as e:
        return HttpResponse(f"Image upload failed: {e}", status=500)
    

    return HttpResponseRedirect(reverse('full_index'))
