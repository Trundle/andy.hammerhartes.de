# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Andy'
SITENAME = u'Superficial Reflections'
SITEURL = 'https://andy.hammerhartes.de'
#SITEURL = ''

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'de'

THEME = 'mytheme'

# Feed generation is usually not desired when developing
FEED_DOMAIN = '//andy.hammerhartes.de'
FEED_ALL_ATOM = 'atom.xml'
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = []

# Social widget
SOCIAL = []

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# Plugins
PLUGIN_PATHS = ["plugins"]
PLUGINS = ["blockquote_fixer"]

# XXX TODO
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'weekly',
        'indexes': 'weekly',
        'pages': 'weekly'
    }
}
