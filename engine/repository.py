from .models import WorkflowInstance, StepExecution

class WorkflowRepository:
    def create_instance(self, definition, start_step, context):
        return WorkflowInstance.objects.create(
            definition=definition,
            current_step=start_step,
            context=context
        )

    def get_instance(self, instance_id):
        return WorkflowInstance.objects.get(id=instance_id)

    def update_instance(self, instance):
        instance.version += 1
        instance.save()

    def save_execution(self, instance, step_name, status, data, key):
        return StepExecution.objects.create(
            instance=instance,
            step_name=step_name,
            status=status,
            response=data,
            idempotency_key=key
        )

    def is_duplicate(self, key):
        return StepExecution.objects.filter(idempotency_key=key).exists()
