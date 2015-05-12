from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TrainingPortal.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/', 'django.contrib.auth.views.logout',{
        'next_page': '/',
    }),
    url(r'^$', 'review.user.home'),
    url(r'^review/$', 'review.views.index'),
    url(r'^review/save/surface_text/(?P<entity>.*)$', 'review.views.save_surface_text'),
    url(r'^review/save/(?P<entity>.*)$', 'review.views.save'),
    url(r'^review/skip', 'review.views.skip'),
   # url(r'^progress-stat/$', 'review.user.progress'),
    url(r'^review/(?P<resource>.*)$', 'review.views.index'),
    url(r'^progress', 'review.progress.progress'),
    url(r'^report/download', 'review.download.download'),
    url(r'^report/(?P<id>[-\d]+)/download/$', 'review.download.user_report_download'),
    url(r'^search/', 'review.search.search'),
    url(r'^entity/details/(?P<query_string>.*)/(?P<entity_id>.*)$', 'review.views.get_details_by_id'),
    url(r'^bot-training/$', 'review.bot.start_training'),
    url(r'^review/delete/(?P<id>[-\d]+)$', 'review.views.delete'),
    url(r'^generate-results/$', 'review.user.retrain'),
    url(r'^generate-results/progress', 'review.user.check_retraining_progress'),
    url(r'^No-Tags/$', 'review.no_tag.display_no_tag'),
    url(r'^no-tags/$', 'review.no_tag.get_associated_entities'),
    url(r'^no-tags/associate/$', 'review.no_tag.associate_entity'),
    url(r'^upload/$', 'review.upload.upload'),
    url(r'^mass-training/$', 'review.download.mass_training'),
    url(r'^cuisine_selection/$', 'review.cuisine.select_cuisine'),
    url(r'^generate-questions/$', 'review.cuisine.generate_questions'),
    url(r'^generate-questions/progress', 'review.cuisine.check_question_gen_progress'),
    url(r'^bot/$', 'bot.views.bot'),
    url(r'^bot/step/(?P<process>[-\w]+)$', 'bot.views.bot'),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# urlpatterns = patterns('',
#     (r'^', include('TrainingPortal.urls')),
# ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
