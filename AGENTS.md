## Repository Context
This is a **System Design Exercise** repository. The goal is to build a Low-Level Design (LLD) mock of a decoupled **Workflow Engine** built on top of Django. We are optimizing for demonstrating clean architecture, design patterns, and maintainability—not for rapid application development or full-stack UI building.

## Architecture & Boundaries
When generating or modifying code, strictly adhere to the following architectural layers:

1. **Models (`models.py`)**: Defines the persistence layer (State). No business logic goes here.
2. **Repository (`repository.py`)**: The ONLY place that interacts directly with the database (Django ORM). Do not write `.objects.filter()` in the Engine or Views.
3. **Executors (`executors.py`)**: Implementations of workflow steps (Strategy Pattern). They receive context, do a specific task, and return a status and new context.
4. **Registry & Factory (`registry.py`, `factory.py`)**: Dependency Injection and orchestration setup.  
5. **Engine (`engine.py`)**: The core State Machine. It evaluates where a workflow is, executes the next step, saves the state, and enqueues the next transition.
6. **Dispatcher (`dispatcher.py`)**: Abstraction for async execution (simulates Celery/Kafka).
7. **Views/Services (`views.py`, `services.py`)**: The entrypoints. Views handle HTTP; Services handle the transaction boundaries.

## Coding Guidelines
- **Dependency Management**: This project uses **`uv`** for Python management. Do not suggest standard `pip install` or `python -m venv`. Use `uv venv`, `uv pip install`, and `uv run`.
- **Hardcoding**: Do not hardcode secrets. Advise the use of `.env` files and `os.getenv()`.
- **Type Hinting**: Prefer adding Python type hints (`-> dict`, `-> str`, etc.) where clear, as this is a system design exercise and types clarify contracts.
- **Simplicity over Scale**: We are building a mock simulation. Do not actually install Celery or Kafka unless explicitly asked. Stick to printing to the console or synchronous execution in the dispatcher to demonstrate the *concept*.

Please follow these guidelines strictly when producing code or answering questions about this repository!
