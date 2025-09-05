from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView
from django.contrib import messages
from .models import ExampleModel, Domain
from .services import DomainPurchaseService, AdmToolsService
from .tasks import process_domain_batch
from core.logger import Logger


def home(request):
    """Home view with domain purchase form"""
    Logger(f"Home view accessed with method: {request.method}", "info")
    
    # Get balance from adm.tools
    adm_service = AdmToolsService()
    balance = adm_service.get_balance()
    
    if request.method == 'POST':
        Logger("POST request detected", "info")
        try:
            # Get domain mode
            domain_mode = request.POST.get('domainMode', 'random')
            Logger(f"Domain mode: {domain_mode}", "info")
            
            purchase_service = DomainPurchaseService()
            
            if domain_mode == 'custom':
                # Handle custom domain names
                custom_zone = request.POST.get('custom_domain_zone', '.space')
                
                # Collect all custom domain names from form
                custom_domains = []
                for key, value in request.POST.items():
                    if key.startswith('custom_domain_') and value.strip():
                        custom_domains.append(value.strip())
                
                if not custom_domains:
                    messages.error(request, 'Вкажіть хоча б одну назву домену')
                    return render(request, 'brain/home.html', {'balance': balance})
                
                Logger(f"Custom domain purchase request: {len(custom_domains)} domains {custom_domains} with zone {custom_zone}", "info")
                
                messages.info(
                    request,
                    f'Розпочато обробку {len(custom_domains)} власних доменів. Слідкуйте за прогресом у Telegram каналі.'
                )
                
                # Process custom domains in background thread
                import threading
                thread = threading.Thread(
                    target=purchase_service.purchase_custom_domains,
                    args=(custom_domains, custom_zone)
                )
                thread.start()
                
                Logger(f"Started custom domain processing in background thread", "info")
                
            else:
                # Handle random domain generation
                domain_count = int(request.POST.get('domain_count', 1))
                domain_zone = request.POST.get('domain_zone', '.space')
                
                Logger(f"Random domain purchase request: {domain_count} domains with zone {domain_zone}", "info")
                
                if domain_count < 1 or domain_count > 100:
                    messages.error(request, 'Кількість доменів повинна бути від 1 до 100')
                    return render(request, 'brain/home.html', {'balance': balance})
                
                messages.info(
                    request,
                    f'Розпочато обробку {domain_count} випадкових доменів. Слідкуйте за прогресом у Telegram каналі.'
                )
                
                # Process random domains in background thread
                import threading
                thread = threading.Thread(
                    target=purchase_service.purchase_domains,
                    args=(domain_count, domain_zone)
                )
                thread.start()
                
                Logger(f"Started random domain processing in background thread", "info")
            
            # For AJAX requests, return simple success response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponse('OK')
            
        except ValueError:
            error_msg = 'Невірна кількість доменів'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponse(error_msg, status=400)
            messages.error(request, error_msg)
        except Exception as e:
            error_msg = 'Виникла помилка при купівлі доменів'
            Logger(f"Error in domain purchase: {str(e)}", "error")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponse(error_msg, status=500)
            messages.error(request, error_msg)
    else:
        Logger("GET request - showing form", "info")
    
    context = {
        'balance': balance
    }
    
    return render(request, 'brain/home.html', context)


class ExampleListView(ListView):
    model = ExampleModel
    template_name = 'brain/example_list.html'
    context_object_name = 'examples'
    paginate_by = 10

    def get_queryset(self):
        Logger("Example list accessed", "info")
        return ExampleModel.objects.filter(is_active=True)


def api_examples(request):
    """Simple API endpoint for examples"""
    examples = ExampleModel.objects.filter(is_active=True).values(
        'id', 'title', 'description', 'created_at'
    )
    Logger(f"API examples accessed, returning {len(examples)} examples", "info")
    return JsonResponse(list(examples), safe=False)