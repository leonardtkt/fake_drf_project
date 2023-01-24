from channels.testing import WebsocketCommunicator
from channels.auth import AuthMiddlewareStack
from asgiref.sync import sync_to_async


from contrib.consumers import UserConsumer
from contrib.tests.base import BaseTestCase
from users.models import User


class WebsocketTests(BaseTestCase):
    async def test_user_sub_but_not_logged_in(self):
        """ Must be logged in to connect to this websocket - so this should fail. """

        communicator = WebsocketCommunicator(UserConsumer.as_asgi(), 'ws/user-watcher/')
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_user_sub_and_logged_in(self):
        """ Must be logged in to connect to this websocket - so this should succeed. """

        user = await sync_to_async(User.objects.create, thread_sensitive=True)(username='bob')
        app = AuthMiddlewareStack(UserConsumer.as_asgi())
        communicator = WebsocketCommunicator(app, 'ws/user-watcher/')
        communicator.scope['user'] = user

        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_subscriber_receives_messages(self):
        """ When user instance is updated, we should get a notification from the server. """

        user = await sync_to_async(User.objects.create, thread_sensitive=True)(username='bob')
        app = AuthMiddlewareStack(UserConsumer.as_asgi())

        communicator = WebsocketCommunicator(app, 'ws/user-watcher/')
        communicator.scope['user'] = user

        await communicator.connect()
        user.username = 'gao'
        await sync_to_async(user.save)()
        response = await communicator.receive_json_from()

        self.assertEqual(response['msg_content']['username'], 'gao')
        await communicator.disconnect()
