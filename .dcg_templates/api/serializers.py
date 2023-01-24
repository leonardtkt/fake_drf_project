{% load code_generator_tags %}from rest_framework.serializers import ModelSerializer

from . import models
{% for model in models %}


class {{ model.name }}Serializer(ModelSerializer):
    """ Main serializer interface for {{ model.name }}. """

    class Meta:
        model = models.{{ model.name }}
        depth = 1
        fields = (
            {% indent_items model.field_names 12 quote='simple' %}
        )
        read_only_fields = ('id',){% comment %}
{% endcomment %}{% endfor %}
