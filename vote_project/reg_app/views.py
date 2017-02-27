from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


def register(request):
    if request.method == 'POST':
        user_form = UserCreationForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()

            make_staff = User.objects.get(username=user_form.cleaned_data['username'])
            make_staff.is_staff=True
            make_staff.save()

            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect("/polls")
        else:
            print (user_form.errors)
    else:
        user_form = UserCreationForm()

    return render(request, 'register.html', {'user_form': user_form})