from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, authenticate
from .decorators import staff_required
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q, Count
from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from .serializers import TodoSerializer, UserSerializer
from .forms import TodoForm, SignUpForm, EmailAuthenticationForm
from .models import Todo

# --- API VIEWS ---

class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Todo.objects.filter(removed=False).order_by('-created_at')
        return Todo.objects.filter(user=self.request.user, removed=False).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- MVT VIEWS ---

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.get_user())
        return redirect(request.GET.get('next', 'home'))
    return render(request, 'registration/login.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def list_todos(request):
    query = request.GET.get('q', '')
    status_filters = request.GET.getlist('status')
    priority_filters = request.GET.getlist('priority')

    todos_list = Todo.objects.filter(user=request.user, removed=False).order_by('-created_at')

    if query:
        todos_list = todos_list.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if status_filters:
        todos_list = todos_list.filter(status__in=status_filters)
    if priority_filters:
        todos_list = todos_list.filter(priority__in=priority_filters)

    page_size = getattr(settings, 'TODOS_PAGE_SIZE', 25)
    paginator = Paginator(todos_list, page_size)
    page_number = request.GET.get('page')
    todos = paginator.get_page(page_number)

    # Calculate profile stats for inline drawer
    total_created = Todo.objects.filter(user=request.user).count()
    total_done = Todo.objects.filter(user=request.user, status=Todo.Status.DONE).count()
    total_pending = Todo.objects.filter(user=request.user, status=Todo.Status.PENDING, removed=False).count()

    return render(request, 'todos/home.html', {
        'todos': todos,
        'query': query,
        'status_filters': status_filters,
        'priority_filters': priority_filters,
        'total_created': total_created,
        'total_done': total_done,
        'total_pending': total_pending
    })

@login_required
def create_todo(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            if is_ajax:
                return JsonResponse({'success': True, 'redirect': '/' })
            return redirect('home')
    else:
        form = TodoForm()
    if is_ajax:
        return render(request, 'todos/todo_form_partial.html', {'form': form})
    return render(request, 'todos/todo_form.html', {'form': form, 'title': _('New Todo')})

from django.http import JsonResponse

@login_required
def edit_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user, removed=False)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            if is_ajax:
                return JsonResponse({'success': True, 'redirect': '/' })
            return redirect('home')
    else:
        form = TodoForm(instance=todo)
    if is_ajax:
        return render(request, 'todos/todo_form_partial.html', {'form': form, 'todo': todo})
    return render(request, 'todos/todo_form.html', {'form': form, 'title': _('Update Todo')})

@login_required
def delete_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'
    if request.method == 'POST':
        todo.removed = True
        todo.save()
        if is_ajax:
            return JsonResponse({'success': True, 'redirect': '/'})
        return redirect('home')
    if is_ajax:
        return render(request, 'todos/delete_todo_partial.html', {'todo': todo})
    return render(request, 'todos/delete_todo.html', {'todo': todo})

@login_required
def toggle_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == 'POST':
        if todo.status == Todo.Status.DONE:
            todo.status = Todo.Status.PENDING
        else:
            todo.status = Todo.Status.DONE
        todo.save()
    return redirect('home')

@login_required
def profile(request):
    total_created = Todo.objects.filter(user=request.user).count()
    total_done = Todo.objects.filter(user=request.user, status=Todo.Status.DONE).count()
    total_pending = Todo.objects.filter(user=request.user, status=Todo.Status.PENDING, removed=False).count()

    context = {
        'total_created': total_created,
        'total_done': total_done,
        'total_pending': total_pending,
    }
    return render(request, 'todos/profile.html', context)


@staff_required
def admin_dashboard(request):
    from django.utils import timezone
    from datetime import timedelta
    
    total_users = User.objects.count()
    total_todos = Todo.objects.count()
    
    # Usuários ativos nos últimos 7 dias
    seven_days_ago = timezone.now() - timedelta(days=7)
    active_users_count = User.objects.filter(last_login__gte=seven_days_ago).count()
    
    # Quantidade de afazeres ativos por status
    status_counts = Todo.objects.filter(removed=False).values('status').annotate(total=Count('id'))
    total_done = 0
    total_pending = 0
    for item in status_counts:
        if item['status'] == Todo.Status.DONE:
            total_done = item['total']
        elif item['status'] == Todo.Status.PENDING:
            total_pending = item['total']

    # Quantidade de afazeres ativos por prioridade
    priority_counts = Todo.objects.filter(removed=False).values('priority').annotate(total=Count('id'))
    priority_dict = {
        'HIGH': 0,
        'MEDIUM': 0,
        'LOW': 0,
        'NORMAL': 0
    }
    for item in priority_counts:
        if item['priority'] in priority_dict:
            priority_dict[item['priority']] = item['total']

    all_todos = Todo.objects.all().order_by('-created_at')
    paginator = Paginator(all_todos, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'total_users': total_users,
        'active_users_count': active_users_count,
        'total_todos': total_todos,
        'total_done': total_done,
        'total_pending': total_pending,
        'high_priority': priority_dict['HIGH'],
        'medium_priority': priority_dict['MEDIUM'],
        'low_priority': priority_dict['LOW'],
        'normal_priority': priority_dict['NORMAL'],
        'all_todos': page_obj
    }
    return render(request, 'todos/admin_dashboard.html', context)
