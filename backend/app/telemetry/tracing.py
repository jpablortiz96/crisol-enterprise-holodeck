from contextlib import contextmanager
from typing import Iterator


_TRACER = None


def initialize_tracing(service_name: str = "crisol-backend") -> bool:
    global _TRACER
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)
        _TRACER = trace.get_tracer(service_name)
    except Exception:
        return False
    return True


@contextmanager
def trace_span(name: str) -> Iterator[None]:
    if _TRACER is None:
        yield
        return
    with _TRACER.start_as_current_span(name):
        yield
