from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (
            request.user.is_authenticated
            and not request.user.profile == 4
            and request.path != reverse('setup')
            and not request.path.startswith('/media/')
        ):
            return redirect('setup')

        return response