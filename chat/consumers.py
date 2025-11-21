import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from django.utils import timezone
from asgiref.sync import sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    # -----------------------------------------------------------------
    # 1. Kazi za kusaidia (Synchronous) zinazoendesha kwenye thread tofauti
    # -----------------------------------------------------------------
    
    @sync_to_async
    def get_room_and_user(self, room_id):
        """Inapata ChatRoom na inahakikisha mtumiaji yupo (authentication)."""
        user = self.scope["user"]
        
        # Inafanya kazi ya kuthibitisha mtumiaji ni mshiriki.
        # Tunarudisha None na kuacha Consumer ifunge muunganisho kama haijathibitishwa.
        if not user.is_authenticated:
            print("USER AUTH ERROR: Mtumiaji hajaingia.")
            return None, None
            
        try:
            # Tafuta chumba kwa ID, au inatupa 404 (exception)
            room = ChatRoom.objects.get(pk=room_id)
            
            # Hakikisha mtumiaji ni mshiriki wa chumba hicho
            if user != room.user1 and user != room.user2:
                print(f"USER AUTH ERROR: Mtumiaji {user.username} si mshiriki wa chumba {room_id}.")
                return None, None
            
            return room, user
        except ChatRoom.DoesNotExist:
            print(f"ROOM ERROR: Chumba {room_id} hakipo.")
            return None, None

    @database_sync_to_async
    def save_message(self, room, sender, message_content):
        """Inahifadhi ujumbe kwenye database."""
        # Weka ujumbe mpya
        Message.objects.create(
            room=room,
            sender=sender,
            content=message_content,
            timestamp=timezone.now()
        )
        # Rudisha jina la mtumaji ili litumike kwenye Group message
        return sender.username

    # -----------------------------------------------------------------
    # 2. Kazi za ASYNCHRONOUS (WebSockets Handling)
    # -----------------------------------------------------------------

    async def connect(self):
        """Inaunganisha mtumiaji na WebSocket na kumwingiza kwenye Group."""
        
        # Tofauti na hapo awali, inatumia room_id iliyopitishwa kama room_name kwenye routing
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Tunakubali muunganisho kwanza. Kama kutakuwa na kosa la DB tutafunga baada ya accept.
        await self.accept() # Fungua muunganisho wa Socket
        
        # Angalia kama chumba na mtumiaji ni halali kwa kutumia DB
        self.room, self.user = await self.get_room_and_user(self.room_id)
        
        if self.room is None or self.user is None:
            # Kama haijathibitishwa au chumba hakipo/haihusiki, tunafunga muunganisho
            print(f"Closing socket for room {self.room_id} due to Auth/Room error.")
            await self.close(code=4003) # Tumia code tofauti kwa error
            return
            
        # Ingiza kwenye Group/Channel Layer
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Ujumbe wa uthibitisho (hiari)
        await self.send(text_data=json.dumps({'type': 'connection_status', 'message': 'Connected successfully'}))


    async def disconnect(self, close_code):
        """Inamtoa mtumiaji kwenye Group/Channel Layer."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Inapokea ujumbe kutoka kwa WebSocket na kuutuma kwenye Group."""
        # Hakikisha user ame-login na room ipo kabla ya kupokea ujumbe
        if self.room is None or self.user is None:
            await self.send(text_data=json.dumps({'error': 'You are not authorized or the room does not exist.'}))
            return

        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        if not message.strip():
            # Puuza ujumbe mtupu
            return

        # Hifadhi ujumbe kwenye database
        sender_username = await self.save_message(self.room, self.user, message)
        
        # Tuma ujumbe kwa Group/Channel Layer
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', 
                'message': message,
                'username': sender_username,
                # Tunatumia strftime kwa sababu Javascript haielewi objects za timezone
                'timestamp': timezone.now().strftime("%I:%M %p") 
            }
        )

    # -----------------------------------------------------------------
    # 3. Mfumo wa Channel Layer
    # -----------------------------------------------------------------

    async def chat_message(self, event):
        """Inapokea ujumbe kutoka kwa Group na kuutuma kwa WebSocket ya mtumiaji."""
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']

        # Tuma ujumbe moja kwa moja kwa WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'timestamp': timestamp,
        }))