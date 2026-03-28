from .models import WorkflowDefinition
from .factory import WorkflowFactory

class WorkflowService:
    def start_workflow(self, definition_id, context):
        definition = WorkflowDefinition.objects.get(id=definition_id)

        start_step = definition.definition["start_step"]

        engine = WorkflowFactory.create_engine()

        instance = engine.repo.create_instance(
            definition,
            start_step,
            context
        )

        engine.dispatcher.enqueue(instance.id, start_step)

        return instance.id
