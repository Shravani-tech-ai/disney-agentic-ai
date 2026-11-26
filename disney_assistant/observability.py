
import time
import uuid
import threading
from contextvars import ContextVar
from functools import wraps
import math

MAX_TRACES = 200

_current_trace_id = ContextVar("current_trace_id", default=None)

_traces = {}
_trace_lock = threading.RLock()


def create_trace(user_message, session_id):
    trace_id = str(uuid.uuid4())

    trace = {
        "trace_id": trace_id,
        "session_id": session_id,
        "user_message": user_message,
        "status": "RUNNING",
        "started_at": time.time(),
        "completed_at": None,
        "latency_ms": None,
        "events": [],
        "selected_agents": [],
        "tool_calls": 0,
        "model_calls": None,
        "input_tokens": None,
        "output_tokens": None,
        "error": None,
    }

    with _trace_lock:
        _traces[trace_id] = trace

        while len(_traces) > MAX_TRACES:
            oldest_id = next(iter(_traces))
            del _traces[oldest_id]

    _current_trace_id.set(trace_id)

    return trace_id


def record_event(event_type, name, details=None, duration_ms=None):
    trace_id = _current_trace_id.get()

    if not trace_id:
        return

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "name": name,
        "details": details or {},
        "duration_ms": duration_ms,
        "timestamp": time.time(),
    }

    with _trace_lock:
        trace = _traces.get(trace_id)

        if trace:
            trace["events"].append(event)

            if event_type == "AGENT":
                if name not in trace["selected_agents"]:
                    trace["selected_agents"].append(name)

            elif event_type == "TOOL":
                trace["tool_calls"] += 1


def finish_trace(status="SUCCESS", error=None):
    trace_id = _current_trace_id.get()

    if not trace_id:
        return

    completed_at = time.time()

    with _trace_lock:
        trace = _traces.get(trace_id)

        if trace:
            trace["completed_at"] = completed_at
            trace["latency_ms"] = round(
                (completed_at - trace["started_at"]) * 1000,
                2
            )
            trace["status"] = status
            trace["error"] = error

    _current_trace_id.set(None)


def get_trace(trace_id):
    with _trace_lock:
        trace = _traces.get(trace_id)

        if trace:
            return dict(trace)

    return None


def list_traces():
    with _trace_lock:
        return [
            dict(trace)
            for trace in reversed(list(_traces.values()))
        ]


def get_metrics():
    with _trace_lock:
        traces = list(_traces.values())

    completed = [
        t for t in traces
        if t["latency_ms"] is not None
    ]

    latencies = sorted(
        t["latency_ms"] for t in completed
    )

    total = len(traces)
    successful = sum(
        1 for t in completed if t["status"] == "SUCCESS"
    )
    failed = sum(
        1 for t in completed if t["status"] == "ERROR"
    )

    average_latency = (
        round(sum(latencies) / len(latencies), 2)
        if latencies else 0
    )

    p95_index = (
        max(0, math.ceil(len(latencies) * 0.95) - 1)
        if latencies else 0
    )

    p95_latency = (
        latencies[p95_index] if latencies else 0
    )

    return {
        "total_traces": total,
        "successful_traces": successful,
        "failed_traces": failed,
        "average_latency_ms": average_latency,
        "p95_latency_ms": p95_latency,
        "success_rate": round(
            successful / len(completed) * 100, 2
        ) if completed else 0,
        "error_rate": round(
            failed / len(completed) * 100, 2
        ) if completed else 0,
        "total_tool_calls": sum(
            t["tool_calls"] for t in traces
        ),
        "total_model_calls": None,
        "total_tokens": None,
    }


def trace_tool(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        try:
            result = func(*args, **kwargs)

            duration = round(
                (time.perf_counter() - start) * 1000,
                2
            )

            record_event(
                "TOOL",
                func.__name__,
                {"status": "SUCCESS"},
                duration
            )

            return result

        except Exception as exc:
            duration = round(
                (time.perf_counter() - start) * 1000,
                2
            )

            record_event(
                "TOOL",
                func.__name__,
                {
                    "status": "ERROR",
                    "error": str(exc)
                },
                duration
            )

            raise

    return wrapper
