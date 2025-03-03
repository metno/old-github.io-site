#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Webmaster'
SITENAME = u'IT.met.no'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Oslo'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('MET Norway', 'http://met.no/English'),
         ('yr.no', 'http://yr.no'),
	)

# Menu
MENUITEMS = (
    ('home', '/index.html'),
    ('about', '/pages/about.html'),
    ('howto', '/pages/howto.html'),
    ('|', '#'),
)

# Social widget
#SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

CHECK_MODIFIED_METHOD="md5"
THEME = "pelican-fresh"

DISPLAY_PAGES_ON_MENU=False
DISPLAY_CATEGORIES_ON_MENU=True

YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/index.html'
ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{slug}.html'
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{slug}.html'
SITESUBTITLE = u''
SUMMARY_MAX_LENGTH = 150
READERS = {'html': None}
TEMPLATE_PAGES = {
    'CNAME': 'CNAME'
}
TAG_CLOUD_MAX_ITEMS=100
TAG_CLOUD_STEPS=4

STATIC_PATHS = ['images', 'files']

