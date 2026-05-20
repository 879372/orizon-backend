from django.db import models
from uuid import uuid4

class KanbanTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='kanban_tasks')
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    column = models.CharField(max_length=20, choices=[
        ('todo', 'A Fazer'),
        ('in_progress', 'Em Andamento'),
        ('waiting', 'Aguardando'),
        ('done', 'Concluído'),
    ], default='todo')
    priority = models.CharField(max_length=15, choices=[
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
    ], default='medium')
    assigned_to = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    phase_task = models.ForeignKey('phases.PhaseTask', on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title
