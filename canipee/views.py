from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from forms import MyRegistrationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext

def register(request):
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            login(request, user)
            return redirect("profile")
    else:
        form = MyRegistrationForm()
    return render(request, "registration/register.html", 
        {'form': form})

@login_required
def profile(request):
    return render(request, "accounts/profile.html")