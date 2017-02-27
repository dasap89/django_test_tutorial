from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Choice, Question, Answer


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

@login_required(login_url="/reg/login/")
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()

        user = get_object_or_404(User, username=request.user)
        answer = Answer(user = user, question = question, choice = selected_choice)
        answer.save()

        return HttpResponseRedirect(reverse('vote_app:results', args=(question.id,)))


class AnswerUserView(generic.ListView):
    template_name = 'polls/answers.html'
    context_object_name = 'list_of_answers'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return User.objects.all()


def answer_per_user(request, id):
    answer_per_user = Answer.objects.filter(user=id)
    return render(request, 'polls/answer_per_user.html', {
            'answer_per_user': answer_per_user,
        })

    # def get_queryset(self):
        #"""
        #Excludes any questions that aren't published yet.
        #"""
        # return Answer.objects.filter(user=request.GET['id'])
        # return User.answer_set.get(id=request.GET['id'])
        # question.choice_set.filter(pk=request.POST['choice'])
