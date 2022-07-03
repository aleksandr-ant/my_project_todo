from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from todo.forms import TodoTasksForm
from todo.models import Todo


def home(request):
    return render(request, 'todo/home.html')


def signup_user(request):
    if request.method == 'GET':
        return render(request, 'todo/signup.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('current_todos')
            except IntegrityError:
                return render(request, 'todo/signup.html',
                              {'form': UserCreationForm(), 'error': 'Пользователь с таким именем уже существует'})
        else:
            return render(request, 'todo/signup.html', {'form': UserCreationForm(), 'error': 'Вы ввели разные пароли'})


def login_user(request):
    if request.method == 'GET':
        return render(request, 'todo/login.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/login.html', {'form': AuthenticationForm(), 'error': 'Ошибка входа'})
        else:
            login(request, user)
            return redirect('current_todos')


@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def create_todo(request):
    if request.method == 'GET':
        return render(request, 'todo/create_todo.html', {'form': TodoTasksForm()})
    else:
        try:
            form = TodoTasksForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/create_todo.html',
                          {'form': TodoTasksForm(), 'error': 'Передано неверное значение'})


@login_required
def current_todos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'todo/current_todos.html', {'todos': todos})


@login_required
def completed_todos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request, 'todo/completed_todos.html', {'todos': todos})


@login_required
def view_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "GET":
        form = TodoTasksForm(instance=todo)
        return render(request, 'todo/view_todo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoTasksForm(request.POST, instance=todo)
            form.save()
            return redirect('current_todos')
        except ValueError:
            form = TodoTasksForm(instance=todo)
            return render(request, 'todo/view_todo.html', {'todo': todo, 'form': form, 'error': 'Неверное значение'})


@login_required
def complete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.date_completed = timezone.now()
        todo.save()
        return redirect('current_todos')


@login_required
def delete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.delete()
        return redirect('current_todos')
