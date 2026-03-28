
# HOW TO READ THIS

Well build a proper Django app:

```
config/

 engine/
    models.py         DB schema
    repository.py     DB abstraction
    executors.py      Strategy pattern
    registry.py       Factory pattern
    engine.py         Orchestrator
    dispatcher.py     Queue abstraction
    services.py       Business layer
    views.py          API layer
    urls.py

 config/
    settings.py
    urls.py
```

---

# 1. MODELS (Persistence Layer)

```python
# engine/models.py

from django.db import models
import uuid


class WorkflowDefinition(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=100)
    version = models.IntegerField()
    definition = models.JSONField()  # steps + transitions
    created_at = models.DateTimeField(auto_now_add=True)


class WorkflowInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    definition = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE)
    current_step = models.CharField(max_length=50)
    context = models.JSONField(default=dict)
    status = models.CharField(max_length=20, default="RUNNING")
    version = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class StepExecution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE)
    step_name = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    response = models.JSONField(default=dict)
    retry_count = models.IntegerField(default=0)
    idempotency_key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

# 2. REPOSITORY (DB Abstraction)

```python
# engine/repository.py

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
```

---

# 3. EXECUTORS (Strategy Pattern)

```python
# engine/executors.py

class StepExecutor:
    def execute(self, context):
        raise NotImplementedError


class KYCExecutor(StepExecutor):
    def execute(self, context):
        if context["user_id"] % 2 == 0:
            return "SUCCESS", {"kyc": "passed"}
        return "FAIL", {"kyc": "failed"}


class EmailExecutor(StepExecutor):
    def execute(self, context):
        print(f"Sending email to {context['user_id']}")
        return "SUCCESS", {"email": "sent"}


class ManualReviewExecutor(StepExecutor):
    def execute(self, context):
        print("Manual review triggered")
        return "SUCCESS", {"review": "approved"}
```

---

# 4. REGISTRY (Factory Pattern)

```python
# engine/registry.py

from .executors import KYCExecutor, EmailExecutor, ManualReviewExecutor


class ExecutorRegistry:

    def __init__(self):
        self.executors = {
            "KYC_CHECK": KYCExecutor(),
            "EMAIL": EmailExecutor(),
            "MANUAL_REVIEW": ManualReviewExecutor(),
        }

    def get(self, step_type):
        return self.executors[step_type]
```

---

# 5. DISPATCHER (Queue Abstraction)

```python
# engine/dispatcher.py

class TaskDispatcher:
    """
    In real world -> Celery / Kafka
    """

    def enqueue(self, instance_id, step_name):
        from .factory import WorkflowFactory
        engine = WorkflowFactory.create_engine()
        engine.process_step(instance_id, step_name)
```

Note: Replace later with:

```python
enqueue.delay(instance_id, step_name)
```

---

# 6. ENGINE (Orchestrator + State Machine)

```python
# engine/engine.py

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
```

---

# 7. FACTORY (Dependency Injection)

```python
# engine/factory.py

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
```

---

# 8. SERVICE LAYER

```python
# engine/services.py

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
```

---

# 9. VIEWS (API Layer)

```python
# engine/views.py

from django.views import View
from django.http import JsonResponse
import json
from .services import WorkflowService


class StartWorkflowView(View):

    def post(self, request):
        body = json.loads(request.body)

        service = WorkflowService()

        instance_id = service.start_workflow(
            body["definition_id"],
            body.get("context", {})
        )

        return JsonResponse({"instance_id": str(instance_id)})
```

---

# 10. URLS

```python
# engine/urls.py

from django.urls import path
from .views import StartWorkflowView

urlpatterns = [
    path("start/", StartWorkflowView.as_view()),
]
```

---

# ROOT URL

```python
# config/urls.py

from django.urls import path, include

urlpatterns = [
    path("engine/", include("engine.urls")),
]
```

---

# END-TO-END FLOW (REAL DJANGO FLOW)

```text
Client -> Django View
        |
Service Layer
        |
Factory (DI)
        |
WorkflowEngine
        |
Repository (DB)
        |
Dispatcher (Celery/Kafka)
        |
Worker -> Engine.process_step()
        |
Executor (Strategy)
        |
DB update + next step
```

---

# LEARNING

This is now a **real LLD-ready backend** with:

* [x] Django ORM (real persistence)
* [x] Repository pattern
* [x] Strategy pattern (executors)
* [x] Factory + DI
* [x] State machine (transitions)
* [x] Queue abstraction
* [x] Service layer separation

---

# FINAL LINE

> "structured a Django system with models for persistence, services for orchestration, and a domain engine using strategy and state machine patterns, with dependencies injected via factories and async execution handled through a dispatcher like Celery."

---
