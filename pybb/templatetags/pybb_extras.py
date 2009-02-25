from datetime import datetime, timedelta

from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.utils.encoding import smart_unicode
from django.db import settings
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.utils import dateformat

from pybb.models import Forum, Topic, Read, PrivateMessage
from pybb.unread import cache_unreads
from pybb import settings as pybb_settings

register = template.Library()

@register.filter
def pybb_profile_link(user):
    data = u'<a href="%s">%s</a>' % (\
        reverse('pybb_profile', args=[user.username]), user.username)
    return mark_safe(data)


@register.tag
def pybb_time(parser, token):
    try:
        tag, time = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('pybb_time requires single argument')
    else:
        return PybbTimeNode(time)


class PybbTimeNode(template.Node):
    def __init__(self, time):
        self.time = template.Variable(time)

    def render(self, context):
        time = self.time.resolve(context)

        delta = datetime.now() - time
        today = datetime.now().replace(hour=0, minute=0, second=0)
        yesterday = today - timedelta(days=1)

        if delta.days == 0:
            if delta.seconds < 60:
                if context['LANGUAGE_CODE'].startswith('ru'):
                    msg = _('seconds ago,seconds ago,seconds ago')
                    import pytils
                    msg = pytils.numeral.choose_plural(delta.seconds, msg)
                else:
                    msg = _('seconds ago')
                return u'%d %s' % (delta.seconds, msg)

            elif delta.seconds < 3600:
                minutes = int(delta.seconds / 60)
                if context['LANGUAGE_CODE'].startswith('ru'):
                    msg = _('minutes ago,minutes ago,minutes ago')
                    import pytils
                    msg = pytils.numeral.choose_plural(minutes, msg)
                else:
                    msg = _('minutes ago')
                return u'%d %s' % (minutes, msg)
        if time > today:
            return _('today, %s') % time.strftime('%H:%M')
        elif time > yesterday:
            return _('yesterday, %s') % time.strftime('%H:%M')
        else:
            return dateformat.format(time, 'd M, Y H:i')


@register.inclusion_tag('pybb/pagination.html',takes_context=True)
def pybb_pagination(context, label):
    page = context['page']
    paginator = context['paginator']
    return {'page': page,
            'paginator': paginator,
            'label': label,
            }


@register.simple_tag
def pybb_link(object, anchor=u''):
    """
    Return A tag with link to object.
    """

    url = hasattr(object,'get_absolute_url') and object.get_absolute_url() or None   
    anchor = anchor or smart_unicode(object)
    return mark_safe('<a href="%s">%s</a>' % (url, escape(anchor)))


@register.filter
def pybb_has_unreads(topic, user):
    """
    Check if topic has messages which user didn't read.
    """

    now = datetime.now()
    delta = timedelta(seconds=pybb_settings.READ_TIMEOUT)
    
    def _is_topic_read(topic,user):
        if (now - delta > topic.updated):
            return True 
        else:
            if hasattr(topic, '_read'):
                print "hasattr:"
                read = topic._read
            else:
                print "Trying!"
                try:
                    read = Read.objects.get(user=user, topic=topic)
                    print "read:", read

                except Read.DoesNotExist:
                    read = None

            if read is None:
                return False
            else:
                return topic.updated < read.time

    if not user.is_authenticated():
        return False
    else:
        if isinstance(topic, Topic):
            return not _is_topic_read(topic,user)
        if isinstance(topic,Forum):
            forum = topic
            for t in forum.topics.all():
                print "type(t),type(user):", type(t),type(user)
                print "t,user:", t,user

                rv = _is_topic_read(t,user)
                print "t,rv:", t,rv

                if rv == False:
                    return True
            return False
        else:
            raise Exception('Object should be a topic')


@register.filter
def pybb_setting(name):
    return mark_safe(getattr(pybb_settings, name, 'NOT DEFINED'))


@register.filter
def pybb_moderated_by(topic, user):
    """
    Check if user is moderator of topic's forum.
    """

    return user.is_superuser or user in topic.forum.moderators.all()


@register.filter
def pybb_editable_by(post, user):
    """
    Check if the post could be edited by the user.
    """

    if user.is_superuser:
        return True
    if post.user == user:
        return True
    if user in post.topic.forum.moderators.all():
        return True
    return False


@register.filter
def pybb_posted_by(post, user):
    """
    Check if the post is writed by the user.
    """

    return post.user == user


@register.filter
def pybb_equal_to(obj1, obj2):
    """
    Check if objects are equal.
    """

    return obj1 == obj2


@register.filter
def pybb_unreads(qs, user):
    return cache_unreads(qs, user)
