from django.conf import settings
 
def base(request):
    return {
        'TITLE': settings.TITLE,
    }
