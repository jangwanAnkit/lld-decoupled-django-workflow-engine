class TaskDispatcher:
    """
    In real world → Celery / Kafka
    """

    def enqueue(self, instance_id, step_name):
        from .factory import WorkflowFactory
        engine = WorkflowFactory.create_engine()
        engine.process_step(instance_id, step_name)
