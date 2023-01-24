{% load code_generator_tags %}from django.contrib import admin

from . import models{% for model in models %}


@admin.register(models.{{ model.name }})
class {{ model.name }}Admin(admin.ModelAdmin):
    """ Back office interface for {{ model.name }} model. """

    list_display = (
        {% indent_items model.filter_field_names 8 quote='simple' %}
    )
    search_fields = (
        {% indent_items model.char_field_names 8 quote='simple' %}
    )
{% if model.foreign_field_names %}  autocomplete_fields = (
        {% indent_items model.foreign_field_names 8 quote='simple' %}
    ){% endif %}
    fieldsets = [
        [None, {
            'fields': [
                {% indent_items model.char_field_names 8 quote='simple' %}
            ]
        }]
    ]{% endfor %}
