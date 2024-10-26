# context_processors.py

from .models import Message, DM

def unread_messages(request):
    if request.user.is_authenticated:
        unread_game_messages_count = Message.objects.filter(receiver=request.user, read=False).count()
        unread_dms_count = DM.objects.filter(receiver=request.user, read=False).count()
        total_unread = unread_game_messages_count + unread_dms_count
    else:
        total_unread = 0

    return {
        'unread_messages_count': total_unread,
        'has_unread_messages': total_unread > 0,
    }
