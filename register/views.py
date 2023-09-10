from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.views import LoginView, LogoutView
# Create your views here.


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login')
        return render(request, 'register/register.html', {'form': form})
    else:
        form = RegisterForm()
    return render(request, 'register/register.html', {'form': form})

