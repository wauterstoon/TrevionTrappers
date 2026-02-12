from django.db import connection
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import render
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from django.db.migrations.executor import MigrationExecutor


class PendingMigrationsMiddleware(MiddlewareMixin):
    """Show a friendly instruction page when DB migrations are pending."""

    cache_key = '_pending_migrations'

    def _has_pending_migrations(self):
        if hasattr(connection, self.cache_key):
            return getattr(connection, self.cache_key)

        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        has_pending = bool(executor.migration_plan(targets))
        setattr(connection, self.cache_key, has_pending)
        return has_pending

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            current_url = resolve(request.path_info)
            if current_url.url_name in {'admin:index'}:
                return None
        except Exception:
            pass

        try:
            if self._has_pending_migrations():
                return render(request, 'pending_migrations.html', status=503)
        except (OperationalError, ProgrammingError):
            return render(request, 'pending_migrations.html', status=503)

        return None
