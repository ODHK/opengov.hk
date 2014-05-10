# -*- coding: utf-8 -*-
import os

from froide.settings import Base, ThemeBase, HerokuPostmark, HerokuPostmarkS3  # noqa


class CustomThemeBase(ThemeBase):
    FROIDE_THEME = 'froide_theme.theme'

    SITE_NAME = "My Froide"
    SITE_EMAIL = "info@example.com"
    SITE_URL = 'http://localhost:8000'

    SECRET_URLS = {
        "admin": "admin",
    }

    @property
    def LOCALE_PATHS(self):
        return list(super(CustomThemeBase, self).LOCALE_PATHS.default) + [
            os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', "locale")
            )
        ]


class Dev(CustomThemeBase, Base):
    pass


class ThemeHerokuPostmark(CustomThemeBase, HerokuPostmark):
    pass


class ThemeHerokuPostmarkS3(CustomThemeBase, HerokuPostmarkS3):
    pass


try:
    from .local_settings import *  # noqa
except ImportError:
    pass
