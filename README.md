# CyBreach Notification Hub

## Overview

The CyBreach Notification Hub is a FastAPI backend that manages notifications and user notification preferences.

## Features

- Create Notifications
- Read Notifications
- Update Notifications
- Delete Notifications
- Filter Notifications by User
- Mark Notifications as Read
- Update Notification Status
- View Unread Notifications
- Get Unread Notification Count
- Manage User Notification Preferences

## Technologies

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## Run

```bash
uvicorn app.main:app --reload
```

## Swagger

```
http://127.0.0.1:8000/docs
```