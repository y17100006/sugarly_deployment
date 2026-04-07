# Sugrly - AI Powered Diabetic Assistant

Sugrly is an advanced diabetes management application that leverages artificial intelligence to assist users in tracking blood glucose levels, performing nutritional analysis of meals using computer vision, and interacting with an intelligent medical assistant via voice.

The backend is built with FastAPI to ensure high performance and seamless asynchronous operations.

---

## Architecture and Databases

The project utilizes a dual-database system to optimize performance and efficiency:

### 1. PostgreSQL (Primary Database)
- **Purpose**: Stores user information, authentication data, blood sugar logs, daily meal history, and profile settings.
- **Rationale**: A robust relational database that supports complex queries and provides the scalability needed to handle large sets of user data.

### 2. SQLite (Nutritional Database)
- **Purpose**: Facilitates local nutritional information lookups.
- **Rationale**: Lightweight and exceptionally fast for read-only operations. It requires no server configuration, making it ideal for instantaneous calorie and nutrient searches.

---

## Technical Prerequisites

Before setting up the project, ensure the following are installed:
1. Python 3.9+
2. PostgreSQL (Database server)
3. FFMPEG (Required for audio processing)

### Audio Processing with FFMPEG
Sugrly supports voice interactions. Mobile applications typically transmit audio in formats such as .ogg or .m4a. The backend uses the pydub library, which requires FFMPEG to convert these files into the .wav format necessary for Speech-to-Text engines. Voice features will not function without FFMPEG.

---

## Local Setup Instructions

### 1. AI Configuration
The project uses Google Gemini Flash for analysis and interaction. Obtain a GEMINI_API_KEY from Google AI Studio.

### 2. PostgreSQL Configuration
1. Open your database management tool (e.g., pgAdmin or terminal).
2. Create a new database named sugrly_db:
   ```sql
   CREATE DATABASE sugrly_db;
   ```
3. Note your database username and password for the environment configuration.

### 3. Installation
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Variables (.env)
Create a file named .env in the root directory and add the following configurations:
```env
# Database Connection
DATABASE_URL=postgresql+asyncpg://your_username:your_password@localhost:5432/sugrly_db

# AI API Keys
GEMINI_API_KEY=your_gemini_key_here
FDC_API_KEY=your_usda_nutrition_key_here

# Security
SECRET_KEY=your_secure_random_string
ALGORITHM=HS256
```

### 5. Running the Server
```bash
uvicorn app.main:app --reload
```
Once the server is running, the interactive API documentation is available at:
http://127.0.0.1:8000/docs

---

## Key Features

- Voice-to-Text Chat: Interactive voice communication with the assistant for medical guidance based on user data.
- AI Food Analysis: Image-based meal analysis using Gemini Vision for immediate nutritional reporting.
- Smart Insulin Calculation: Suggested insulin dosages based on recorded carbohydrate intake.
- JWT Authentication: Advanced security and encryption for user data protection.

---

## Directory Structure

- app/core: Application settings and security configurations.
- app/models: SQLAlchemy models defining PostgreSQL table structures.
- app/routers: API endpoints for meals, sugar tracking, analytics, and chat services.
- app/services: Application logic including AI services, speech processing, and nutritional lookups.
- app/schemas: Pydantic schemas for data validation and serialization.

---

Note: Ensure that the food_database.db file is located in the correct directory as referenced in the ai_food_service.py file to enable local food search functionality.
