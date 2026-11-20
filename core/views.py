from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from .forms import LoginForm, SignUpForm, ProfileForm
from questions.models import Profile


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                next_url = request.GET.get('next', '')
                if next_url and url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts=settings.ALLOWED_HOSTS,
                    require_https=request.is_secure()
                ):
                    return redirect(next_url)

                return redirect('index')
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data.get('first_name', '')
            )

            Profile.objects.create(user=user)

            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()

    return render(request, 'core/signup.html', {'form': form})


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def profile(request):
    profile_obj = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile_obj, user=request.user)

    return render(request, 'core/profile.html', {'form': form})


def logout_view(request):
    logout(request)
    next_url = request.GET.get('next', '')
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts=settings.ALLOWED_HOSTS,
        require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect(request.META.get('HTTP_REFERER', 'index'))