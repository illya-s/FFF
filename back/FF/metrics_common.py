from prometheus_client import Counter, Gauge

class Metrics:
    media_visits = Counter('media_visits', 'total number of media visits')