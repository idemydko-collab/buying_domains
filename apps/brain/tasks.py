from celery import shared_task
from core.utils import use_celery
from core.logger import Logger
from .models import ExampleModel, Domain
from .services import DomainNameGenerator, CloudFlareService, AdmToolsService, KeitaroService, TelegramService
import time
from django.utils import timezone
from datetime import timedelta


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


@shared_task
@use_celery
def process_domain_batch(count, zone):
    """Process batch of domains asynchronously"""
    telegram = TelegramService()
    
    try:
        Logger(f"Starting async domain batch processing: {count} domains with zone {zone}", "info")
        
        # Generate unique domains
        domains = DomainNameGenerator.generate_unique_domains(zone, count)
        
        if not domains:
            telegram.notify_domain_generation([], False)
            return {"success": False, "error": "Failed to generate unique domains"}
        
        telegram.notify_domain_generation(domains, True)
        
        # Create individual tasks for each domain
        for domain_name in domains:
            process_single_domain.delay(domain_name, zone)
        
        Logger(f"Created {len(domains)} async domain processing tasks", "info")
        return {"success": True, "domains_queued": len(domains)}
        
    except Exception as e:
        Logger(f"Error in domain batch processing: {str(e)}", "error")
        telegram.send_message(f"❌ <b>Критична помилка батча</b>\n{str(e)}")
        return {"success": False, "error": str(e)}


@shared_task
@use_celery
def process_single_domain(domain_name, zone):
    """Process single domain with NS retry logic"""
    telegram = TelegramService()
    cf_service = CloudFlareService()
    adm_tools = AdmToolsService()
    
    try:
        Logger(f"Starting async processing for domain: {domain_name}", "info")
        
        # Step 1: Create CloudFlare zone
        zone_id = cf_service.create_zone(domain_name)
        if not zone_id:
            telegram.notify_cloudflare_zone(domain_name, False, "Failed to create zone")
            return {"domain": domain_name, "success": False, "error": "CloudFlare zone creation failed"}
        
        telegram.notify_cloudflare_zone(domain_name, True)
        
        # Step 2: Setup DNS
        if not cf_service.delete_all_dns_records(zone_id):
            telegram.notify_dns_setup(domain_name, False, "Failed to delete existing records")
            return {"domain": domain_name, "success": False, "error": "DNS cleanup failed"}
        
        if not cf_service.create_dns_record(zone_id, domain_name):
            telegram.notify_dns_setup(domain_name, False, "Failed to create A record")
            return {"domain": domain_name, "success": False, "error": "DNS record creation failed"}
        
        telegram.notify_dns_setup(domain_name, True)
        
        # Step 3: Get nameservers
        nameservers = cf_service.get_nameservers(zone_id)
        if not nameservers:
            return {"domain": domain_name, "success": False, "error": "Failed to get nameservers"}
        
        # Step 4: Purchase domain
        domain_id = adm_tools.purchase_domain(domain_name)
        if not domain_id:
            telegram.notify_domain_purchase(domain_name, False, "Purchase failed")
            return {"domain": domain_name, "success": False, "error": "Domain purchase failed"}
        
        telegram.notify_domain_purchase(domain_name, True)
        
        # Create domain record with pending NS status
        domain_obj = Domain.objects.create(
            name=domain_name,
            zone=zone,
            cloudflare_account_email=cf_service.account["email"],
            cloudflare_zone_id=zone_id,
            registrar_domain_id=domain_id,
            status='ns_pending'
        )
        
        # Step 5: Queue NS update task with retry logic
        update_domain_nameservers.delay(domain_obj.id, nameservers)
        
        Logger(f"Domain {domain_name} purchased, NS update queued", "info")
        return {"domain": domain_name, "success": True, "status": "ns_pending"}
        
    except Exception as e:
        Logger(f"Error processing domain {domain_name}: {str(e)}", "error")
        telegram.send_message(f"❌ <b>Критична помилка</b>\n<code>{domain_name}</code>\n{str(e)}")
        return {"domain": domain_name, "success": False, "error": str(e)}


@shared_task
@use_celery
def update_domain_nameservers(domain_id, nameservers):
    """Update domain nameservers with retry logic (15 min timeout)"""
    telegram = TelegramService()
    adm_tools = AdmToolsService()
    
    try:
        domain_obj = Domain.objects.get(id=domain_id)
        domain_name = domain_obj.name
        
        Logger(f"Starting NS update task for {domain_name}", "info")
        
        # Retry logic: 15 minutes total (30 attempts with 30s intervals)
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            Logger(f"NS update attempt {attempt}/{max_attempts} for {domain_name}", "info")
            
            if adm_tools.update_nameservers(domain_name, nameservers):
                # Success - complete domain setup
                telegram.notify_nameserver_update(domain_name, True)
                
                # Add to Keitaro
                keitaro_service = KeitaroService()
                keitaro_success = keitaro_service.add_domain(domain_name, domain_obj.cloudflare_account_email)
                
                if keitaro_success:
                    telegram.notify_keitaro_addition(domain_name, True)
                else:
                    telegram.notify_keitaro_addition(domain_name, False, "Failed to add to Keitaro")
                
                # Update domain status
                domain_obj.keitaro_added = keitaro_success
                domain_obj.status = 'completed'
                domain_obj.save()
                
                Logger(f"Domain {domain_name} fully completed", "info")
                return {"domain": domain_name, "success": True}
            
            # Wait 30 seconds before next attempt
            if attempt < max_attempts:
                time.sleep(30)
        
        # Timeout reached
        telegram.notify_nameserver_update(domain_name, False, f"Timeout after 15 minutes ({max_attempts} attempts)")
        domain_obj.status = 'ns_failed'
        domain_obj.save()
        
        Logger(f"NS update timeout for {domain_name} after 15 minutes", "error")
        return {"domain": domain_name, "success": False, "error": "NS update timeout"}
        
    except Domain.DoesNotExist:
        Logger(f"Domain with ID {domain_id} not found", "error")
        return {"success": False, "error": "Domain not found"}
    except Exception as e:
        Logger(f"Error in NS update task for domain ID {domain_id}: {str(e)}", "error")
        return {"success": False, "error": str(e)}