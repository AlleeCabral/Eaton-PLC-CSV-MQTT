import logging
from datetime import datetime, timezone

import azure.functions as func

try:
    from src.modules import cleanup_cycles as cleanup_cycles_module
    from src.modules.process_cycle import process_cycle_work_item
    from src.modules.schedule_cycle import schedule_completed_cycle
    from src.modules.orchestrator import ACTIVE_STATUSES, plan_cycle, run_cycle_pipeline
    from src.shared.config import validate_required_env
    from src.shared.cycle_message import CycleWorkItem
    from src.shared.dependency_factory import build_runtime_context, build_storage_repo
    from src.shared.observability import build_log_envelope, log_cycle_alert
except ModuleNotFoundError:
    from modules import cleanup_cycles as cleanup_cycles_module
    from modules.process_cycle import process_cycle_work_item
    from modules.schedule_cycle import schedule_completed_cycle
    from modules.orchestrator import ACTIVE_STATUSES, plan_cycle, run_cycle_pipeline
    from shared.config import validate_required_env
    from shared.cycle_message import CycleWorkItem
    from shared.dependency_factory import build_runtime_context, build_storage_repo
    from shared.observability import build_log_envelope, log_cycle_alert

app = func.FunctionApp()


@app.timer_trigger(schedule="%CYCLE_SCHEDULE%", arg_name="timer", use_monitor=True)
@app.queue_output(
    arg_name="cycle_message",
    queue_name="%CYCLE_QUEUE_NAME%",
    connection="AzureWebJobsStorage",
)
def cycle_planner_timer(timer: func.TimerRequest, cycle_message: func.Out[str]) -> None:
    """Claim the last completed cycle and enqueue it for reliable processing."""
    run_id = datetime.now(timezone.utc).isoformat()
    try:
        config = validate_required_env()
        repo = build_storage_repo(config)
        result = schedule_completed_cycle(
            datetime.now(timezone.utc), config, repo, correlation_id=run_id
        )
        if result["message"] is not None:
            cycle_message.set(result["message"])
        logging.info("cycle_planner_timer completed", extra=build_log_envelope(
            "cycle_planner", result["cycleKey"], run_id, 1, result["status"]
        ) | {"pastDue": timer.past_due})
    except Exception:
        logging.exception("cycle_planner_timer failed", extra=build_log_envelope(
            "cycle_planner", "unknown", run_id, 1, "error"
        ))


@app.queue_trigger(
    arg_name="message",
    queue_name="%CYCLE_QUEUE_NAME%",
    connection="AzureWebJobsStorage",
)
def aggregation_cycle_worker(message: func.QueueMessage) -> None:
    """Process one queued aggregation cycle; failures propagate for queue retry."""
    item = CycleWorkItem.from_json(message.get_body().decode("utf-8"))
    run_id = item.correlationId
    try:
        config = validate_required_env()
        context = build_runtime_context(config)
        result = process_cycle_work_item(item, context, config)
        logging.info("aggregation_cycle_worker completed", extra=build_log_envelope(
            "aggregation_worker", item.cycleKey, run_id, message.dequeue_count, result["status"]
        ) | {
            "writebackMode": config["WRITEBACK_MODE"],
            "candidatePointCount": len(result.get("candidatePayload", {}).get("trends", [])),
        })
    except Exception:
        logging.exception("aggregation_cycle_worker failed", extra=build_log_envelope(
            "aggregation_worker", item.cycleKey, run_id, message.dequeue_count, "error"
        ))
        raise


@app.timer_trigger(schedule="0 0 */6 * * *", arg_name="timer")
def cleanup_cycles(timer: func.TimerRequest) -> None:
    """Every 6 hours: purge CycleStatus/CycleDataSnapshot rows past RETENTION_HOURS."""
    run_id = datetime.now(timezone.utc).isoformat()
    try:
        config = validate_required_env()
        repo = build_storage_repo(config)
        result = cleanup_cycles_module.run(datetime.now(timezone.utc), config, repo)
        logging.info("cleanup_cycles completed", extra=build_log_envelope(
            "cleanup_cycles", "n/a", run_id, 1, "completed"
        ) | {"deletedCounts": result["deletedCounts"]})
    except Exception:
        logging.exception("cleanup_cycles failed", extra=build_log_envelope(
            "cleanup_cycles", "n/a", run_id, 1, "error"
        ))
