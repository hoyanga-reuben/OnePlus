from django.urls import path
from . import views

# Tunatumia namespace 'chat' kama inavyotakiwa na views.py (redirect('chat:room', ...))
app_name = 'chat' 

urlpatterns = [
    # URL ya kuunda au kupata chumba cha chat (kutoka kwenye orodha ya watumiaji)
    # Mfano wa URL: /chat/start/5/ (5 ni ID ya mtumiaji mwingine)
    path('start/<int:other_user_id>/', views.start_or_get_chat_room, name='start_chat'),
    
    # URL ya kuonyesha chumba halisi cha chat
    # Mfano wa URL: /chat/123/ (123 ni ID ya ChatRoom)
    path('<int:room_id>/', views.room, name='room'),
]