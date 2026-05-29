"""OpenTelemetry configuration helper with lazy imports."""

from __future__ import annotations

import os


def configure_opentelemetry(service_name: str) -> None:
    """Configure OpenTelemetry tracing when dependencies are installed.

    Required optional packages:
    - opentelemetry-sdk
    - opentelemetry-exporter-otlp
    - opentelemetry-instrumentation-fastapi
    """
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError as exc:
        raise RuntimeError("Install OpenTelemetry SDK/exporter packages to enable tracing") from exc

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)


def instrument_fastapi(app) -> None:
    """Instrument a FastAPI app when OpenTelemetry dependencies are installed."""
    if not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    except ImportError as exc:
        raise RuntimeError("Install opentelemetry-instrumentation-fastapi to instrument FastAPI") from exc
    FastAPIInstrumentor.instrument_app(app)
