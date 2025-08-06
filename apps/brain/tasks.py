from celery import shared_task
from core.utils import use_celery
from core.logger import Logger
from .models import ExampleModel


@shared_task
@use_celery
def scheduled_cleanup_task():
    """Example scheduled task that runs periodically"""
    Logger("Starting scheduled cleanup task", "info")
    
    try:
        # Example: Delete old inactive examples (older than 30 days)
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count = ExampleModel.objects.filter(
            is_active=False,
            updated_at__lt=cutoff_date
        ).delete()[0]
        
        Logger(f"Cleanup task completed: deleted {deleted_count} old examples", "info")
        return f"Deleted {deleted_count} old examples"
        
    except Exception as e:
        Logger(f"Error in scheduled cleanup task: {str(e)}", "error")
        raise


@shared_task
@use_celery
def process_example_data(example_id, data):
    """Example on-demand task for processing data"""
    Logger(f"Starting data processing for example {example_id}", "info")
    
    try:
        example = ExampleModel.objects.get(id=example_id)
        
        # Example processing logic
        processed_data = {
            'original': data,
            'processed_at': timezone.now().isoformat(),
            'status': 'completed'
        }
        
        # Update the example with processed data
        example.description += f"\nProcessed: {processed_data['status']}"
        example.save()
        
        Logger(f"Data processing completed for example {example_id}", "info")
        return processed_data
        
    except ExampleModel.DoesNotExist:
        Logger(f"Example {example_id} not found", "error")
        raise
    except Exception as e:
        Logger(f"Error processing data for example {example_id}: {str(e)}", "error")
        raise


@shared_task
@use_celery
def generate_report():
    """Example task for generating reports"""
    Logger("Starting report generation", "info")
    
    try:
        active_count = ExampleModel.objects.filter(is_active=True).count()
        inactive_count = ExampleModel.objects.filter(is_active=False).count()
        
        report = {
            'active_examples': active_count,
            'inactive_examples': inactive_count,
            'total_examples': active_count + inactive_count,
            'generated_at': timezone.now().isoformat()
        }
        
        Logger(f"Report generation completed: {report}", "info")
        return report
        
    except Exception as e:
        Logger(f"Error generating report: {str(e)}", "error")
        raise