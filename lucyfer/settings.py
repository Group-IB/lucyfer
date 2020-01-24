from django.conf import settings
from django.test.signals import setting_changed


LUCYFER_SETTINGS_NAME = "LUCYFER_SETTINGS"


DEFAULTS = {
    "SAVED_SEARCHES_ENABLE": False,
    "SAVED_SEARCHES_KEY": None,
    "CACHE_SEARCH_VALUES": True,
    "CACHE_TIME": 6000,  # one hour
    "CACHE_MAX_VALUES_COUNT_FOR_ONE_PREFIX": 10,
    "CACHE_VALUES_MIN_LENGTH": 3,
}


class LucyferSettings:
    def __init__(self, user_settings=None, defaults=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, LUCYFER_SETTINGS_NAME, {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f"Invalid setting: {attr}")

        try:
            val = self.user_settings[attr]
        except KeyError:
            val = self.defaults[attr]

        return val

    def reload(self):
        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


lucyfer_settings = LucyferSettings(None, DEFAULTS)


def reload_lucyfer_settings(*args, **kwargs):
    if kwargs['setting'] == LUCYFER_SETTINGS_NAME:
        lucyfer_settings.reload()


setting_changed.connect(reload_lucyfer_settings)
