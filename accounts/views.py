from django.shortcuts import render

# Create your views here.
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib import messages

def send_login_email(request):
    email = request.POST['email']
    send_mail(
        'Your login link for Superlists',
        'body text tbc',
        'noreply@superlists',
        [email]
    )
    # send_mail(
    #     'Your login link for Superlists',
    #     'body text tbc',
    #     'noreply@superlists',
    #     [email],
    # )
    messages.success(
        request,
        'Check your email, we have sent you a link you can use to log in'
    )
    return redirect('/')
