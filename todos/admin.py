from django.contrib import admin
from .models import Todo

class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'status', 'due_date', 'created_at', 'removed')
    list_filter = ('priority', 'status', 'removed')
    search_fields = ('title', 'description', 'user__username')

admin.site.register(Todo, TodoAdmin)
