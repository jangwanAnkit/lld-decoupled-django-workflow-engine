from .repository import WorkflowRepository
from .registry import ExecutorRegistry
from .dispatcher import TaskDispatcher
from .engine import WorkflowEngine

class WorkflowFactory:
    @staticmethod
    def create_engine():
        repo = WorkflowRepository()
        registry = ExecutorRegistry()
        dispatcher = TaskDispatcher()

        return WorkflowEngine(repo, registry, dispatcher)
