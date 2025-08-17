# Dashboard Setup Guide

This document explains how to run the escalation dashboard locally, configure environment variables, and understand the expected backend API responses.

---

## 1. Running the Dashboard Locally

### **Prerequisites**
- Python 3.9+
- `pip` installed
- (Optional) Backend API running

### **Steps**
1. Clone the repository:

```bash
git clone https://github.com/Shreya-nipunge/GrowAI.git
cd GrowAI
cd dashboard
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
cd ..
```

4. Edit `.env`:

   * **Without backend**: Leave `BACKEND_URL` blank to use sample in-memory data.
   * **With backend**: Set `BACKEND_URL` to your backend API base URL and `ADMIN_TOKEN` to your admin access token.

Example:

```bash
BACKEND_URL=http://localhost:9000
ADMIN_TOKEN=my-secret-token
```

5. Start the dashboard:

```bash
uvicorn dashboard.app:app --reload
```

6. Open your browser and go to:

```bash
http://127.0.0.1:8000
```

---

## 2. Environment Variables

| Variable      | Description                                                  |
| ------------- | ------------------------------------------------------------ |
| `BACKEND_URL` | Base URL of the backend API (leave empty for in-memory mode) |
| `ADMIN_TOKEN` | Token required for authenticated API calls                   |

---

## 3. Expected Backend API Routes

The dashboard will call these endpoints when `BACKEND_URL` is set:

### **GET** `/api/escalations`

Returns a list of escalation objects.

#### Example Response:

```bash
[
  {
    "id": 1,
    "user": "+91-98xxxxxxx",
    "query": "Will frost affect wheat next week?",
    "attachments": [],
    "confidence": "LOW",
    "status": "open",
    "notes": [
      {
        "by": "user",
        "msg": "Hi, I’m worried about frost.",
        "timestamp": "2025-08-14 14:22:00"
      },
      {
        "by": "advisor",
        "msg": "We’ll check the forecast.",
        "timestamp": "2025-08-14 15:10:00"
      }
    ]
  }
]
```

---

### **GET** `/api/escalations/{id}`

Returns details of a single escalation by ID.

#### Example Response:

```bash
{
  "id": 1,
  "user": "+91-98xxxxxxx",
  "query": "Will frost affect wheat next week?",
  "attachments": [],
  "confidence": "LOW",
  "status": "open",
  "notes": [
    {
      "by": "user",
      "msg": "Hi, I’m worried about frost.",
      "timestamp": "2025-08-14 14:22:00"
    },
    {
      "by": "advisor",
      "msg": "We’ll check the forecast.",
      "timestamp": "2025-08-14 15:10:00"
    }
  ]
}
```

---

### **POST** `/api/escalations/{id}/respond`

Payload:

```bash
{ "message": "Your reply text here" }
```

### **POST** `/api/escalations/{id}/resolve`

Payload:

```bash
{ "note": "Resolved via dashboard" }
```

---

## 4. Notes

* When backend is not running, the dashboard will automatically use in-memory test data.
* Simulated API delays can be added in `app.py` for UI loading state testing.

---

**Author:** Shreya Nipunge
**Last Updated:** 2025-08-14
