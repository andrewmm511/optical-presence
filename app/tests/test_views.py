import json

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from app.models import Person
from app.views import register_people


class RegisterPeopleTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_register_people_success(self):
        request = self.factory.post(reverse('register_people'), {'name': 'Test Person'}, content_type='application/json')
        request.user = self.user

        response = register_people(request)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')

        person_id = response_data['person_id']
        person = Person.objects.get(id=person_id)
        self.assertIsNotNone(person)
        self.assertEqual(person.name, 'Test Person')
        self.assertEqual(person.user, self.user)

    def test_register_people_missing_name(self):
        request = self.factory.post(reverse('register_people'), {}, content_type='application/json')
        request.user = self.user

        response = register_people(request)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('message', response_data)
