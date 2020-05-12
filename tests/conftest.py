def pytest_configure(config):
    from django.conf import settings

    if not settings.configured:
        settings.configure()
