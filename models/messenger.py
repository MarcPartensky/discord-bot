from fbchat import Client
from fbchat.models import *


class MessengerClient(Client):
    def onMessage(
        self,
        author_id=None,
        message_object=None,
        thread_id=None,
        thread_type=ThreadType.USER,
        **kwargs
    ):
        self.markAsRead(author_id)
        msgText = message_object.text
        # reply = Répondre(msgText)
        reply = "nope"

        # Send message
        if author_id != self.uid:
            self.send(Message(text=reply), thread_id=thread_id, thread_type=thread_type)

        # Mark message as delivered
        self.markAsDelivered(author_id, thread_id)


# Create an object of our class, enter your email and password for facebook.
# client = Jarvis("marc.partensky@free.fr", "CRAM69")

# Listen for new message
# client.listen()
