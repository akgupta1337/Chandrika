from googleapiclient.errors import HttpError

from datetime import datetime


def sort_tasks(tasks):
    """
    Sort tasks: unfinished ones (by due date) first, completed ones last.
    Tasks without due dates go to the bottom of their respective groups.
    """

    def task_sort_key(task):
        is_completed = task.get("status") == "completed"
        due_str = task.get("due")
        try:
            due_date = (
                datetime.fromisoformat(due_str.replace("Z", "")) if due_str else None
            )
        except:
            due_date = None
        return (is_completed, due_date or datetime.max)

    return sorted(tasks, key=task_sort_key)


def get_all_tasks_from_list(service, tasklist_id):
    """Fetch all tasks from a specific task list."""
    try:
        results = (
            service.tasks()
            .list(
                tasklist=tasklist_id,
                maxResults=100,  # Adjust as needed
                showCompleted=True,  # Include completed tasks
                showDeleted=False,  # Exclude deleted tasks
                showHidden=True,  # Include hidden tasks
            )
            .execute()
        )
        return results.get("items", [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


def get_all_task_lists(service):
    """Fetch all task lists."""
    try:
        results = service.tasklists().list().execute()
        return results.get("items", [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


import os

DATE_FILE = "current_date.txt"


def fetch_all_tasks(service):
    task_lists = get_all_task_lists(service)

    if not task_lists:
        print("No task lists found.")
        return

    all_tasks = []

    # Iterate through each task list
    for task_list in task_lists:
        list_id = task_list["id"]
        list_title = task_list["title"]

        # print(f"\nFetching tasks from: {list_title}")

        # Get all tasks from this list
        tasks = get_all_tasks_from_list(service, list_id)

        if tasks:
            for task in tasks:
                # Add task list info to each task
                task["taskListId"] = list_id
                task["taskListTitle"] = list_title
                all_tasks.append(task)

        #         # Print task details
        #         print(f"  - {task.get('title', 'Untitled')}")
        #         print(f"    Status: {task.get('status', 'Unknown')}")
        #         print(f"    Due: {task.get('due', 'No due date')}")
        #         print(f"    Notes: {task.get('notes', 'No notes')}")
        #         print()
        # else:
        #     print(f"  No tasks found in {list_title}")

    # print(f"\nTotal tasks found: {len(all_tasks)}")
    delete_old_completed_tasks_from_list(all_tasks, service)
    return sort_tasks(all_tasks)


from datetime import datetime, timezone


def delete_old_completed_tasks_from_list(tasks, service):
    today = datetime.now(timezone.utc).date()

    for task in tasks:
        if task.get("status") == "completed":
            due_str = task.get("due") or task.get("completed")
            if not due_str:
                continue

            due_date = datetime.fromisoformat(due_str.replace("Z", "+00:00")).date()
            if due_date < today:
                print(f"Deleting: {task['title']} (Date: {due_date})")
                service.tasks().delete(
                    tasklist=task["taskListId"], task=task["id"]
                ).execute()


from datetime import datetime, timedelta
import re

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def parse_date_string(date_str: str) -> str:
    date_str = (date_str or "today").strip().lower()
    today = datetime.utcnow().date()

    if date_str in ("", "today"):
        return today.strftime("%Y-%m-%d")
    elif date_str == "tomorrow":
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif date_str in WEEKDAYS:
        current_weekday = today.weekday()
        target_weekday = WEEKDAYS[date_str]
        days_ahead = (target_weekday - current_weekday + 7) % 7 or 7
        return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    elif re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return date_str
    else:
        raise ValueError("Invalid date format")


def parse_time_string(time_str: str) -> str:
    time_str = time_str.strip().lower()
    for fmt in ("%H:%M", "%I %p", "%I:%M %p"):
        try:
            return datetime.strptime(time_str, fmt).strftime("%H:%M")
        except ValueError:
            continue
    raise ValueError("Invalid time format")


def set_todo_and_reminder(service, arguments: dict):
    tasklist_id = "@default"
    task_name = arguments.get("task_name")
    time_str = arguments.get("time")

    if not task_name or not time_str:
        print("Missing required fields: 'task_name' and 'time'")
        return None

    try:
        # Use default "today" and "" if missing
        date_str = arguments.get("date", "today")
        description = arguments.get("description", "")

        due_date = parse_date_string(date_str)
        due_time = parse_time_string(time_str)
        due_rfc3339 = f"{due_date}T{due_time}:00.000Z"

        task_body = {
            "title": task_name,
            "due": due_rfc3339,
        }

        if description:
            task_body["notes"] = description

        result = service.tasks().insert(tasklist=tasklist_id, body=task_body).execute()
        print(f"Task '{task_name}' added successfully.")
        return result

    except (ValueError, HttpError) as e:
        print(f"Failed to add task: {e}")
        return None
