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
