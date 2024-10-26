from django.contrib import admin

from .models import User,Games,Nations,Map,Square,War,MakeAlliance,Announcements,Message, Achievements,DM

# Register your models here
admin.site.register(Games)
admin.site.register(User)
admin.site.register(Nations)
admin.site.register(Square)
admin.site.register(Map)
admin.site.register(War)
admin.site.register(MakeAlliance)
admin.site.register(Announcements)
admin.site.register(Message)
admin.site.register(Achievements)
admin.site.register(DM)
