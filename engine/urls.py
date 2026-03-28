from django.urls import path
from .views import StartWorkflowView, WorkflowStatusView, ui_view

urlpatterns = [
    path("start/", StartWorkflowView.as_view(), name="start_workflow"),
    path("status/<uuid:instance_id>/", WorkflowStatusView.as_view(), name="workflow_status"),
    path("", ui_view, name="ui_view"),
]
