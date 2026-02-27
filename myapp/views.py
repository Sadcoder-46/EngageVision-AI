from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EngagementRecordForm



def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def register_view(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account Created Successfully")
            return redirect('login')
    return render(request, 'register.html', {'form': form})

def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('dashboard')
                else:
                    return redirect('userpage')
            else:
                messages.error(request, "Invalid Credentials")

    return render(request, 'login.html', {'form': form})

@login_required
def userpage(request):
    return render(request, 'userpage.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('userpage')
    user_count = User.objects.count()
    return render(request, 'dashboard.html', {'user_count': user_count})

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def about(request):
    return render(request, 'about.html')

@login_required
def contact(request):
    return render(request, 'contact.html')
@login_required
def add_engagement(request):
    if request.method == 'POST':
        form = EngagementRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.student = request.user
            record.save()
            return redirect('dashboard')
    else:
        form = EngagementRecordForm()

    return render(request, 'add_engagement.html', {'form': form})
@login_required
def dashboard(request):
    records = request.user.engagementrecord_set.all()
    return render(request, 'dashboard.html', {'records': records})      