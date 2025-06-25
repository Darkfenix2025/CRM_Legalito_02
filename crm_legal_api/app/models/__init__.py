# Importar todos los modelos para que Flask-Migrate los detecte fácilmente.
# Esto también permite un acceso más limpio desde otras partes de la aplicación,
# por ejemplo: from app.models import User, Client, etc.

from .user_model import User
from .client_model import Client, client_tags_association
from .case_model import Case, case_tags_association
from .tag_model import Tag
from .audience_model import Audience
from .task_model import Task
from .document_model import Document
from .involved_party_model import InvolvedParty
from .case_ia_analysis_model import CaseIAAnalysis
from .financial_models import Fee, Expense, Invoice

# Lista __all__ para controlar lo que se importa con 'from app.models import *'
# (aunque es mejor importar explícitamente lo que se necesita)
__all__ = [
    'User',
    'Client', 'client_tags_association',
    'Case', 'case_tags_association',
    'Tag',
    'Audience',
    'Task',
    'Document',
    'InvolvedParty',
    'CaseIAAnalysis',
    'Fee',
    'Expense',
    'Invoice'
]
