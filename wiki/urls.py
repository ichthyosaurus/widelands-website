# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.http import HttpResponseRedirect
from wiki import views, models
from wiki.templatetags.wiki import WIKI_URL_RE
from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
    # I wanted a true reverse, but it didn't work out 
    url(r'^$', redirect_to, { "url": "/wiki/MainPage" }, name="wiki_index" ),

    url(r'^preview/$', views.article_preview, name='wiki_preview'),
    url(r'^diff/$', views.article_diff, name='wiki_preview_diff'),

    url(r'^list/$', views.article_list, name='wiki_list'),

    url(r'^history/$', views.history, name='wiki_history'),

    url(r'^feeds/(?P<feedtype>\w+)/$', views.history_feed, name='wiki_history_feed'),

    url(r'^(?P<title>'+ WIKI_URL_RE +r')/feeds/(?P<feedtype>\w+)/$', views.article_history_feed,
        name='wiki_article_history_feed'),

    url(r'^(?P<title>'+ WIKI_URL_RE +r')/$', views.view_article, name='wiki_article'),

    url(r'^edit/(?P<title>'+ WIKI_URL_RE +r')/$', views.edit_article, name='wiki_edit'),

    url(r'observe/(?P<title>'+ WIKI_URL_RE +r')/$', views.observe_article, name='wiki_observe'),

    url(r'observe/(?P<title>'+ WIKI_URL_RE +r')/stop/$', views.stop_observing_article,
        name='wiki_stop_observing'),

    url(r'^history/(?P<title>'+ WIKI_URL_RE +r')/$', views.article_history, name='wiki_article_history'),

    url(r'^history/(?P<title>'+ WIKI_URL_RE +r')/changeset/(?P<revision>\d+)/$', views.view_changeset,
        name='wiki_changeset',),

    url(r'^history/(?P<title>'+ WIKI_URL_RE +r')/revert/$', views.revert_to_revision,
        name='wiki_revert_to_revision'),

    # Redirects
    url(r'^ChangeLog', redirect_to, { "url": "/changelog", "permanent": True }, name="wiki_changelog" ),
)
