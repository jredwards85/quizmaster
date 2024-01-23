from .models import ShowcaseQuiz

def showcase_context(request):
    
    showcase_data = ShowcaseQuiz.objects.all().first()
    showcase_status = False

    if showcase_data:
        showcase_status = True

    return {
        'showcase_data': showcase_data,
        'showcase_status': showcase_status,
    }