import json
from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        
        if data.get('action'):
            # Handle special actions (delete/edit)
            action = data['action']
            message_id = data.get('message_id')
            username = data['username']
            room = data['room']
            
            if action == 'delete':
                # Verify user can delete this message
                if await self.verify_message_owner(username, message_id) or await self.verify_room_owner(username, room):
                    await self.delete_message(message_id)
                    
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'action': 'delete',
                            'message_id': message_id,
                            'username': username,
                            'room': room
                        }
                    )
            
            elif action == 'edit':
                # Verify user can edit this message
                if await self.verify_message_owner(username, message_id):
                    new_content = data['new_content']
                    await self.update_message(message_id, new_content)
                    
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'action': 'edit',
                            'message_id': message_id,
                            'message': new_content,
                            'username': username,
                            'room': room
                        }
                    )
        else:
            # Handle regular messages
            message = data['message']
            username = data['username']
            room = data['room']

            message_obj = await self.save_message(username, room, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'room': room,
                    'message_id': message_obj.id
                }
            )

    async def chat_message(self, event):
        # Send the appropriate data based on action type
        if event.get('action') == 'delete':
            await self.send(text_data=json.dumps({
                'action': 'delete',
                'message_id': event['message_id']
            }))
        elif event.get('action') == 'edit':
            await self.send(text_data=json.dumps({
                'action': 'edit',
                'message_id': event['message_id'],
                'message': event['message']
            }))
        else:
            # Regular message
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'username': event['username'],
                'message_id': event['message_id']
            }))

    @sync_to_async
    def save_message(self, username, room_slug, content):
        user = User.objects.get(username=username)
        room = Room.objects.get(slug=room_slug)
        message = Message.objects.create(user=user, room=room, content=content)
        return message

    @sync_to_async
    def delete_message(self, message_id):
        Message.objects.filter(id=message_id).delete()

    @sync_to_async
    def update_message(self, message_id, new_content):
        Message.objects.filter(id=message_id).update(content=new_content)

    @sync_to_async
    def verify_message_owner(self, username, message_id):
        try:
            message = Message.objects.get(id=message_id)
            return message.user.username == username
        except Message.DoesNotExist:
            return False

    @sync_to_async
    def verify_room_owner(self, username, room_slug):
        try:
            room = Room.objects.get(slug=room_slug)
            return room.dono.username == username
        except Room.DoesNotExist:
            return False