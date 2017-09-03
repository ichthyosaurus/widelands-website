# Create your views here.


from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext

from forms import SearchForm

from wiki.models import Article
from pybb.models import Post, Topic
from news.models import Post as NewsPost
from wlhelp.models import Building, Ware
from wlmaps.models import Map

class DummyEmptyQueryset(object):
    """A simple dummy class when a search should not be run.

    The template expects a queryset and checks for the count member.

    """

    def count(self):
        return 0


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)

        if form.is_valid():
            query = form.cleaned_data['search']
            do_wiki = form.cleaned_data['incl_wiki']
            do_forum = form.cleaned_data['incl_forum']
            do_news = form.cleaned_data['incl_news']
            do_help = form.cleaned_data['incl_help']
            do_maps = form.cleaned_data['incl_maps']

            # Help
            wlhelp_wares = Ware.search.query(
                query) if do_help else DummyEmptyQueryset()
            wlhelp_buildings = Building.search.query(
                query) if do_help else DummyEmptyQueryset()

            # Maps
            map_results = Map.search.query(
                query) if do_maps else DummyEmptyQueryset()

            # Wiki
            wiki_results = Article.search.query(
                query) if do_wiki else DummyEmptyQueryset()

            # Forum
            forum_results_topic = Topic.search.query(
                query) if do_forum else DummyEmptyQueryset()
            forum_results_post = Post.search.query(
                query) if do_forum else DummyEmptyQueryset()

            # News
            news_results = NewsPost.search.query(
                query) if do_news else DummyEmptyQueryset()

            template_params = {
                'wiki_results': wiki_results,

                'wlhelp_hits': wlhelp_wares.count() + wlhelp_buildings.count(),
                'wlhelp_results_wares': wlhelp_wares,
                'wlhelp_results_buildings': wlhelp_buildings,

                'forum_hits': forum_results_post.count() + forum_results_topic.count(),
                'forum_results_topic': forum_results_topic,
                'forum_results_post': forum_results_post,

                'map_results': map_results,

                'news_results': news_results,

                'search_form': form,
                'post': True,
            }

            return render_to_response('wlsearch/search.html',
                                      template_params,
                                      context_instance=RequestContext(request))
    else:
        form = SearchForm()

    template_params = {
        'search_form': form,
        'post': False,
    }
    return render_to_response('wlsearch/search.html',
                              template_params,
                              context_instance=RequestContext(request))


from haystack.generic_views import SearchView
from haystack.forms import ModelSearchForm as HaystackForm
from forms import WlSearchForm
from haystack.query import EmptySearchQuerySet, SearchQuerySet
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from datetime import date, timedelta

class HaystackSearchView(SearchView):
    """My custom search view."""
    template_name = 'search/search_test.html'
    form_class = WlSearchForm
    paginate_by = None

    def post(self, request, *args, **kwargs):
        """ This is executed when searching through the box in the navigation
        
        We build the query string and redirect it to this view again.
    
        """
        form = self.form_class(request.POST)
        if form.is_valid() and form.cleaned_data['q'] != '':
            print('franku cleaned_data: ', form.cleaned_data)
            search_url = 'q=%s' % (form.cleaned_data['q'])
            # Search only the last two years from today
            search_url += '&start_date=%s' % (date.today() - timedelta(365*2))

            for model in form.cleaned_data['models']:
                search_url += '&models=%s' % (model)
            return HttpResponseRedirect('%s?%s' % (reverse('search'), search_url))
        return render(request, self.template_name, {'form': form})

    def get_context_data(self, *args, **kwargs):
        """ Regrouping the search results """
    
        context = super(HaystackSearchView, self).get_context_data(*args, **kwargs)
        #print('franku context kwargs: ', args, kwargs)
        # for k,v in context.iteritems():
        #     print('franku context data: ', k, " : ", v)
        # print('franku object_list: ', context['object_list'])
        if context['object_list'] != EmptySearchQuerySet:
            maps = []
            topics = []
            posts = []
            workers = []
            for item in context['object_list']:
                #print('franku item: ', item)
                if item.content_type() == 'wlmaps.map':
                    maps.append(item)
                if item.content_type() == "pybb.post":
                    posts.append(item)
                if item.content_type() == "pybb.topic":
                    topics.append(item)
                if item.content_type() == "wlhelp.worker":
                    workers.append(item)
            
            sorted_objects = [
                {'maps': maps},
                {'topics': topics},
                {'posts': posts},
                {'workers': workers},
            ]
            context['object_list'] = sorted_objects
        
        return context
