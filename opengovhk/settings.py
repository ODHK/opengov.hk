# -*- coding: utf-8 -*-
import os, re
from configurations import Configuration, importer, values
from froide.settings import ThemeBase, Base # noqa

# importer.install(check_options=True)

class OpenGovHK(ThemeBase, Base):
    FROIDE_THEME = 'opengovhk.theme'

    LANGUAGES = (
        ('en', 'English'),
        ('zh-hk', '繁體中文'),
        ('zh-cn', '简体中文'),
    )

    ROOT_URLCONF = 'froide.urls'

    SITE_NAME = "OpenGov.HK"
    SITE_EMAIL = "foi@opendatahk.com"
    SITE_URL = 'http://localhost:8000'

    SECRET_URLS = {
        "admin": "admin",
    }

    @property
    def LOCALE_PATHS(self):
        return list(super(OpenGovHK, self).LOCALE_PATHS.default) + [
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', "locale")
        )
    ]

    @property
    def INSTALLED_APPS(self):
        installed = super(OpenGovHK, self).INSTALLED_APPS
        # installed += [
        #     # 'foiidea',
        #     # 'celery_haystack',
        #     # 'djcelery_email',
        #     # 'djangosecure',
        #     # 'django.contrib.redirects',
        #     # 'django.contrib.flatpages'
        # ]
        return installed

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        }
    }

class Dev(OpenGovHK):

    rec = re.compile

    FROIDE_CONFIG = dict(
        create_new_publicbody=True,
        publicbody_empty=True,
        user_can_hide_web=True,
        public_body_officials_public=True,
        public_body_officials_email_public=False,
        request_public_after_due_days=14,
        payment_possible=True,
        currency="Euro",
        default_law=1,
        search_engine_query="http://www.google.de/search?as_q=%(query)s&as_epq=&as_oq=&as_eq=&hl=en&lr=&cr=&as_ft=i&as_filetype=&as_qdr=all&as_occt=any&as_dt=i&as_sitesearch=%(domain)s&as_rights=&safe=images",
        greetings=[rec(u"Dear (?:Mr\.?|Ms\.? .*?)")],
        closings=[rec(u"Sincerely yours,?")],
        public_body_boosts={},
        dryrun=True,
        dryrun_domain="opengov.hk",
        allow_pseudonym=False,
        doc_conversion_binary=None,  # replace with libreoffice instance
        doc_conversion_call_func=None  # see settings_test for use
    )


class Production(OpenGovHK):
    DEBUG = True
    TEMPLATE_DEBUG = True
    ALLOWED_HOSTS = ['opengov.hk']
    ALLOWED_HOSTS = ['*'] # temp flexibility

    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
    STATICFILES_DIRS = (
        os.path.join(PROJECT_PATH, 'static'),
    )

    STATIC_URL = '/static/'   

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__name__))
    STATIC_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, 'static'))
    
    CELERY_ALWAYS_EAGER = False
    COMPRESS_ENABLED = False
    COMPRESS_OFFLINE = False

    rec = re.compile

    FROIDE_CONFIG = dict(
        create_new_publicbody=True,
        publicbody_empty=True,
        user_can_hide_web=True,
        public_body_officials_public=True,
        public_body_officials_email_public=False,
        request_public_after_due_days=14,
        payment_possible=True,
        currency="Euro",
        default_law=1,
        search_engine_query="http://www.google.de/search?as_q=%(query)s&as_epq=&as_oq=&as_eq=&hl=en&lr=&cr=&as_ft=i&as_filetype=&as_qdr=all&as_occt=any&as_dt=i&as_sitesearch=%(domain)s&as_rights=&safe=images",
        greetings=[rec(u"Dear (?:Mr\.?|Ms\.? .*?)")],
        closings=[rec(u"Sincerely yours,?")],
        public_body_boosts={},
        dryrun=True,
        dryrun_domain="opengov.hk",
        allow_pseudonym=False,
        doc_conversion_binary=None,  # replace with libreoffice instance
        doc_conversion_call_func=None  # see settings_test for use
    )

try:
    from .local_settings import *  # noqa
except ImportError:
    pass
