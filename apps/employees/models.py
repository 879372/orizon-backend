from django.db import models
from uuid import uuid4

class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)  # Pedreiro, Eletricista, etc.
    cpf = models.CharField(max_length=14, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='employees/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField(default=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ['employee', 'project', 'date']

    def __str__(self):
        status = "Presente" if self.present else "Ausente"
        return f"{self.employee.name} - {self.date} ({status})"
