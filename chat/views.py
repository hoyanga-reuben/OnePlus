
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import ChatRoom, Message

User = get_user_model()

@login_required
def start_or_get_chat_room(request, other_user_id):
    """
    Inaanzisha Chumba cha Chat na kuelekeza mtumiaji kwenye URL ya chumba hicho.
    """
    current_user = request.user
    
    # Hakikisha mtumiaji hajaribu kujichat mwenyewe
    if current_user.pk == other_user_id:
        # Unaweza kuongeza ujumbe wa kosa hapa ikiwa unataka
        return redirect('dashboard') # Badilisha na sehemu inayofaa kuelekeza
    
    other_user = get_object_or_404(User, pk=other_user_id)
    
    # 1. Jaribu kupata chumba kilichopo
    # Q objects inasaidia kutafuta bila kujali mpangilio wa user1 na user2
    room = ChatRoom.objects.filter(
        (Q(user1=current_user) & Q(user2=other_user)) | 
        (Q(user1=other_user) & Q(user2=current_user))
    ).first()
    
    # 2. Kama chumba hakipo, unda chumba kipya
    if not room:
        # Unda chumba. Tunahakikisha watumiaji wanapangwa kwa ID ndogo/kubwa
        # ili kuepuka duplicate rooms (UniqueConstraint inalinda hili pia)
        if current_user.pk < other_user_id:
            room = ChatRoom.objects.create(user1=current_user, user2=other_user)
        else:
            room = ChatRoom.objects.create(user1=other_user, user2=current_user)
            
    # Elekeza mtumiaji kwenye URL ya chumba chenye ID yake
    return redirect('chat:room', room_id=room.pk)


@login_required
def room(request, room_id):
    """
    Inaonyesha ukurasa wa Chat na historia ya ujumbe.
    """
    # Pata chumba, au rudisha 404
    chatroom = get_object_or_404(ChatRoom, pk=room_id)
    
    # Hakikisha mtumiaji aliye-login ni mmoja wa washiriki
    if request.user != chatroom.user1 and request.user != chatroom.user2:
        return redirect('dashboard') # Mzuie mtumiaji asiyehusika
        
    # Pata ujumbe 50 wa mwisho
    messages = Message.objects.filter(room=chatroom).order_by('-timestamp')[:50]
    
    # Mtumiaji mwingine kwenye chumba
    other_user = chatroom.get_other_user(request.user)
    
    context = {
        'room': chatroom,
        'other_user': other_user,
        # Tunatumia list() ili kuonyesha ujumbe wa zamani kwanza kwenye template
        'messages': list(messages), 
    }
    
    return render(request, 'chat/room.html', context)