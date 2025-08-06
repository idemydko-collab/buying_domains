# Test Project

A complete Django 5.0 project with modern architecture, featuring Unfold admin interface, Celery task management, and BetterStack logging integration.

## Features

- 🚀 **Django 5.0** with modern project structure
- 🎨 **Unfold Admin** - Beautiful, modern admin interface
- ⚡ **Celery & Redis** - Background task processing
- 📊 **BetterStack Logging** - Professional logging solution
- 🗄️ **Flexible Database** - SQLite/PostgreSQL switching
- 🧪 **Testing Suite** - Pre-configured test environment
- 📱 **Responsive Design** - Tailwind CSS frontend

## Quick Start

### Prerequisites

Ensure you have Python 3.12+ installed:
```bash
python3 --version
```

### Installation

1. **Install system dependencies** (Ubuntu/Debian):
```bash
sudo apt install python3.12-venv python3-pip
```

2. **Create and activate virtual environment**:
```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. **Install dependencies**:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Set up environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run migrations**:
```bash
python manage.py migrate
```

6. **Create superuser**:
```bash
python manage.py createsuperuser
# Use: admin / admin123 for quick setup
```

7. **Start development server**:
```bash
python manage.py runserver
```

Visit http://localhost:8000 to see your project!

## Project Structure

```
test-project/
├── core/                    # Main Django project
│   ├── settings.py         # Django settings
│   ├── celery.py          # Celery configuration
│   ├── utils.py           # Utility functions
│   ├── logger.py          # Custom logging
│   └── admin.py           # Core admin configs
├── apps/                   # Django applications
│   └── brain/             # Example app
├── templates/             # HTML templates
├── static/               # Static files
├── media/                # User uploads
└── components/           # Custom components
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Core Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
USE_SQLITE=True  # Set to False for PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Celery
USE_CELERY=False  # Set to True for async tasks
CELERY_BROKER_URL=redis://localhost:6379/0

# Logging
LOGTAIL_SOURCE_TOKEN=your-token
LOGTAIL_HOST=your-host
```

### Database Options

**SQLite (Development)**:
- Set `USE_SQLITE=True`
- No additional setup required

**PostgreSQL (Production)**:
- Set `USE_SQLITE=False`
- Configure `DATABASE_URL`
- Install: `pip install psycopg2-binary`

### Celery Setup

For background tasks:

1. **Install Redis**:
```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Start Redis
redis-server
```

2. **Enable Celery**:
```bash
# In .env file
USE_CELERY=True
```

3. **Start Celery worker** (new terminal):
```bash
celery -A core worker --loglevel=info
```

4. **Start Celery Beat** (new terminal):
```bash
celery -A core beat --loglevel=info
```

## Usage

### Admin Panel
- URL: http://localhost:8000/admin/
- Login: admin / admin123
- Features: User management, Celery task scheduling

### API Endpoints
- Home: http://localhost:8000/
- Examples: http://localhost:8000/examples/
- API: http://localhost:8000/api/examples/

### Creating Tasks

Add tasks to `apps/[app]/tasks.py`:

```python
from celery import shared_task
from core.utils import use_celery
from core.logger import Logger

@shared_task
@use_celery
def my_task(param):
    Logger(f"Processing: {param}", "info")
    # Task logic here
    return "completed"
```

### Logging

Always use the custom Logger class:

```python
from core.logger import Logger

Logger("Operation successful", "info")
Logger("Debug information", "debug")
Logger("Error occurred", "error")
```

## Development Commands

```bash
# Django
python manage.py runserver          # Start server
python manage.py migrate            # Apply migrations
python manage.py makemigrations     # Create migrations
python manage.py test               # Run tests
python manage.py collectstatic      # Collect static files

# Celery
celery -A core worker --loglevel=info    # Start worker
celery -A core beat --loglevel=info      # Start scheduler
celery -A core flower                    # Monitoring (if installed)
```

## Testing

Run the test suite:

```bash
python manage.py test
```

For specific app:

```bash
python manage.py test apps.brain
```

## Deployment

### Production Checklist

1. Set `DEBUG=False` in production
2. Configure proper `SECRET_KEY`
3. Set up PostgreSQL database
4. Configure static files serving
5. Set up Redis for Celery
6. Configure logging tokens
7. Set proper `ALLOWED_HOSTS`

### Docker Support

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the coding standards
4. Add tests for new features
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the CLAUDE.md file for development guidelines
- Review Django documentation
- Check Unfold admin documentation