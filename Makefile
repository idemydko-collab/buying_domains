# Django Test Project Makefile

.PHONY: help install migrate run test clean celery beat

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install --upgrade pip
	pip install -r requirements.txt

migrate:  ## Run database migrations
	python manage.py migrate

makemigrations:  ## Create new migrations
	python manage.py makemigrations

run:  ## Start Django development server
	python manage.py runserver

test:  ## Run tests
	python manage.py test

celery:  ## Start Celery worker
	celery -A core worker --loglevel=info

beat:  ## Start Celery Beat scheduler
	celery -A core beat --loglevel=info

shell:  ## Open Django shell
	python manage.py shell

superuser:  ## Create superuser
	python manage.py createsuperuser

collectstatic:  ## Collect static files
	python manage.py collectstatic --noinput

clean:  ## Clean cache and temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/

setup:  ## Complete project setup
	$(MAKE) install
	$(MAKE) migrate
	@echo "Setup complete! Run 'make run' to start the server"

dev-setup:  ## Development setup with superuser
	$(MAKE) setup
	@echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
	@echo "Development setup complete! Login: admin/admin123"

check:  ## Run Django checks
	python manage.py check

showmigrations:  ## Show migration status
	python manage.py showmigrations

dbshell:  ## Open database shell
	python manage.py dbshell