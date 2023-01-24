from django.http import HttpRequest


def get_client_ip(request: HttpRequest) -> str:
    """ Give it a Django request, it gives you the client's IP as string. """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def fake_func():
    a = "hello"
    return a
