from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'vote_app'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', login_required(views.DetailView.as_view(), login_url="/reg/login/"), name='detail'),
    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^answers/$', views.AnswerUserView.as_view(), name='answers'),
    url(r'^answers/(?P<id>[0-9]+)/$', views.answer_per_user, name='answer_per_user'),
]
