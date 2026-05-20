from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from apps.companies.models import Company, CompanySettings
from apps.accounts.models import User
from apps.projects.models import Project
from apps.employees.models import Employee
from apps.suppliers.models import Supplier
from apps.materials.models import Material
from apps.financial.models import Transaction
from apps.tasks.models import KanbanTask
from apps.phases.utils import initialize_project_phases

class Command(BaseCommand):
    help = "Seeds initial development/demo data for Orizon Construtora."

    def handle(self, *args, **options):
        self.stdout.write("Iniciando semeadura de dados de demonstração...")

        # 1. Company
        company, created = Company.objects.get_or_create(
            cnpj="12.345.678/0001-99",
            defaults={
                "name": "Orizon Construtora",
                "email": "contato@orizon.com.br",
                "phone": "+55 11 99999-8888",
                "address": "Av. Brigadeiro Faria Lima, 2000 - São Paulo, SP",
                "plan": "enterprise",
                "is_active": True
            }
        )
        if created:
            self.stdout.write(f"Empresa '{company.name}' criada.")
        else:
            self.stdout.write(f"Empresa '{company.name}' já existia.")

        # Company Settings
        settings, _ = CompanySettings.objects.get_or_create(
            company=company,
            defaults={
                "show_financial_to_client": True,
                "primary_color": "#C9A84C",
                "custom_domain": "orizon.com.br"
            }
        )

        # 2. Users
        def create_user(email, name, role, company=None):
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": name,
                    "role": role,
                    "company": company,
                    "is_active": True
                }
            )
            if created:
                user.set_password("password123")
                user.save()
                self.stdout.write(f"Usuário {email} ({role}) criado.")
            return user

        super_admin = create_user("super_admin@orizon.com.br", "Super Admin Orizon", "super_admin")
        company_admin = create_user("admin@orizon.com.br", "Carlos Silva (Diretor)", "company_admin", company)
        engineer = create_user("engineer@orizon.com.br", "Eng. Mariana Costa", "company_member", company)
        client_user = create_user("client@orizon.com.br", "Dr. Roberto Almeida", "client", company)

        # 3. Project
        project, created = Project.objects.get_or_create(
            slug="residencial-horizon-boutique",
            defaults={
                "company": company,
                "client": client_user,
                "name": "Residencial Horizon Boutique",
                "description": "Edifício residencial boutique de alto padrão com 10 unidades exclusivas no bairro Jardins.",
                "address": "Alameda Lorena, 1500 - Jardins, São Paulo - SP",
                "start_date": date(2026, 1, 10),
                "planned_end_date": date(2026, 12, 20),
                "status": "in_progress",
                "total_budget": 3500000.00
            }
        )
        if created:
            self.stdout.write(f"Projeto '{project.name}' criado.")
            # Initialize phases
            initialize_project_phases(project)
            self.stdout.write("Fases padrão inicializadas para o projeto.")
        else:
            self.stdout.write(f"Projeto '{project.name}' já existia.")

        # 4. Employees
        emp1, _ = Employee.objects.get_or_create(
            company=company,
            cpf="111.111.111-11",
            defaults={
                "name": "Severino Santos",
                "role": "Mestre de Obras",
                "phone": "(11) 98888-7777",
                "email": "severino@orizon.com.br",
                "daily_rate": 250.00,
                "is_active": True
            }
        )
        emp2, _ = Employee.objects.get_or_create(
            company=company,
            cpf="222.222.222-22",
            defaults={
                "name": "Josevaldo Cruz",
                "role": "Carpinteiro",
                "phone": "(11) 97777-6666",
                "email": "josevaldo@orizon.com.br",
                "daily_rate": 180.00,
                "is_active": True
            }
        )
        project.employees.add(emp1, emp2)

        # 5. Suppliers
        sup1, _ = Supplier.objects.get_or_create(
            company=company,
            name="Votorantim Cimentos",
            defaults={
                "cnpj_cpf": "33.444.555/0001-22",
                "email": "vendas@votorantim.com.br",
                "phone": "(11) 4004-0000",
                "category": "materials",
                "rating": 5,
                "notes": "Excelente qualidade e pontualidade na entrega de concreto.",
                "is_active": True
            }
        )
        sup2, _ = Supplier.objects.get_or_create(
            company=company,
            name="Gerdau Aços",
            defaults={
                "cnpj_cpf": "44.555.666/0001-33",
                "email": "comercial@gerdau.com.br",
                "phone": "(11) 3003-1111",
                "category": "materials",
                "rating": 5,
                "is_active": True
            }
        )

        # 6. Materials
        Material.objects.get_or_create(
            company=company,
            project=project,
            name="Cimento CP-II 50kg",
            defaults={
                "supplier": sup1,
                "unit": "un",
                "quantity_ordered": 500.00,
                "quantity_received": 150.00,
                "unit_cost": 42.50,
                "status": "waiting",
                "expected_date": date(2026, 6, 15),
                "notes": "Lote inicial para fundações."
            }
        )
        Material.objects.get_or_create(
            company=company,
            project=project,
            name="Aço CA-50 10.0mm",
            defaults={
                "supplier": sup2,
                "unit": "kg",
                "quantity_ordered": 2000.00,
                "quantity_received": 2000.00,
                "unit_cost": 8.20,
                "status": "received",
                "notes": "Vergalhões para vigas baldrame."
            }
        )

        # 7. Financial Transactions
        Transaction.objects.get_or_create(
            project=project,
            company=company,
            description="Aporte Inicial de Contrato",
            defaults={
                "category": "other",
                "type": "income",
                "amount": 500000.00,
                "date": date(2026, 1, 15),
                "created_by": company_admin
            }
        )
        Transaction.objects.get_or_create(
            project=project,
            company=company,
            description="Compra de Vergalhões Gerdau",
            defaults={
                "category": "material",
                "type": "expense",
                "amount": 16400.00,
                "date": date(2026, 2, 5),
                "supplier": sup2,
                "created_by": engineer
            }
        )

        # 8. Kanban Tasks
        KanbanTask.objects.get_or_create(
            project=project,
            company=company,
            title="Aprovar Projetos Complementares",
            defaults={
                "description": "Revisar e liberar projetos estrutural, elétrico e hidráulico no BIM.",
                "column": "done",
                "priority": "high",
                "assigned_to": emp1,
                "due_date": date(2026, 2, 10),
                "order": 1
            }
        )
        KanbanTask.objects.get_or_create(
            project=project,
            company=company,
            title="Escavação e Movimentação de Terra",
            defaults={
                "description": "Iniciar escavação para sapatas e blocos conforme locação topográfica.",
                "column": "in_progress",
                "priority": "high",
                "assigned_to": emp2,
                "due_date": date(2026, 6, 20),
                "order": 1
            }
        )
        KanbanTask.objects.get_or_create(
            project=project,
            company=company,
            title="Cotar Compra de Tubulações Hidráulicas",
            defaults={
                "description": "Realizar cotação com Tigre e Amanco para tubos de PVC prediais.",
                "column": "todo",
                "priority": "medium",
                "due_date": date(2026, 7, 5),
                "order": 2
            }
        )

        # Force a quick recalculate on project
        project.recalculate_progress()

        self.stdout.write(self.style.SUCCESS("Dados de demonstração semeados com sucesso!"))
