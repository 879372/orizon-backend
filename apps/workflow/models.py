from django.db import models
from uuid import uuid4


class FlowNode(models.Model):
    STATUS_CHOICES = [
        ('open', 'Aberto'),
        ('blocked', 'Bloqueado'),
        ('in_progress', 'Em Andamento'),
        ('done', 'Concluído'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='flow_nodes'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    position_x = models.FloatField(default=100)
    position_y = models.FloatField(default=100)
    color = models.CharField(max_length=20, blank=True)  # hex personalizado opcional
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.project.name})"

    def is_blocked_by_dependencies(self):
        """Verifica se algum predecessor ainda não foi concluído."""
        incoming = self.incoming_edges.select_related('source')
        for edge in incoming:
            if edge.source.status != 'done':
                return True
        return False


class FlowEdge(models.Model):
    """Aresta direcional: source → target (target fica bloqueado até source = done)."""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='flow_edges'
    )
    source = models.ForeignKey(
        FlowNode,
        on_delete=models.CASCADE,
        related_name='outgoing_edges'
    )
    target = models.ForeignKey(
        FlowNode,
        on_delete=models.CASCADE,
        related_name='incoming_edges'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('source', 'target')

    def __str__(self):
        return f"{self.source.title} → {self.target.title}"


class FlowNodeItem(models.Model):
    """Item de checklist dentro do card/nó."""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    node = models.ForeignKey(
        FlowNode,
        on_delete=models.CASCADE,
        related_name='items'
    )
    label = models.CharField(max_length=300)
    is_done = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.label
