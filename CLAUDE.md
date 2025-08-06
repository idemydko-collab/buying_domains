# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Test Project** - A complete Django 5.0 project with modern architecture, featuring Unfold admin interface, Celery task management, and BetterStack logging integration.

## Commands

### Development Commands
- `python manage.py runserver` - Start Django development server
- `python manage.py migrate` - Apply database migrations
- `python manage.py createsuperuser` - Create admin user
- `python manage.py collectstatic` - Collect static files
- `python manage.py test` - Run tests

### Celery Commands
- `celery -A core worker --loglevel=info` - Start Celery worker
- `celery -A core beat --loglevel=info` - Start Celery Beat scheduler
- `celery -A core flower` - Start Celery monitoring (if installed)

### Utility Commands
- `python manage.py shell` - Open Django shell
- `python manage.py makemigrations` - Create new migrations
- `python manage.py dbshell` - Open database shell

## Architecture

### Project Structure
```
test-project/
├── core/                    # Main Django project settings
│   ├── settings.py         # Django settings with environment switching
│   ├── celery.py          # Celery configuration
│   ├── utils.py           # Utility functions (permissions, decorators)
│   ├── logger.py          # Custom Logger class for BetterStack
│   └── admin.py           # Core admin configurations (User, Celery Beat)
├── apps/                   # Django applications
│   └── brain/             # Example app with models, views, tasks
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploaded files
└── components/           # Custom Unfold components
```

### Key Components

**Settings Configuration:**
- Environment-based database switching (SQLite/PostgreSQL)
- Celery integration with USE_CELERY flag
- Unfold admin with comprehensive navigation structure
- BetterStack logging configuration

**Celery Task System:**
- All tasks in `apps/[app_name]/tasks.py`
- Use `@use_celery` decorator for conditional execution
- Task execution depends on USE_CELERY environment flag

**Unfold Admin:**
- Complete navigation structure in SIDEBAR configuration
- All models added through SIDEBAR or TABS (never direct registration)
- Custom admin classes for User, Group, and Celery Beat models
- Permission-based navigation with `user_has_model_permission`

## Development Guidelines

### Celery Task Creation
1. **Location**: Always create tasks in `apps/[app_name]/tasks.py`
2. **Structure**:
   ```python
   from celery import shared_task
   from core.utils import use_celery
   from core.logger import Logger
   
   @shared_task
   @use_celery
   def my_task(param1, param2):
       Logger(f"Starting task with params: {param1}, {param2}", "info")
       # Task logic here
       Logger("Task completed successfully", "info")
       return result
   ```
3. **Execution**: Call with `my_task(param1, param2)` - USE_CELERY flag determines sync/async execution
4. **Scheduling**: Configure periodic tasks in Django Admin under Task Management

### Logging Requirements
**CRITICAL**: Never use print() statements - Always use the custom Logger class

```python
from core.logger import Logger

# Usage examples
Logger("Successfully processed 10 records", "info")
Logger("Debug information for troubleshooting", "debug")
Logger(f"Error occurred: {str(e)}", "error")
```

**Log Types** (use only these):
- `"info"`: General information and successful operations
- `"debug"`: Detailed debugging information  
- `"error"`: Errors and exceptions

### Unfold Admin Rules
1. **Navigation**: All models must be added through SIDEBAR or TABS configuration
2. **Icons**: Use Material Icons from https://fonts.google.com/icons
3. **Permissions**: Every navigation item must have permission callback
4. **Structure**: Navigation items must be in "items": [] arrays within sections
5. **Separation**: Use "separator": True between logical sections

### Environment Variables
- Always update both `.env` and `.env.example` when adding new variables
- USE_SQLITE: Controls database type (True=SQLite, False=PostgreSQL)
- USE_CELERY: Controls task execution mode (True=async, False=sync)
- DEBUG: Controls logging output and debug toolbar

### Database Switching
- Set `USE_SQLITE=True` for SQLite development
- Set `USE_SQLITE=False` and configure `DATABASE_URL` for PostgreSQL
- Automatic switching in settings.py based on USE_SQLITE flag

### Admin Panel Access
- Default superuser: admin/admin123
- Access at: http://localhost:8000/admin/
- Unfold interface with custom navigation and theming

### API Development
- Example API endpoint in `apps/brain/views.py`
- JSON responses with proper logging
- RESTful URL patterns

## Installation Notes

**Dependencies:** Install with pip after setting up virtual environment:
```bash
pip install -r requirements.txt
```

**Required System Packages** (if virtual environment fails):
```bash
sudo apt install python3.12-venv python3-pip
```

**Initial Setup:**
1. Create and activate virtual environment
2. Install dependencies
3. Run migrations
4. Create superuser
5. Start development server