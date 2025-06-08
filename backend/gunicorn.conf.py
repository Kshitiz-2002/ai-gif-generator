import os
import multiprocessing

bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"  # Render sets the PORT env variable

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 2

timeout = 300
graceful_timeout = 30

accesslog = "-"
errorlog = "-"
loglevel = "info"

preload_app = True
max_requests = 1000
max_requests_jitter = 50
