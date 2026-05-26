# AI-Powered Resume Analyzer

A modern, high-performance, full-stack application designed to parse PDF resumes, perform Applicant Tracking System (ATS) keyword analysis, calculate matching score percentages, and provide actionable feedback. It features a responsive React dashboard connected to a FastAPI backend and MongoDB database.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19 + Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v7 (Layout-based routing with Outlet)
- **Visualizations**: Recharts (ATS score history progress graphs)
- **Components**: React Circular Progressbar & Lucide React icons

### Backend & Storage
- **Framework**: FastAPI (REST API architecture)
- **Database**: MongoDB (via PyMongo client connection)
- **Authentication**: JWT Token-based (Header Bearer verification) & `bcrypt` password hashing
- **Parsing**: `pdfplumber` (automated page-by-page text extraction)

---

## 🌟 Key Features

1. **JWT User Authentication**: Secure login and signup flows with client-side token caching.
2. **Global Theme Sync**: Synchronized dark and light modes with localStorage state persistence.
3. **Dynamic Resume Upload**: Drag-and-drop file interface for uploading PDF documents.
4. **Automated ATS Parser**: Extracts resume text and performs keyword matching against 40+ engineering skillsets.
5. **Layout Structural Verification**: Checks for key sections like Work Experience, Education, Projects, and Skills.
6. **Detailed suggestions**: Generates specific improvement recommendations for missing clouds, databases, or project items.
7. **Responsive Analytics Dashboard**: Displays average ATS score cards, skills found metrics, recent uploads histories, and score progress line charts.

---

## 📁 Project Structure

```
├── backend/                  # FastAPI Application
│   ├── database/             # MongoDB client connection routines
│   │   └── mongodb.py
│   ├── models/               # User request schemas
│   │   └── user_model.py
│   ├── routes/               # REST Route Handlers (auth, resume)
│   │   ├── auth.py
│   │   └── resume.py
│   ├── services/             # Auth JWT decoding & PDF parsing logic
│   │   ├── auth_service.py
│   │   └── resume_service.py
│   ├── uploads/              # Local storage folder for uploaded resumes
│   ├── .env                  # Backend credentials (MONGO_URI, JWT_SECRET)
│   ├── main.py               # FastAPI server entrypoint
│   └── requirements.txt      # Python dependencies
│
└── frontend/                 # React Vite Client
    ├── src/
    │   ├── components/       # Reusable components (Navbar, Sidebar, Charts)
    │   │   ├── AnalyticsChart.jsx
    │   │   ├── DashboardCards.jsx
    │   │   ├── ScoreGauge.jsx
    │   │   └── UploadResume.jsx
    │   ├── pages/            # View pages (Dashboard, Upload, Auth)
    │   │   ├── Login.jsx
    │   │   ├── Signup.jsx
    │   │   └── Upload.jsx
    │   ├── services/         # API HTTP Client helper
    │   │   └── api.js
    │   ├── App.jsx           # App layout, global dark-mode, and routing
    │   └── main.jsx          # React DOM mounting
    ├── package.json          # Node dependencies
    └── vite.config.js        # Vite compilation configuration
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** (v18 or higher recommended)
- **Python** (v3.10 or higher recommended)
- **MongoDB** running locally on `mongodb://localhost:27017`

### 1. Setup the Database
Ensure MongoDB is running locally:
```bash
# Example command if running via mongod
mongod --dbpath /path/to/data/db
```

### 2. Run the FastAPI Backend
1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Configure environment variables in `backend/.env`:
   ```env
   MONGO_URI=mongodb://localhost:27017
   JWT_SECRET=your_custom_secure_jwt_secret_key
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the development server:
   ```bash
   python -m uvicorn main:app --port 8000 --reload
   ```
   The backend documentation will be available at `http://127.0.0.1:8000/docs`.

### 3. Run the React Frontend
1. Navigate to the frontend folder:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Launch the Vite dev server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173/` in your browser to view the application.

---

## 🧪 Integration Testing
A verification script is included to test the API workflows end-to-end (Signup -> Login -> PDF Generation -> PDF Upload -> Stats Check -> Graph Check).

To run integration testing:
1. Ensure the FastAPI backend is running on `http://127.0.0.1:8000`.
2. Locate the test script in the active conversation logs scratch directory or copy the script:
   ```bash
   # Run the integration test suite
   python test_flow.py
   ```
   The script generates a dummy PDF using `reportlab`, registers a new account, logs in, uploads the PDF, verifies text scanning results, and requests statistics.
