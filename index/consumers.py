# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Thread, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'chat_{self.thread_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    @database_sync_to_async
    def check_permission(self):
        try:
            thread = Thread.objects.get(id=self.thread_id)
            
            # 1. If it's a class thread, check if user is a student or teacher of that class
            if thread.eclass:
                eclass = thread.eclass
                # Check if user is a student in the class
                is_student = eclass.students.filter(user=self.user).exists()
                # Check if user is a teacher in the class
                is_teacher = eclass.teachers.filter(user=self.user).exists()
                return is_student or is_teacher
            
            # 2. If it's a private thread, check if user is in participants
            return self.user in thread.participants.all()
            
        except Thread.DoesNotExist:
            return False

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = self.scope['user']

        # Save to database
        await self.save_message(user, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': user.username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))

    @database_sync_to_async
    def save_message(self, user, message):
        thread = Thread.objects.get(id=self.thread_id)
        ChatMessage.objects.create(thread=thread, sender=user, text=message)