# Smart Task Analyzer

A full-stack application to intelligently score and prioritize tasks based on urgency, importance, effort, and dependencies.

## 🚀 Setup Instructions

### Backend
1. Navigate to the project root.
2. Create a virtual environment:
   ```bash
   python -m venv env
   .\env\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install django djangorestframework django-cors-headers
   ```
4. Run migrations:
   ```bash
   cd backend
   python manage.py migrate
   ```
5. Start the server:
   ```bash
   python manage.py runserver
   ```

### Frontend
1. Open `frontend/index.html` in your browser.
2. Ensure the backend is running on `http://localhost:8000`.

## 🧠 Algorithm Explanation

The core of the application is the `calculate_priority_score` function in `backend/tasks/scoring.py`. It assigns a score (0-100+) based on four weighted factors:

1.  **Urgency (40%)**: Calculated from the Due Date.
    *   **Overdue**: High penalty (Score > 100).
    *   **Approaching**: Exponential decay as the date gets further away.
2.  **Importance (30%)**: Linear scale based on user input (1-10).
3.  **Dependencies (20%)**: Tasks that block other tasks (dependencies) get a boost.
4.  **Effort (10%)**: "Quick Wins" (low effort) get a small boost to encourage clearing small tasks.

### Strategies
The algorithm supports dynamic strategies that adjust the weights:
*   **Smart Balance**: Default balanced approach.
*   **Deadline Driven**: heavily weights Urgency (70%).
*   **High Impact**: heavily weights Importance (70%).
*   **Fastest Wins**: heavily weights Effort (60%) to clear backlog.

## 🛠 Design Decisions

*   **Stateless Analysis**: The `/analyze` endpoint accepts a list of tasks and returns them sorted without requiring database storage. This allows for quick "what-if" scenarios and bulk analysis.
*   **Django & DRF**: Used for robust API handling and potential future scalability.
*   **Vanilla JS Frontend**: Kept the frontend simple and lightweight without build steps, focusing on clean code and logic.
*   **Glassmorphism UI**: Implemented a modern, premium dark-mode design for better user experience.

## ⏱ Time Breakdown

*   **Backend Setup & Models**: 30 mins
*   **Algorithm Design & Implementation**: 45 mins
*   **API Views & Strategies**: 30 mins
*   **Frontend Structure & Styling**: 45 mins
*   **JS Logic & Integration**: 30 mins
*   **Documentation & Polish**: 15 mins
*   **Total**: ~3.5 hours

## 🌟 Bonus Features Attempted
*   **Sorting Strategies**: Implemented 4 distinct strategies.
*   **Dependency Logic**: Tasks that block others are prioritized.
*   **Visual Explanations**: The UI explains *why* a task got its score.
*   **Circular Dependency Detection**: The system detects cycles (e.g., A->B->A) and visually flags them with a warning.

## 🔮 Future Improvements
*   **User Authentication**: Allow users to save their own task lists securely.
*   **Database Persistence**: Fully utilize the database to save tasks between sessions (currently `/analyze` is stateless).
*   **Drag-and-Drop Interface**: Allow users to reorder tasks manually to override the algorithm.
*   **Email Notifications**: Send reminders for high-priority tasks.
