# AI Digital Human – Virtual Secretary (Lisa)

## Overview

This project implements an **AI Digital Human (Avatar-based Virtual Secretary)** that combines:

- Real-time conversational AI (LLM + LangChain Agents)
- Emotion detection and voice style mapping
- Microsoft Azure Speech Avatar (WebRTC-based)
- FastAPI backend with Redis-based memory
- TURN server (coturn) for WebRTC relay
- Docker-based one-click deployment

The virtual secretary, **Lisa**, is designed to interact naturally with users through text, voice, emotion, and a real-time animated avatar.

---

## System Architecture

```

├── Frontend (HTML + JavaScript)
│   ├── WebRTC Avatar Rendering
│   ├── Azure Speech SDK (TTS + Avatar)
│   └── Chat UI
│
├── Backend (FastAPI)
│   ├── LangChain Agent (LLM + Tools)
│   ├── Emotion Detection Chain
│   ├── Redis-based Conversation Memory
│   └── Search Tool (SerpAPI)
│
├── Infrastructure
│   ├── coturn (TURN server)
│   ├── Redis
│   └── Docker

```

---

## Tech Stack

### Frontend
- HTML5 / JavaScript
- WebRTC
- Microsoft Cognitive Services Speech SDK
- Azure Avatar Synthesis (TTS + Video)

### Backend
- Python 3
- FastAPI
- LangChain
- OpenAI-compatible LLM API
- Redis (conversation memory)
- SerpAPI (real-time web search)

### Infrastructure
- Docker
- coturn (TURN server)
- Redis Server

---

## Key Features

- **Real-time Digital Avatar** via WebRTC
- **Multi-language & Multi-voice Support**
- **Emotion-aware Responses**
- **Persistent Conversation Memory (Redis)**
- **Autonomous Tool Usage (Web Search)**
- **Fully Containerized Deployment**

---

## Project Structure

```

.
├── static/
│   └── index.html          # Frontend Avatar UI
├── server.py               # FastAPI backend
├── turnserver.conf         # coturn configuration
├── redis.conf              # Redis configuration
├── Dockerfile
└── README.md

````

---

## Environment Variables

Set the following environment variables before running:

```bash
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=your_api_base_url
SERPAPI_API_KEY=your_serpapi_key
````

---

## Frontend Description

The frontend uses **Azure Speech Avatar SDK** to:

* Establish a WebRTC connection via TURN
* Render a real-time animated avatar
* Convert AI responses into expressive speech using SSML
* Dynamically control voice style based on detected emotion

Emotion styles are mapped to Azure SSML voice styles, such as:

* `default`
* `friendly`
* `cheerful`
* `upbeat`
* `angry`
* `depressed`

---

## Backend Description

### FastAPI Endpoints

#### `GET /`

Health check endpoint.

#### `POST /chat`

Handles user input, emotion detection, agent reasoning, and response generation.

---

### LangChain Agent

* Uses `ChatOpenAI`
* Tool-enabled agent (`search`)
* Automatically decides when to perform web searches
* Maintains conversation context via Redis

---

### Emotion Detection

A dedicated chain classifies user input into one of the following moods:

* `default`
* `friendly`
* `cheerful`
* `upbeat`
* `angry`
* `depressed`

The detected mood affects both:

* Textual response style
* Avatar voice expression

---

### Conversation Memory

* Powered by `RedisChatMessageHistory`
* Automatically summarizes long conversations
* Extracts and preserves key user attributes (e.g. name, preferences)

---

## Docker Deployment

### Build Image

```bash
docker build -t ai-avatar .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -p 3478:3478 \
  -p 6379:6379 \
  ai-avatar
```

---

## Exposed Ports

| Port | Service         |
| ---: | --------------- |
| 8000 | FastAPI Backend |
| 3478 | TURN Server     |
| 6379 | Redis           |

---

## TURN Server (coturn)

* Provides WebRTC relay for avatar streaming
* Configured via `turnserver.conf`
* Supports credential-based authentication

---

## Redis

* Stores conversation history
* Enables long-term memory and summarization
* Mounted volume: `/data`

---

## Notes & Recommendations

* Use HTTPS when deploying to production
* Do not expose API keys in frontend code
* Consider GPU acceleration for large-scale avatar rendering
* Azure Speech Avatar requires a valid Azure Speech resource

---

## License

This project is provided for educational and research purposes.
Please ensure compliance with Azure, OpenAI, and SerpAPI usage policies.

---

## Author

AI Digital Human – Virtual Secretary (Lisa)
Built with FastAPI, LangChain, Azure Speech, and WebRTC
```
```
