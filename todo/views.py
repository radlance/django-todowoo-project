from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from .forms import TodoForm
from .models import Todo
from django.contrib.auth.decorators import login_required


def login_forbidden(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('currenttodos')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper


@login_forbidden
def home(request):
    return render(request, 'todo/home.html')


@login_forbidden
def signupUser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:

        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(),
                                                                'error': 'the user is already registered'})
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm(),
                                                        'error': 'Password did not match'})


@login_forbidden
def loginUser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html',
                          {'form': AuthenticationForm(), 'error': 'Username and password did not match.'})
        else:
            login(request, user)
            return redirect('currenttodos')


def logoutUser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def createTodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html',
                          {'form': TodoForm(), 'error': 'Bad data past in. Try again.'})


@login_required
def currentTodos(request):
    todos = Todo.objects.filter(user=request.user.id, datecompleted__isnull=True).order_by('-important')
    return render(request, 'todo/currenttodos.html', {'todos': todos})


@login_required
def completeTodos(request):
    todos = Todo.objects.filter(user=request.user.id, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completetodos.html', {'todos': todos})


@login_required
def viewTodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'error': 'Bad info.'})


@login_required
def completeTodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deleteTodo(request, todo_pk):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
        todo.delete()
        return redirect('currenttodos')
