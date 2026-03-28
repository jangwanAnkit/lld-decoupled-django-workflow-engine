from django.contrib import admin
from .models import WorkflowDefinition, WorkflowInstance, StepExecution

@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "version", "created_at")

@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ("id", "definition", "current_step", "status", "version", "created_at")
    list_filter = ("status", "current_step")

@admin.register(StepExecution)
class StepExecutionAdmin(admin.ModelAdmin):
    list_display = ("id", "instance", "step_name", "status", "retry_count", "created_at")
    list_filter = ("status", "step_name")
