import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Product, Category

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json.get('username', 'Anonymous')
        message_type = text_data_json.get('type', 'message')
        
        if message_type == 'message':
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'timestamp': timezone.now().isoformat()
                }
            )
        elif message_type == 'typing':
            # Send typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'username': username,
                    'is_typing': text_data_json.get('is_typing', False)
                }
            )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))
    
    async def typing_indicator(self, event):
        # Send typing indicator to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': event['username'],
            'is_typing': event['is_typing']
        }))

class CustomerSupportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = 'customer_support'
        
        # Join customer support group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify support agents that a user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'username': self.user.username if self.user.is_authenticated else 'Anonymous',
                'user_id': self.user.id if self.user.is_authenticated else None
            }
        )
    
    async def disconnect(self, close_code):
        # Notify support agents that a user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'username': self.user.username if self.user.is_authenticated else 'Anonymous',
                'user_id': self.user.id if self.user.is_authenticated else None
            }
        )
        
        # Leave customer support group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message_type = text_data_json.get('type', 'message')
        
        if message_type == 'message':
            # Save message to database (if needed)
            await self.save_message(message)
            
            # Send message to support group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'support_message',
                    'message': message,
                    'username': self.user.username if self.user.is_authenticated else 'Anonymous',
                    'user_id': self.user.id if self.user.is_authenticated else None,
                    'timestamp': timezone.now().isoformat(),
                    'is_support': False
                }
            )
        elif message_type == 'product_query':
            # Handle product-specific queries
            product_id = text_data_json.get('product_id')
            if product_id:
                product_info = await self.get_product_info(product_id)
                await self.send(text_data=json.dumps({
                    'type': 'product_info',
                    'product': product_info
                }))
    
    async def support_message(self, event):
        # Send support message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
            'is_support': event.get('is_support', False)
        }))
    
    async def user_joined(self, event):
        # Notify when a user joins
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'user_id': event['user_id']
        }))
    
    async def user_left(self, event):
        # Notify when a user leaves
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
            'user_id': event['user_id']
        }))
    
    @database_sync_to_async
    def save_message(self, message):
        # Save message to database (implement if needed)
        pass
    
    @database_sync_to_async
    def get_product_info(self, product_id):
        try:
            product = Product.objects.get(id=product_id)
            return {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'description': product.description[:200],
                'available': product.available,
                'image': product.image.url if product.image else None
            }
        except Product.DoesNotExist:
            return None

class LiveChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'live_chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json.get('username', 'Anonymous')
        message_type = text_data_json.get('type', 'message')
        
        if message_type == 'message':
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'live_chat_message',
                    'message': message,
                    'username': username,
                    'timestamp': timezone.now().isoformat()
                }
            )
        elif message_type == 'file_share':
            # Handle file sharing
            file_info = text_data_json.get('file_info')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'file_shared',
                    'username': username,
                    'file_info': file_info,
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    async def live_chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))
    
    async def file_shared(self, event):
        # Send file share notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'file_share',
            'username': event['username'],
            'file_info': event['file_info'],
            'timestamp': event['timestamp']
        }))
