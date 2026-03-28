class WorkflowEngine:
    def __init__(self, repo, registry, dispatcher):
        self.repo = repo
        self.registry = registry
        self.dispatcher = dispatcher

    def process_step(self, instance_id, step_name):
        instance = self.repo.get_instance(instance_id)
        definition = instance.definition.definition

        key = f"{instance_id}_{step_name}"

        if self.repo.is_duplicate(key):
            print("Duplicate execution skipped")
            return

        step_def = definition["steps"][step_name]
        executor = self.registry.get(step_def["type"])

        status, data = executor.execute(instance.context)

        self.repo.save_execution(instance, step_name, status, data, key)
        instance.context.update(data)

        # transition logic (State Machine)
        next_step = None
        for t in definition["transitions"]:
            if t["from"] == step_name and t["on"] == status:
                next_step = t["to"]

        if not next_step:
            instance.status = "COMPLETED"
        else:
            instance.current_step = next_step
            self.dispatcher.enqueue(instance.id, next_step)

        self.repo.update_instance(instance)
