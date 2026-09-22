from benchmark_django_rest_framework import benchmark


benchmark(
    url="/api/my-models/",   # your DRF endpoint
    method="GET",            # HTTP method to test
    n=100                    # number of requests to simulate
)