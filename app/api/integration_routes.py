"""Integration REST helpers: cached score, on-demand analytics flush, health."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.core.redis import get_redis, ping_redis
from app.core.security import AuthenticatedPrincipal, get_current_principal
from app.services.integration.metrics import metrics_output
from app.services.integration.runtime import get_consumer, get_producer, get_ws_manager
from app.services.integration.score_cache import ScoreCache

router = APIRouter(prefix="/api/v1/integration", tags=["Integration"])


@router.get("/health")
async def integration_health() -> dict:
    redis_ok = await ping_redis()
    kafka_producer = False
    kafka_consumer = False
    ws_connections = 0
    try:
        kafka_producer = get_producer().ready
    except RuntimeError:
        pass
    try:
        kafka_consumer = get_consumer().ready
    except RuntimeError:
        pass
    try:
        ws_connections = get_ws_manager().local_connection_count()
    except RuntimeError:
        pass

    status_value = "healthy" if redis_ok else "degraded"
    if not kafka_producer or not kafka_consumer:
        status_value = "degraded"

    return {
        "status": status_value,
        "redis": redis_ok,
        "kafka_producer": kafka_producer,
        "kafka_consumer": kafka_consumer,
        "websocket_local_connections": ws_connections,
    }


@router.get("/score/{tenant_id}")
async def get_cached_score(
    tenant_id: str,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
) -> dict:
    if principal.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant scope mismatch",
        )
    redis = await get_redis()
    cached = await ScoreCache(redis).get(tenant_id)
    if cached is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not cached for tenant",
        )
    return cached


@router.post("/analytics/flush/{tenant_id}")
async def flush_analytics(
    tenant_id: str,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
) -> dict:
    if principal.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant scope mismatch",
        )
    from app.services.integration.analytics_pipeline import AnalyticsPipeline

    pipeline = AnalyticsPipeline(get_producer())
    report = await pipeline.flush_tenant(tenant_id, report_kind="on_demand")
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics flush failed",
        )
    return report.model_dump(mode="json")


@router.get("/metrics")
async def prometheus_metrics() -> Response:
    return Response(content=metrics_output(), media_type="text/plain")
