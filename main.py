from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from API import utils, task, news, weather, sysinfo, wiki, arch3b
import uvicorn
import requests
import os
from datetime import datetime
from fastapi.responses import JSONResponse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from fastapi import Request, HTTPException

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_SECRETS_FILE = "client_secrets.json"
REDIRECT_URI = "http://localhost:8000/auth/callback"
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]


app = FastAPI()

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up template directory
templates = Jinja2Templates(directory="templates")


@app.get("/api/greeting")
async def get_greeting(request: Request):
    user = request.cookies.get("user")
    # Get current hour
    hour = datetime.now().hour
    if 4 <= hour < 6:
        greeting = "Early Morning"
        icon = "fas fa-cloud-sun"
    elif 6 <= hour < 12:
        greeting = "Good Morning"
        icon = "fas fa-sun"
    elif 12 <= hour < 15:
        greeting = "Good Afternoon"
        icon = "fas fa-cloud"
    elif 15 <= hour < 18:
        greeting = "Good Evening"
        icon = "fas fa-cloud-sun-rain"
    elif 18 <= hour < 21:
        greeting = "Good Night"
        icon = "fas fa-moon"
    elif 21 <= hour < 24:
        greeting = "Late Night"
        icon = "fas fa-star-and-crescent"
    else:  # 0 <= hour < 4
        greeting = "Midnight Greetings"
        icon = "fas fa-bed"

    return {"user": user, "greeting": greeting, "greeting_icon": icon}


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    user = request.cookies.get("user")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user},
    )


@app.get("/login")
def login():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )
    return RedirectResponse(auth_url)


@app.get("/auth/callback")
def auth_callback(request: Request):
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
    )

    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {credentials.token}"})
    response = session.get("https://openidconnect.googleapis.com/v1/userinfo")

    user_info = response.json()
    print("USERINFO STATUS:", response.status_code)
    print("USERINFO RESPONSE:", response.text)

    email = user_info["email"]
    google_id = user_info["sub"]
    name = user_info["given_name"]

    utils.store_user(
        email, google_id, name, credentials.token, credentials.refresh_token
    )

    response = RedirectResponse(url="/")

    # Secure backend ID
    response.set_cookie(
        key="google_id",
        value=google_id,
        max_age=86400,
    )

    # Public display name
    response.set_cookie(
        key="user",
        value=name,
        max_age=86400,
    )

    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("user")
    return response


@app.get("/api/weather")
def get_weather(day: int = 1):
    data = weather.get_weather_data(day)
    return JSONResponse(content=data)


@app.get("/api/weather_summary")
def get_weather_summary(day: int = 1):
    data = weather.get_weather_data(day)
    data_str = ", ".join(f"{k}: {v}" for k, v in data.items())

    summary = arch3b.get_summary(data_str, "Summarize these weather details")
    return JSONResponse(content=summary)


@app.get("/api/tasks")
def get_tasks(request: Request):
    google_id = request.cookies.get("google_id")
    if not google_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = utils.get_user_by_google_id(google_id)

    creds = utils.build_credentials(user)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # Step 4: Call the Tasks API
    service = build("tasks", "v1", credentials=creds)
    all_tasks = task.fetch_all_tasks(service)
    return JSONResponse(content=all_tasks)


from pydantic import BaseModel


class CompleteTaskPayload(BaseModel):
    taskId: str
    listId: str


@app.post("/api/tasks/complete")
def complete_task(payload: CompleteTaskPayload, request: Request):
    google_id = request.cookies.get("google_id")
    if not google_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = utils.get_user_by_google_id(google_id)
    creds = utils.build_credentials(user)

    service = build("tasks", "v1", credentials=creds)
    task = service.tasks().get(tasklist=payload.listId, task=payload.taskId).execute()
    task["status"] = "completed"
    task["completed"] = datetime.utcnow().isoformat() + "Z"

    service.tasks().update(
        tasklist=payload.listId, task=payload.taskId, body=task
    ).execute()
    return {"success": True}


@app.get("/api/news")
def get_news(query: str = "india"):
    try:
        if query == "india":
            all_articles = news.get_today_news()
        else:
            all_articles = news.get_all_news(query)
        return JSONResponse(content=all_articles)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to fetch news", "details": str(e)},
        )


@app.get("/api/system-info")
def get_system_info(request: Request):
    return sysinfo.getinfo()


from typing import List, Union


@app.get("/get_wiki_context")
def get_wiki_context(query):
    try:
        contexts = wiki.get_context(query)
        result = " ".join(contexts)
        summary = arch3b.get_summary(
            result[:500],
            "Summarize the following context clearly and concisely. Focus on capturing the key ideas, facts, or events without unnecessary repetition.",
        )
        return summary
    except Exception as e:
        return {"error": str(e)}


@app.get("/get_images", response_model=List[str])
def get_images(query):
    try:
        return wiki.search_images(query)
    except Exception as e:
        return {"error": str(e)}


@app.get("/get_query_type")
def get_query_type(query):
    result = arch3b.route_query(query)
    return result


@app.post("/add_task")
def add_task(request: Request, arguments: dict = Body(...)):
    google_id = request.cookies.get("google_id")
    if not google_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = utils.get_user_by_google_id(google_id)

    creds = utils.build_credentials(user)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # Step 4: Call the Tasks API
    service = build("tasks", "v1", credentials=creds)
    if not arguments.get("description"):  # empty string or missing key
        arguments["description"] = arch3b.get_summary(
            "Summarize this task and give it a very small description "
            + arguments["task_name"],
            "You are a helpful assistant.",
        )
    task.set_todo_and_reminder(service, arguments)

    return "Reminder" + arguments["task_name"] + " added"


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
