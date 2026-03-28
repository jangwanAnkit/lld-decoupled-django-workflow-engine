from django.core.management.base import BaseCommand
from engine.models import WorkflowDefinition
import uuid

class Command(BaseCommand):
    help = 'Seed a sample workflow definition for testing'

    def handle(self, *args, **kwargs):
        definition = {
            "start_step": "KYC",
            "steps": {
                "KYC": {"type": "KYC_CHECK"},
                "EMAIL_USER": {"type": "EMAIL"},
                "MANUAL_REVIEW": {"type": "MANUAL_REVIEW"}
            },
            "transitions": [
                {"from": "KYC", "on": "SUCCESS", "to": "EMAIL_USER"},
                {"from": "KYC", "on": "FAIL", "to": "MANUAL_REVIEW"},
                {"from": "EMAIL_USER", "on": "SUCCESS", "to": "MANUAL_REVIEW"}
            ]
        }
        
        definition_id = f"onboarding_v1_{uuid.uuid4().hex[:8]}"

        WorkflowDefinition.objects.create(
            id=definition_id,
            name="User Onboarding",
            version=1,
            definition=definition
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created WorkflowDefinition with id: {definition_id}'))
