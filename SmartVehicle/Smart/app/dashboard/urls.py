from django.urls import path

from .dashboard_views import dashboard_stats
from .stats_views import recent_logs

urlpatterns = [

    path("stats/", dashboard_stats),

    path("recent-logs/", recent_logs),
]