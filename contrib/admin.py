from django.contrib import admin

from solo.admin import SingletonModelAdmin

from . import models


@admin.register(models.PrivateGlobalSettings)
class PrivateGlobalSettingsAdmin(SingletonModelAdmin):
    pass


@admin.register(models.PublicGlobalSettings)
class PublicGlobalSettingsAdmin(SingletonModelAdmin):
    pass
