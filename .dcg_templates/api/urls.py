{% load code_generator_tags %}
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
{% for model in models %}
router.register(
    '{{ model.snake_case_name }}',
    views.{{ model.name }}ViewSet,
    basename='{{ model.name.lower }}'
)
{% endfor %}