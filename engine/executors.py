class StepExecutor:
    def execute(self, context):
        raise NotImplementedError

class KYCExecutor(StepExecutor):
    def execute(self, context):
        if context.get("user_id", 1) % 2 == 0:
            return "SUCCESS", {"kyc": "passed"}
        return "FAIL", {"kyc": "failed"}

class EmailExecutor(StepExecutor):
    def execute(self, context):
        print(f"Sending email to {context.get('user_id')}")
        return "SUCCESS", {"email": "sent"}

class ManualReviewExecutor(StepExecutor):
    def execute(self, context):
        print("Manual review triggered")
        return "SUCCESS", {"review": "approved"}
