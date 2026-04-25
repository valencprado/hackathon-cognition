"""Multi-tenant middleware — resolves the current tenant from the request.

Tenant resolution order:
1. ``X-Tenant`` header (useful for API / admin calls).
2. Subdomain of the ``Host`` header (e.g., ``anhembi.our-library.com`` -> ``anhembi``).
3. ``tenant`` query parameter (fallback for local development).

The resolved tenant slug is stored on ``flask.g.tenant`` and can be accessed
by any endpoint that needs it.
"""

from __future__ import annotations

from flask import Flask, g, request


def tenant_middleware(app: Flask) -> None:
    """Register a ``before_request`` hook that resolves the current tenant."""

    @app.before_request
    def _resolve_tenant() -> None:
        # 1. Explicit header
        tenant = request.headers.get("X-Tenant", "").strip()

        # 2. Subdomain
        if not tenant:
            host = request.host.split(":")[0]  # drop port
            parts = host.split(".")
            if len(parts) >= 3:
                tenant = parts[0]

        # 3. Query parameter fallback
        if not tenant:
            tenant = request.args.get("tenant", "").strip()

        g.tenant = tenant or None
