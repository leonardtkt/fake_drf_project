from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth import get_user_model
from django.core.files.storage import get_storage_class
from django.core.cache import cache

from rest_framework import serializers

import uuid

from . import models

User = get_user_model()


class PublicGlobalSettingsSerializer(serializers.ModelSerializer):
    """ We're going to give frontend some global settings. """

    class Meta:
        model = models.PublicGlobalSettings
        exclude = ('id',)


class HealthSerializer(serializers.Serializer):
    """ Checks on various services and returns health report. """

    version = serializers.SerializerMethodField()
    storage = serializers.SerializerMethodField(method_name='is_storage_ok')
    postgres = serializers.SerializerMethodField(method_name='is_postgres_ok')

    def get_version(self, obj: dict) -> str:
        """ Allows us to have different projects returning different types of formats for an aggregator. """

        return settings.HEALTH_ENDPOINT_VERSION

    def is_storage_ok(self, obj: dict) -> bool:
        """ Writes and deletes a file. Adapted from:
        https://github.com/KristianOellegaard/django-health-check/blob/master/health_check/storage/backends.py
        """

        key = 'is_storage_ok'
        value = cache.get(key)
        if value:
            return value

        filename = f'health_check_storage_test/test-{uuid.uuid4()}.txt'
        file_content = b'this is the healthtest file content'
        storage = get_storage_class()()  # needs double parentheses

        temp_file = NamedTemporaryFile(delete=True)
        temp_file.write(file_content)
        filename = storage.save(name=filename, content=temp_file)

        # read the file and compare
        if not storage.exists(filename):
            cache.set(key, False, 15 * 60)
            return False
        with storage.open(filename) as f:
            if not f.read() == file_content:
                cache.set(key, False, 15 * 60)
                return False

        # delete the file and make sure it is gone
        storage.delete(filename)
        if storage.exists(filename):
            cache.set(key, False, 15 * 60)
            return False
        cache.set(key, True, 15 * 60)
        return True

    def is_postgres_ok(self, obj: dict) -> bool:
        """ Checks to ensure that postgres is up and running """

        try:
            User.objects.first()
            return True
        except Exception:
            return False

    # def is_elasticsearch_ok(self) -> bool:
    #     """ Checks health of elasticsearch service '""
    #     from elasticsearch import Elasticsearch
    #     es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    #     try:
    #         health_status = es.cat.health()
    #         if health_status.find('red') != -1:
    #             return False
    #         return True
    #     except Exception:
    #         return False
