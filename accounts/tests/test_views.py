from django.test import TestCase
from django .contrib.auth import get_user_model
from unittest.mock import patch, call
from accounts.models import Token
from accounts.authentication import PasswordlessAuthenticationBackend
User = get_user_model()

class SendLoginEmailViewTest(TestCase):

    def test_redirects_to_home_page(self):
        response = self.client.post('/accounts/send_login_email',
                                    data={
                                        'email': 'edith@example.com'
                                    })
        self.assertRedirects(response, '/')

    @patch('accounts.views.send_mail')
    def test_sends_mail_to_address_from_post(self, mock_send_mail):
        self.client.post(
            '/accounts/send_login_email',
            data={'email': 'edith@example.com'
                  }
        )
        self.assertEqual(mock_send_mail.called, True)
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertEqual(subject, 'Your login link for Superlists')
        self.assertEqual(from_email, 'noreply@superlists')
        self.assertEqual(to_list, ['edith@example.com'])

    @patch('accounts.views.messages')
    def test_adds_success_message_with_mocks(self, mock_messages):
        response = self.client.post(
            '/accounts/send_login_email',
            data={'email': 'edith@example.com'}
        )
        expected = 'Check your email, we have sent you a link you can use to log in'
        self.assertEqual(
            mock_messages.success.call_args,
            call(response.wsgi_request, expected),
        )


class LoginViewTest(TestCase):

    def test_redirects_to_home_page(self):
        response = self.client.get('/accounts/login?token=abcd123')
        self.assertRedirects(response, '/')

    def test_creates_token_associated_with_email(self):
        self.client.post('/accounts/send_login_email',
                         data={'email': 'edith@example.com'})
        token = Token.objects.first()
        self.assertEqual(token.email, 'edith@example.com')

    @patch('accounts.views.send_mail')
    def test_sends_link_to_login_using_token_uid(self, mock_send_mail):
        self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        })
        token = Token.objects.first()
        expected_url = f'http://testserver/accounts/login?token={token.uid}'
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertIn(expected_url, body)

class AuthenticateTest(TestCase):

    def test_returns_None_if_no_such_token(self):
        result = PasswordlessAuthenticationBackend().authenticate(
            'no-such-token'
        )
        self.assertIsNone(result)

    def test_returns_new_user_with_correct_email_if_token_exists(self):
        email = 'edith@example.com'
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(token.uid)
        new_user = User.objects.get(email=email)
        self.assertEqual(user, new_user)

    def test_returns_existing_user_with_correct_email_if_token_exists(self):
        email = 'edith@example.com'
        existing_user = User.objects.create(email=email)
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(token.uid)
        self.assertEqual(user, existing_user)