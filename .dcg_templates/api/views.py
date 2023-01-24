{% load code_generator_tags %}from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from . import models
from . import serializers{% comment %}
{% endcomment %}{% for model in models %}


class {{ model.name }}ViewSet(viewsets.ModelViewSet):
    """ Full CRUD endpoint for {{ model.name }} model. """

    permission_classes = [IsAuthenticated]
    queryset = models.{{ model.name }}.objects.all()
    serializer_class = serializers.{{ model.name }}Serializer
    search_fields = (
        {% indent_items model.string_field_names 8 quote='simple' %}
    )
    filter_fields = (
        {% indent_items model.filter_field_names 8 quote='simple' %}
    )
    ordering_fields = (
        {% indent_items model.concrete_field_names 8 quote='simple' %}
    ){% comment %}
{% endcomment %}{% endfor %}
