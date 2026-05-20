from .models import PhaseCategory, PhaseTask

DEFAULT_PHASES = [
    {
        "name": "1. Serviços Preliminares & Projetos",
        "weight": 5.0,
        "tasks": [
            {"name": "Projetos Executivos e BIM", "weight": 40.0},
            {"name": "Mobilização e Canteiro de Obras", "weight": 40.0},
            {"name": "Ligações Provisórias de Água e Energia", "weight": 20.0}
        ]
    },
    {
        "name": "2. Infraestrutura & Fundações",
        "weight": 15.0,
        "tasks": [
            {"name": "Locação da Obra e Gabarito", "weight": 15.0},
            {"name": "Escavação e Movimentação de Terra", "weight": 25.0},
            {"name": "Fundações Profundas (Estacas)", "weight": 35.0},
            {"name": "Blocos de Coroamento e Vigas Baldrame", "weight": 25.0}
        ]
    },
    {
        "name": "3. Estrutura",
        "weight": 20.0,
        "tasks": [
            {"name": "Pilares - Formas e Armaduras", "weight": 30.0},
            {"name": "Vigas e Lajes - Escoramento e Concretagem", "weight": 50.0},
            {"name": "Desforma e Cura do Concreto", "weight": 20.0}
        ]
    },
    {
        "name": "4. Alvenaria e Divisórias",
        "weight": 10.0,
        "tasks": [
            {"name": "Elevação de Paredes de Alvenaria", "weight": 60.0},
            {"name": "Instalação de Vergas e Contravergas", "weight": 20.0},
            {"name": "Fixações e Encunhamento", "weight": 20.0}
        ]
    },
    {
        "name": "5. Cobertura e Impermeabilização",
        "weight": 5.0,
        "tasks": [
            {"name": "Estrutura de Suporte da Cobertura", "weight": 40.0},
            {"name": "Telhas e Calhas", "weight": 30.0},
            {"name": "Impermeabilização de Lajes e Áreas Frias", "weight": 30.0}
        ]
    },
    {
        "name": "6. Instalações Hidrossanitárias",
        "weight": 10.0,
        "tasks": [
            {"name": "Tubulações de Esgoto e Ventilação", "weight": 35.0},
            {"name": "Tubulações de Água Fria e Quente", "weight": 45.0},
            {"name": "Testes de Pressão e Estanqueidade", "weight": 20.0}
        ]
    },
    {
        "name": "7. Instalações Elétricas e Lógica",
        "weight": 10.0,
        "tasks": [
            {"name": "Passagem de Eletrodutos e Caixas de Passagem", "weight": 40.0},
            {"name": "Fiação Geral (Cabos de Energia/Lógica)", "weight": 40.0},
            {"name": "Montagem do Quadro de Distribuição", "weight": 20.0}
        ]
    },
    {
        "name": "8. Acabamentos e Revestimentos",
        "weight": 15.0,
        "tasks": [
            {"name": "Reboco e Regularização de Paredes", "weight": 30.0},
            {"name": "Contrapiso e Regularização de Níveis", "weight": 20.0},
            {"name": "Instalação de Porcelanatos e Revestimentos Cerâmicos", "weight": 50.0}
        ]
    },
    {
        "name": "9. Pinturas e Vidros",
        "weight": 7.0,
        "tasks": [
            {"name": "Aplicação de Selador e Massa Corrida", "weight": 40.0},
            {"name": "Pintura Interna e Externa", "weight": 40.0},
            {"name": "Instalação de Esquadrias e Vidros", "weight": 20.0}
        ]
    },
    {
        "name": "10. Limpeza Geral e Entrega",
        "weight": 3.0,
        "tasks": [
            {"name": "Limpeza Pós-Obra Detalhada", "weight": 50.0},
            {"name": "Vistoria Técnica de Qualidade", "weight": 30.0},
            {"name": "Entrega das Chaves e Manual do Proprietário", "weight": 20.0}
        ]
    }
]

def initialize_project_phases(project):
    """
    Seeds default 10-phase template to a project.
    Clears existing phases if they exist.
    """
    PhaseCategory.objects.filter(project=project).delete()
    
    for idx_cat, phase_data in enumerate(DEFAULT_PHASES, 1):
        cat = PhaseCategory.objects.create(
            project=project,
            order=idx_cat,
            name=phase_data["name"],
            weight_percentage=phase_data["weight"],
            progress_percentage=0.00
        )
        
        for idx_task, task_data in enumerate(phase_data["tasks"], 1):
            PhaseTask.objects.create(
                category=cat,
                order=idx_task,
                name=task_data["name"],
                weight_percentage=task_data["weight"],
                status='not_started'
            )
            
    project.progress_percentage = 0.00
    project.save(update_fields=['progress_percentage'])
