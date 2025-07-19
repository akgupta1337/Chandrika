from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from supabase import create_client, Client
import os
from fastapi import Request, HTTPException
from dotenv import load_dotenv


load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def store_user(email, google_id, name, access_token, refresh_token):
    # Insert or update user
    supabase.table("users").upsert(
        {
            "google_id": google_id,
            "email": email,
            "name": name,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    ).execute()


def get_valid_credentials(user):
    creds = Credentials(
        token=user["access_token"],
        refresh_token=user["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    )

    # Refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        supabase.table("users").update({"access_token": creds.token}).eq(
            "email", user["email"]
        ).execute()

    return creds


import json

GOOGLE_CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]


def build_credentials(user):
    with open(GOOGLE_CLIENT_SECRETS_FILE) as f:
        secret = json.load(f)["web"]

    client_id = secret["client_id"]
    client_secret = secret["client_secret"]
    token_uri = secret["token_uri"]

    return Credentials(
        token=user["access_token"],
        refresh_token=user["refresh_token"],
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )


def get_user(email):
    response = supabase.table("users").select("*").eq("email", email).single().execute()
    return response.data  # This will be a dict


def get_user_by_google_id(google_id: str):
    response = supabase.table("users").select("*").eq("google_id", google_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")

    return response.data[0]
