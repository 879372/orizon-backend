from django.test import TestCase
from apps.companies.models import Company
from apps.accounts.models import User
from apps.projects.models import Project
from apps.phases.models import PhaseCategory, PhaseTask
from apps.phases.utils import initialize_project_phases
from datetime import date

class OrizonBackendTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Orizon Test",
            cnpj="11.222.333/0001-44",
            email="test@orizon.com",
            phone="123456",
            plan="basic"
        )
        self.client_user = User.objects.create(
            email="client@test.com",
            name="Client User",
            role="client",
            company=self.company
        )
        self.project = Project.objects.create(
            company=self.company,
            client=self.client_user,
            name="Test Building",
            address="123 Main St",
            start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 12, 31),
            status="in_progress",
            total_budget=1000000.00
        )

    def test_project_slug_auto_generation(self):
        self.assertEqual(self.project.slug, "test-building")
        
        another_project = Project.objects.create(
            company=self.company,
            client=self.client_user,
            name="Test Building",
            address="456 Other St",
            start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 12, 31),
            total_budget=500000.00
        )
        self.assertEqual(another_project.slug, "test-building-1")

    def test_initialize_phases_and_progress_recalculation(self):
        initialize_project_phases(self.project)
        
        categories = self.project.phase_categories.all()
        self.assertEqual(categories.count(), 10)
        
        self.project.refresh_from_db()
        self.assertEqual(self.project.progress_percentage, 0.00)
        
        first_cat = categories.first()
        first_task = first_cat.tasks.first()
        first_task.status = 'completed'
        first_task.save()
        
        first_cat.refresh_from_db()
        self.assertAlmostEqual(float(first_cat.progress_percentage), 40.00)
        
        self.project.refresh_from_db()
        self.assertAlmostEqual(float(self.project.progress_percentage), 2.00)
