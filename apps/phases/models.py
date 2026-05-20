from django.db import models
from uuid import uuid4
from django.utils import timezone

class PhaseCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='phase_categories')
    order = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['order']

    def recalculate_progress(self):
        tasks = self.tasks.all()
        total_weight = sum(t.weight_percentage for t in tasks)
        if total_weight > 0:
            completed_weight = sum(t.weight_percentage for t in tasks if t.status == 'completed')
            self.progress_percentage = (completed_weight / total_weight) * 100
        else:
            self.progress_percentage = 0.00
        self.save(update_fields=['progress_percentage'])
        
        # Recalculate project progress
        self.project.recalculate_progress()

    def __str__(self):
        return f"{self.project.name} - {self.name}"

class PhaseTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    category = models.ForeignKey(PhaseCategory, on_delete=models.CASCADE, related_name='tasks')
    order = models.PositiveIntegerField()
    name = models.CharField(max_length=300)
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Não Iniciada'),
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluída'),
    ], default='not_started')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None
        super().save(*args, **kwargs)
        self.category.recalculate_progress()

    def __str__(self):
        return f"{self.category.name} - {self.name}"
