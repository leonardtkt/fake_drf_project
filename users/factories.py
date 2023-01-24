from django.contrib.auth import get_user_model

import factory

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """ By default, this creates a non-superuser. """

    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('safe_email')
    username = factory.Faker('user_name')
    password = factory.PostGenerationMethodCall('set_password', 'password')
    is_active = True
    is_staff = False
    is_superuser = False
