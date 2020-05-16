import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question, Choice


class QuestionModelTests(TestCase):

############################### UnitTests ###################################

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than one day.
        """
        time = timezone.now() - datetime.timedelta(days = 1, seconds = 1)
        question = Question("old question", pub_date = time)

        actual = question.was_published_recently()
        self.assertIs(False, actual)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is recent.
        """
        time = timezone.now() - datetime.timedelta(days = 1)
        question = Question(pub_date = time)

        self.assertIs(True, question.was_published_recently())

    def test_was_published_recently_with_now_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is recent.
        """
        time = timezone.now()
        question = Question(pub_date = time)

        self.assertIs(True, question.was_published_recently())



############################ IntegrationTests ###############################

#- - - - - - - - - - - - - - Helper functions - - - - - - - - - - - - - - - #

def create_question(question_text, days):
    """ Shortcut function to create questions given a text and time """
    time = timezone.now() + timezone.timedelta(days = days)
    return Question.objects.create(question_text=question_text, pub_date = time)

#- - - - - - - - - - - - - - - - - Index View - - - - - - - - - - - - - - - #

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "No polls are available")

    def test_past_question(self):
        question = create_question("past question", -1)
        question.choice_set.create(choice_text = "Choice 1")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: past question>']
        )
    def test_future_question(self):
        question = create_question("future question", 1)
        question.choice_set.create(choice_text = "Choice 1")
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            []
        )

    def future_question_and_past_question(self):
        question1 = create_question("past question", -1)
        question1.choice_set.create(choice_text = "Choice 1")
        question2 = create_question("future question", 1)
        question2.choice_set.create(choice_text = "Choice 1")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: past question>']
        )

    def test_multiple_past_questions(self):
        question1 = create_question("past question 1", -30)
        question1.choice_set.create(choice_text = "Choice 1")
        question2 = create_question("past question 2", -20)
        question2.choice_set.create(choice_text = "Choice 1")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: past question 2>', '<Question: past question 1>']
        )

    def test_question_with_no_choices_is_not_displayed(self):
        question = create_question("Question without choices", -1)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_question_with_choices_is_displayed(self):
        question = create_question("Question with choices", -1)
        question.choice_set.create(choice_text = "Choice 1")
        question.choice_set.create(choice_text = "Choice 2")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                ['<Question: Question with choices>'])

#- - - - - - - - - - - - - - - - Detail View - - -  - - - - - - - - - - - - - #

class QuestionDetailViewTest(TestCase):
    def test_future_question(self):
        question = create_question("future question", 1)
        response = self.client.get(reverse('polls:detail', args = (question.id,)))
        self.assertEquals(response.status_code, 404)

    def test_past_questions(self):
        question = create_question("past question", -1)
        response = self.client.get(reverse('polls:detail', args = (question.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, question.question_text)


#- - - - - - - - - - - - - - - - Results View - - - - - - - - - - - - - - - - #

class QuestionResultViewTest(TestCase):
    def test_future_question(self):
        question = create_question("future question", 1)
        response = self.client.get(reverse('polls:results', args = (question.id,)))
        self.assertEquals(response.status_code, 404)

    def test_past_questions(self):
        question = create_question("past question", -1)
        response = self.client.get(reverse('polls:results', args = (question.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, question.question_text)
