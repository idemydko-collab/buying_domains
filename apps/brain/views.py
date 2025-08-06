from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import ListView
from .models import ExampleModel
from core.logger import Logger


def home(request):
    """Simple home view"""
    Logger("Home page accessed", "info")
    return render(request, 'brain/home.html')


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