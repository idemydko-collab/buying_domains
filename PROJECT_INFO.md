# Test Project - Technical Information

## Project Metadata

- **Project Name**: test-project
- **Django Version**: 5.0+
- **Python Version**: 3.12+
- **Created**: 2024
- **Architecture**: Modern Django with Apps-based structure

## Technology Stack

### Backend
- **Django 5.0** - Web framework
- **Unfold** - Modern admin interface
- **Celery** - Background task processing
- **Redis** - Message broker for Celery
- **SQLite/PostgreSQL** - Database options

### Frontend
- **Tailwind CSS** - Utility-first CSS framework
- **HTML5** - Semantic markup
- **Responsive Design** - Mobile-first approach

### Development Tools
- **Debug Toolbar** - Development debugging
- **BetterStack** - Production logging
- **Python Decouple** - Environment management

## Architecture Decisions

### 1. Apps-based Structure
```
apps/
└── brain/  # Example app demonstrating patterns
```
- Scalable application organization
- Clear separation of concerns
- Easy to add new features

### 2. Environment-based Configuration
- SQLite for development simplicity
- PostgreSQL for production scalability
- Environment flags for feature toggling

### 3. Celery Integration
- Optional async processing via USE_CELERY flag
- Graceful degradation to synchronous execution
- Task scheduling through Django admin

### 4. Logging Strategy
- BetterStack integration for production
- Console logging for development
- Custom Logger class for consistent usage

### 5. Admin Interface
- Unfold for modern, professional appearance
- Custom navigation structure
- Permission-based access control

## Development Patterns

### Model Design
```python
class ExampleModel(models.Model):
    # Standard fields with proper relationships
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
```

### Task Design
```python
@shared_task
@use_celery
def example_task():
    Logger("Task started", "info")
    # Task logic
    Logger("Task completed", "info")
```

### View Design
```python
class ExampleListView(ListView):
    model = ExampleModel
    template_name = 'brain/example_list.html'
    context_object_name = 'examples'
    paginate_by = 10
```

## Configuration Management

### Environment Variables
- **Core Django**: SECRET_KEY, DEBUG, ALLOWED_HOSTS
- **Database**: USE_SQLITE, DATABASE_URL
- **Celery**: USE_CELERY, CELERY_BROKER_URL
- **Logging**: LOGTAIL_SOURCE_TOKEN, LOGTAIL_HOST

### Feature Flags
- `USE_SQLITE`: Database backend selection
- `USE_CELERY`: Task execution mode
- `DEBUG`: Development vs production behavior

## Security Considerations

### Implemented
- CSRF protection enabled
- Secure secret key generation
- Environment-based configuration
- Permission-based admin access

### Recommendations
- Use HTTPS in production
- Configure proper ALLOWED_HOSTS
- Implement rate limiting
- Regular dependency updates

## Performance Optimizations

### Database
- Proper indexing on frequent queries
- Select_related for foreign keys
- Pagination for large datasets

### Celery
- Task result expiration
- Proper error handling
- Resource cleanup

### Static Files
- Collectstatic for production
- CDN integration recommended

## Monitoring & Logging

### BetterStack Integration
- Structured logging with extra context
- Error tracking and alerting
- Performance monitoring

### Development Debugging
- Django Debug Toolbar
- Console logging output
- Detailed error pages

## Testing Strategy

### Included Tests
- Model creation and validation
- String representations
- Basic functionality

### Testing Guidelines
- Unit tests for models
- Integration tests for views
- Task testing with mocks

## Deployment Considerations

### Production Checklist
- [ ] Set DEBUG=False
- [ ] Configure production database
- [ ] Set up Redis for Celery
- [ ] Configure static file serving
- [ ] Set up logging tokens
- [ ] Configure domain/SSL

### Scaling Options
- Horizontal scaling with load balancers
- Database read replicas
- Celery worker scaling
- Redis cluster for high availability

## Maintenance

### Regular Tasks
- Dependency updates
- Log rotation
- Database maintenance
- Performance monitoring

### Backup Strategy
- Database backups
- Media file backups
- Configuration backups

## Documentation

- **CLAUDE.md**: Development guidelines for Claude Code
- **README.md**: Project overview and setup
- **PROJECT_INFO.md**: This technical documentation
- Inline code comments for complex logic