from django.db import models
from django.conf import settings 
from django.utils import timezone


class ChatRoom(models.Model):
    """
    Inasimamia chumba cha mazungumzo (Direct Message) kati ya watumiaji wawili.
    """
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='chats_as_user1', 
        on_delete=models.CASCADE,
        verbose_name="Mshiriki wa Kwanza"
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='chats_as_user2', 
        on_delete=models.CASCADE,
        verbose_name="Mshiriki wa Pili"
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Imeundwa Lini")
    
    class Meta:
        verbose_name = "Chumba cha Chat"
        verbose_name_plural = "Vyumba vya Chat"
        
        constraints = [
            models.UniqueConstraint(
                # Hii inalinda Room moja tu kwa kila jozi ya watumiaji
                fields=['user1', 'user2'],
                name='unique_chat_room'
            )
        ]
        
        # TUMEFUTA MSTARI HUU: index_together = (("user1", "user2"),) # Ulikuwa unaleta kosa
        
    def get_other_user(self, current_user):
        """Inarudisha mtumiaji mwingine kwenye chumba hiki."""
        return self.user1 if self.user2.pk == current_user.pk else self.user2
    
    def __str__(self):
        return f"Chat kati ya {self.user1.username} na {self.user2.username} (ID: {self.pk})"

class Message(models.Model):
    """
    Inasimamia ujumbe mmoja unaotumwa ndani ya ChatRoom.
    """
    room = models.ForeignKey(
        ChatRoom, 
        related_name='messages', 
        on_delete=models.CASCADE,
        verbose_name="Chumba"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='sent_messages', 
        on_delete=models.CASCADE,
        verbose_name="Mtumaji"
    )
    content = models.TextField(verbose_name="Maudhui ya Ujumbe")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Muda wa Kutuma")

    class Meta:
        ordering = ('timestamp',) # Panga ujumbe kwa muda
        verbose_name = "Ujumbe"
        verbose_name_plural = "Ujumbe"

    def __str__(self):
        return f'Ujumbe kutoka {self.sender.username} saa {self.timestamp.strftime("%H:%M")}'
