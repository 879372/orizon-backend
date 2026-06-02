from django.db import models
from django.utils.text import slugify
from uuid import uuid4
from core.fields import CompressedImageField

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='projects')
    client = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    start_date = models.DateField()
    planned_end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Não Iniciada'),
        ('in_progress', 'Em Andamento'),
        ('paused', 'Pausada'),
        ('delayed', 'Atrasada'),
        ('completed', 'Concluída'),
    ], default='not_started')
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_units = models.PositiveIntegerField(default=1)
    value_per_unit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    progress_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )  # auto-calculated from phases
    cover_image = CompressedImageField(upload_to='projects/', null=True, blank=True, max_width=1200, max_height=1200)
    slug = models.SlugField(unique=True, blank=True)  # auto-generated on save
    employees = models.ManyToManyField('employees.Employee', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_contract_value(self):
        return self.quantity_units * self.value_per_unit

    @property
    def total_labor_cost(self):
        return self.quantity_units * self.cost_per_unit

    def recalculate_progress(self):
        categories = self.phase_categories.all()
        total_weight = sum(c.weight_percentage for c in categories)
        if total_weight > 0:
            self.progress_percentage = sum(c.progress_percentage * c.weight_percentage for c in categories) / total_weight
        else:
            self.progress_percentage = 0.00
        self.save(update_fields=['progress_percentage'])

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Project.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
