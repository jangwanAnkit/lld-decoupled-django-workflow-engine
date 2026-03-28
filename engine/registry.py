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
