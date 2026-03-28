from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .services import WorkflowService
from .models import WorkflowInstance, WorkflowDefinition

def ui_view(request):
    return render(request, "index.html")

@method_decorator(csrf_exempt, name='dispatch')
class StartWorkflowView(View):
    def post(self, request):
        try:
            body = json.loads(request.body)
            service = WorkflowService()
            
            def_id = body.get("definition_id")
            if def_id == "default":
                # For UI testing, just grab the first one
                first_def = WorkflowDefinition.objects.first()
                if first_def:
                    def_id = first_def.id
                else:
                    return JsonResponse({"error": "No workflow definitions found. Run 'python manage.py seed_workflow'"}, status=400)

            instance_id = service.start_workflow(
                def_id,
                body.get("context", {})
            )

            return JsonResponse({"instance_id": str(instance_id)})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

class WorkflowStatusView(View):
    def get(self, request, instance_id):
        try:
            instance = WorkflowInstance.objects.get(id=instance_id)
            return JsonResponse({
                "id": str(instance.id),
                "status": instance.status,
                "current_step": instance.current_step,
                "context": instance.context,
                "version": instance.version,
            })
        except WorkflowInstance.DoesNotExist:
            return JsonResponse({"error": "Workflow instance not found"}, status=404)
