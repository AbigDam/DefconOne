from django.urls import path
from django.conf.urls import handler404, handler500, handler403
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('joingame/<int:game_id>/<int:player_number>/', views.join, name='joingame'),
    path('game/<int:game_id>',views.game,name='game'),
    path('map/<int:game_id>', views.map, name = 'map'),
    path('makegame/<int:game_id>', views.makegame, name = 'makegame'),
    path('diplomacy/<int:game_id>', views.diplomacy, name="diplomacy"),
    path('war/<int:game_id>', views.war, name="war"),
    path('current_wars/<int:game_id>', views.current_wars, name='current_wars'),
    path('makealliance/<int:game_id>', views.makealliance, name='makealliance'),
    path('battle/<int:game_id>', views.battle, name='battle'),
    path('focus/<int:game_id>', views.focus, name='focus'),
    path('send/<int:game_id>', views.send, name='send'),
    path('new/<int:game_id>', views.new, name='new'),
    path('beg/<int:game_id>', views.beg, name='beg'),
    path('announcement/<int:game_id>', views.announcemnts, name='announcement'),
    path('message/<int:game_id>/<int:recipient_id>', views.message, name='message'),
    path('passer/<int:game_id>', views.passer, name='passer'),
    path('users/<int:game_id>', views.user_list, name='user_list'),
    path('profile/<int:user_id>', views.profile, name='profile'),
    path('DM/<int:recipient_id>', views.SendDM, name='DM'),
    path('spies/<int:game_id>', views.spies, name='spies'),


]
handler404 = 'AWSDefcon1App.views.error'
handler500 = 'AWSDefcon1App.views.error500'
handler403 = 'AWSDefcon1App.views.error'