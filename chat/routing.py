from django.urls import re_path
from . import consumers

# Mfumo wa URL wa WebSockets.
# Kanuni: ws/chat/1/ -> inalingana na ChatConsumer
websocket_urlpatterns = [
    # Hakikisha 'ws/' na '$' vipo!
    re_path(r'^ws/chat/(?P<room_id>\d+)/$', consumers.ChatConsumer.as_asgi(), name='chat_room'),
]