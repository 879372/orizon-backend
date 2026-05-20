from django.core.management.base import BaseCommand
from apps.projects.models import Project
from apps.phases.utils import initialize_project_phases

class Command(BaseCommand):
    help = "Seeds default construction phases template to all projects or a specific one."

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=str,
            help='Specific project ID to seed phases for',
        )

    def handle(self, *args, **options):
        project_id = options.get('project_id')
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                projects = [project]
            except Project.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Projeto com ID {project_id} não encontrado."))
                return
        else:
            projects = Project.objects.all()

        for project in projects:
            self.stdout.write(f"Semeando fases padrão para o projeto: {project.name}")
            initialize_project_phases(project)
            self.stdout.write(self.style.SUCCESS(f"Fases do projeto {project.name} semeadas com sucesso."))
