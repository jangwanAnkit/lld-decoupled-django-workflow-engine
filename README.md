# Django Workflow Engine (LLD System Design)

This repository serves as a Low-Level Design (LLD) exercise showcasing a robust, decoupled **Workflow Engine** built with Django. It implements several classic software design patterns to achieve a flexible, maintainable architecture.

## Architecture & Patterns

The system is separated into layers demonstrating clean architecture:

* **Persistence Layer (Models)**: Django ORM schema representing Workflow Definitions, Instances, and Step Executions.
* **DB Abstraction (Repository Pattern)**: `WorkflowRepository` isolates database queries from business logic.
* **Strategy Pattern (Executors/Agents)**: Pluggable `StepExecutor` classes (e.g., `KYCExecutor`, `EmailExecutor`) handle specific business logic.
* **Factory Pattern & Dependency Injection**: `WorkflowFactory` constructs the orchestrator engine with injected dependencies.
* **Orchestrator & State Machine (Engine)**: `WorkflowEngine` handles stepping through states, evaluating transitions, and deduplication (idempotency).
* **Queue Abstraction (Dispatcher)**: `TaskDispatcher` simulates a task queue (like Celery or Kafka) for async step processing.
* **API Layer (Views & Services)**: Clean API boundaries that interact only with a `WorkflowService`.

## Getting Started

Follow these steps to run the workflow engine locally:

### 1. Set Up Environment
First, clone the repository and navigate into it:
```bash
# Initialize a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`. This file holds local configuration like `SECRET_KEY` and `DEBUG` mode.
```bash
cp .env.example .env
```

### 3. Initialize Database & Seed Data
Apply Django migrations to set up the SQLite database, then use the custom management command to seed a mock workflow.
```bash
uv run python manage.py migrate
uv run python manage.py seed_workflow
```

### 4. Run the Development Server
```bash
uv run python manage.py runserver
```

You can now interact with the web API endpoints or explore the application via the Django shell.

## Further Reading
* For a deep dive into the code and architecture decisions, see [django-workflow-engine.md](./django-workflow-engine.md).
