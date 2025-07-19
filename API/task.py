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
