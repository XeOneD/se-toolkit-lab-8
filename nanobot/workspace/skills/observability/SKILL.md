# Observability Skill

You have access to observability tools for querying logs and traces, plus cron tools for scheduling recurring tasks.

## Available Tools

### Log Tools (VictoriaLogs)

- **`logs_search`** — Search logs by keyword and/or time range.
  - Use when the user asks about errors, warnings, or specific events.
  - Parameters: `query` (LogsQL query), `limit` (max results), `time_range` (e.g., "1h", "24h").
  - Example: Search for errors in the backend: `query="_stream:{service=\"backend\"} AND level:error"`, `time_range="1h"`.

- **`logs_error_count`** — Count errors per service over a time window.
  - Use when the user asks "any errors?" or "how many errors?".
  - Parameters: `time_range` (e.g., "1h", "24h").
  - Returns: Count of errors grouped by service.

### Trace Tools (VictoriaTraces)

- **`traces_list`** — List recent traces for a service.
  - Use when the user asks about request flows or performance.
  - Parameters: `service` (service name), `limit` (max traces), `time_range` (e.g., "1h").
  - Returns: List of trace IDs with metadata.

- **`traces_get`** — Fetch a specific trace by ID.
  - Use when you need to inspect a specific request flow.
  - Parameters: `trace_id` (trace identifier).
  - Returns: Full trace with span hierarchy and timing.

### Cron Tools

- **`cron_list`** — List all scheduled cron jobs.
  - Use when the user asks "List scheduled jobs" or "What cron tasks do you have?".
  - No parameters required.
  - Returns: List of jobs with name, schedule, prompt, and status.

- **`cron_create`** — Create a new cron job.
  - Use when the user asks to create a scheduled task or health check.
  - Parameters:
    - `name`: Unique name for the job (e.g., "health-check")
    - `schedule`: Cron expression (e.g., "*/2 * * * *" for every 2 minutes)
    - `prompt`: The prompt to run on each schedule
    - `chat_id`: Chat session ID (default: "default")
  - Example: Create a health check every 2 minutes:
    - name: "health-check"
    - schedule: "*/2 * * * *"
    - prompt: "Check for backend errors in the last 2 minutes and post a summary"

- **`cron_remove`** — Remove a cron job.
  - Use when the user asks to cancel or remove a scheduled task.
  - Parameters: `name` (job name to remove).

## Usage Strategy

### When asked "What went wrong?" or "Check system health":

1. **First**, call `logs_error_count` with `time_range="5m"` to check for recent errors.
2. **If errors exist**, call `logs_search` with `query="level:error"`, `time_range="5m"`, `limit=10`.
3. **Look for trace IDs** in the log results (fields like `trace_id` or `traceId`).
4. **If a trace ID is found**, call `traces_get` with that `trace_id` to inspect the full trace.
5. **Summarize findings** concisely:
   - What error occurred
   - Which service was affected
   - What the trace shows (if available)
   - Suggested next steps

### When asked about errors (e.g., "Any errors in the last hour?"):

1. Call `logs_error_count` with `time_range="1h"` to get a summary.
2. If errors > 0, call `logs_search` to get details.
3. If logs mention a trace ID, call `traces_get` to fetch the full trace.
4. Summarize findings concisely — don't dump raw JSON.

### When asked to create a scheduled health check:

1. Understand the requested interval (e.g., "every 2 minutes" → cron expression `*/2 * * * *`).
2. Define what the health check should do:
   - Check for recent errors using `logs_error_count` with matching time range
   - If errors found, search logs and inspect traces
   - Post a summary to the chat
3. Call `cron_create` with:
   - `name`: "health-check"
   - `schedule`: "*/2 * * * *" (or as requested)
   - `prompt`: "Check for backend errors in the last 2 minutes, inspect traces if found, and post a short summary. If no errors, say the system looks healthy."
4. Confirm the job was created and explain when it will run next.

### When asked to list scheduled jobs:

1. Call `cron_list` (no parameters).
2. Report the results to the user:
   - Job names
   - Schedules
   - Status (enabled/disabled)

### When asked to remove a scheduled job:

1. Call `cron_remove` with the job `name`.
2. Confirm the job was removed.

## Example Interactions

**User:** "What went wrong?"

**You:**
1. Call `logs_error_count` with `time_range="5m"`.
2. If errors > 0, call `logs_search` with `query="level:error"`, `time_range="5m"`.
3. Extract any trace IDs from logs.
4. Call `traces_get` for each trace ID found.
5. Summarize: "The backend encountered database connection errors 3 times in the last 5 minutes. The trace shows requests failing at the database layer with 'connection refused'. PostgreSQL may be unavailable."

**User:** "Any errors in the last hour?"

**You:**
1. Call `logs_error_count` with `time_range="1h"`.
2. If errors > 0, call `logs_search` with `query="level:error"`, `time_range="1h"`.
3. Summarize: "Found X errors in the last hour. The backend service had Y connection errors to PostgreSQL at [time]."

**User:** "Create a health check that runs every 2 minutes"

**You:**
1. Call `cron_create` with:
   - `name`: "health-check"
   - `schedule`: "*/2 * * * *"
   - `prompt`: "Check for backend errors in the last 2 minutes, inspect traces if found, and post a short summary. If no errors, say the system looks healthy."
2. Confirm: "I've created a health check named 'health-check' that runs every 2 minutes. It will check for backend errors and post updates here."

**User:** "List scheduled jobs"

**You:**
1. Call `cron_list`.
2. Report: "You have 1 scheduled job: 'health-check' running every 2 minutes (*/2 * * * *). Next run at [time]."

**User:** "Remove the health check"

**You:**
1. Call `cron_remove` with `name`: "health-check".
2. Confirm: "The 'health-check' job has been removed."

## Notes

- Time ranges: Use "1h" for last hour, "24h" for last day, "7d" for last week, "5m" for last 5 minutes.
- LogsQL syntax: `_stream:{service="backend"} AND level:error` filters by service and level.
- Always summarize findings in plain language — users don't want raw JSON.
- When creating cron jobs, ensure the time range in the health check matches the cron interval.
- Cron jobs are tied to the chat session via `chat_id`.
