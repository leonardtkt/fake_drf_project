from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AnonymousUser

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

from users.serializers import UserSerializer
from users.models import User


logger = logging.getLogger('sockets')


class UserConsumer(AsyncJsonWebsocketConsumer):
    """ Allows frontend to subscribe to updates to their user instance. """

    serializer_class = UserSerializer

    async def connect(self) -> None:
        """ On connect register them in their own private group so we can
        communicate with them directly from a Django signal later. """

        # need to be logged in or blocked
        user = self.scope.get('user')
        if not user or isinstance(user, AnonymousUser):
            await self.close()
            logger.info('Failed user subscribe from anonymous user. Connection closed.')
        else:
            await self.accept()
            user_pk = self.scope['user'].pk
            self.group_name = f'ws-user-{user_pk}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            logger.info(f'User subscribed to updates - group_name: {self.group_name}')

    async def user_update(self, event: dict) -> None:
        """ This can be called from an external function by using django channel's `group_send` """

        logger.info(f'Sending user update to group_name {self.group_name}.')
        resp = {
            'msg_type': 'user.updated',
            'msg_content': event['text']
        }
        await self.send_json(resp)


@receiver(post_save, sender=User, dispatch_uid='update_user_overwatchers')
def update_user_watchers(sender, instance, **kwargs):
    """
    Tells anyone subscribed to an User instance that it's been modified
    and gives them the new data.
    """

    logger.debug(f'Signal received that user #{instance.pk} has been updated.')
    group_name = f'ws-user-{instance.pk}'
    serializer = UserSerializer(instance)

    channel_layer = get_channel_layer()

    data = {
        'type': 'user.update',
        'text': serializer.data
    }
    logger.debug(f'Passing this data to the consumer with group_name {group_name}: {data}.')

    # since group_send is a async process but signals are sync,
    # the `async_to_sync` function is critically important here
    async_to_sync(channel_layer.group_send)(group_name, data)
