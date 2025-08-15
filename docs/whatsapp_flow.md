flowchart TD
U[User on WhatsApp] -->|Question| B(Bot: /ingest)
B -->|HIGH confidence| A1[Reply text + image + TTS link]
B -->|LOW/MEDIUM| E[Create Escalation + Ticket ID]
E --> D[Advisor Dashboard]
D -->|Respond/Resolve| N[Notify User on WhatsApp]