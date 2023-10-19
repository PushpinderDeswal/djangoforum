from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UpdateProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Your account has been created! You are now able to log in"
            )
            return redirect("users:login")
        else:
            return render(
                request, "users/register.html", {"errors": form.errors, "form": form}
            )

    form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request):
    return render(request, "users/profile.html")


@login_required
def update_profile(request):
    if request.method == "POST":
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("users:profile")
    else:
        form = UpdateProfileForm(instance=request.user)

    return render(request, "users/update_profile.html", {"form": form})


@login_required
def update_password(request):
    if request.method == "POST":
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(
                request, user
            )  # Important for keeping the user logged in
            messages.success(request, "Your password has been updated successfully!")
            return redirect("users:profile")
    else:
        password_form = PasswordChangeForm(request.user)

    context = {
        "form": password_form,
    }
    return render(request, "users/update_password.html", context)
