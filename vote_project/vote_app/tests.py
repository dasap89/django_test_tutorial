import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.test import Client

from .models import Question, Choice, Answer


def create_question(question_text, days):
    """
    Creates a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question, choice_text ):
    """
    Creates a choice for question.
    """
    return Choice.objects.create(question=question, choice_text=choice_text)

def create_user(username, password=None):
    """
    Creates a new user
    """
    return User.objects.create_user(username, password)

class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('vote_app:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the
        index page.
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('vote_app:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('vote_app:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        should be displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('vote_app:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('vote_app:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question with a pub_date in the future should
        return a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('vote_app:detail', args=(future_question.id,))
        
        response = self.client.get(reverse('reg_app:register'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('reg_app:register'),
            {'username': "admin", 'password1': "adminadmin", 'password2': "adminadmin"}
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question with a pub_date in the past should
        display the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('vote_app:detail', args=(past_question.id,))

        response = self.client.get(reverse('reg_app:register'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('reg_app:register'),
            {'username': "admin", 'password1': "adminadmin", 'password2': "adminadmin"}
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class CreateUserTests(TestCase):
    def test_create_new_user_with_reg_form(self):
        """
        Register form should create user with is_staff = True and redirect to main page.
        """
        response = self.client.get(reverse('reg_app:register'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('reg_app:register'),
            {'username': "admin", 'password1': "adminadmin", 'password2': "adminadmin"}
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="admin")
        self.assertEqual(user.username, "admin")
        self.assertTrue(user.is_staff)

class AnswerTests(TestCase):
    def test_user_makes_answer(self):
        # create question
        question = create_question(question_text="Past question 1.", days=-5)

        # create choices
        choice = create_choice(question, "Choice 1" )
        create_choice(question, "Choice 2" )

        # create user and log in
        response = self.client.get(reverse('reg_app:register'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('reg_app:register'),
            {'username': "admin", 'password1': "adminadmin", 'password2': "adminadmin"}
        )
        self.assertEqual(response.status_code, 302)

        # get page with question
        response = self.client.get(reverse('vote_app:vote', args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        # vote

        response = self.client.post(
            reverse('vote_app:vote', args=(question.id,)),
            {"choice": choice.id}
        )
        self.assertEqual(response.status_code, 302)
        # check amount of answers
        answer_count = Answer.objects.filter(choice=choice).count()
        self.assertEqual(answer_count, 1)

    def test_user_makes_just_one_answer(self):
        # create question
        question = create_question(question_text="Past question 1.", days=-5)

        # create choices
        choice = create_choice(question, "Choice 1" )
        create_choice(question, "Choice 2" )

        # create user and log in
        response = self.client.get(reverse('reg_app:register'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('reg_app:register'),
            {'username': "admin", 'password1': "adminadmin", 'password2': "adminadmin"}
        )
        self.assertEqual(response.status_code, 302)

        # get page with question
        response = self.client.get(reverse('vote_app:vote', args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        # vote

        response = self.client.post(
            reverse('vote_app:vote', args=(question.id,)),
            {"choice": choice.id}
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse('vote_app:vote', args=(question.id,)),
            {"choice": choice.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already voted")

        # check amount of answers, it should be 1
        answer_count = Answer.objects.filter(choice=choice).count()
        self.assertEqual(answer_count, 1)

    def test_get_list_of_users(self):
        response = self.client.get(reverse('vote_app:answers'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There were no users found.")
        
        # create user admin
        create_user("admin", "adminadmin")

        # get page with admin user
        response = self.client.get(reverse('vote_app:answers'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "admin")
