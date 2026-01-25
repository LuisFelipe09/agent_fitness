# AI Fitness Agent 🏋️‍♂️

Intelligent workout and nutrition planning platform with AI-powered personalized plans, professional coach review, and modern React interface.

## 🚀 Key Features

- **AI-Powered Plan Generation**: Personalized workout and nutrition plans using Google Gemini or OpenAI
- **Modern React Interface**: Professional UI built with React 18, TypeScript, and Shadcn UI
- **Telegram Mini App**: Native integration with Telegram for seamless mobile experience
- **Role-Based Access Control**: Admins, Trainers, Nutritionists, and Clients with specific permissions
- **Professional Workflow**: Draft → Review → Approve → Active plan states
- **Version History**: Complete tracking of plan changes
- **Communication**: Comment system for feedback between coaches and athletes
- **Real-time Notifications**: Stay updated on plan approvals and changes

## 🏗️ Technology Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Database ORM with migrations
- **Pydantic** - Data validation and serialization
- **Clean Architecture** - SOLID principles and layered design
- **AI Providers**: Google Gemini / OpenAI GPT
- **Database**: SQLite (dev) / PostgreSQL (prod)

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast build tool and HMR
- **Shadcn UI v4** - Accessible component library
- **Tailwind CSS v4** - Utility-first styling
- **Telegram Mini App SDK** - Native Telegram integration

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+ and npm
- Google Gemini or OpenAI API Key

## 🔧 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd agent_fitness
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys
```

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=sqlite:///./fitness_agent.db

# AI Provider (gemini or openai)
DEFAULT_AI_PROVIDER=gemini

# API Keys
GEMINI_API_KEY=your_api_key_here
# OPENAI_API_KEY=your_api_key_here
```

```bash
# Initialize the database
python -m src.infrastructure.database
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

The frontend `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_TELEGRAM_BOT_NAME=your_bot_name
```

## 🚀 Running the Application

### Development Mode (Recommended)

Run backend and frontend in separate terminals:

```bash
# Terminal 1: Backend (FastAPI)
uvicorn src.interfaces.api.main:app --reload
# API runs on http://localhost:8000
```

```bash
# Terminal 2: Frontend (Vite)
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

The Vite dev server will proxy API requests to the FastAPI backend automatically.

### Production Mode

```bash
# Build frontend
cd frontend
npm run build
cd ..

# Run FastAPI (serves both API and built frontend)
uvicorn src.interfaces.api.main:app --host 0.0.0.0 --port 8000
```

Access the application:
- **New React App**: http://localhost:8000/app
- **API Documentation**: http://localhost:8000/docs
- **Legacy Interface**: http://localhost:8000/static/index.html

## 🧪 Testing

```bash
# Backend tests
python -m pytest tests/

# Frontend tests (when available)
cd frontend
npm test
```

## 📚 Project Structure

```
agent_fitness/
├── frontend/                    # React TypeScript frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── ui/            # Shadcn UI components
│   │   │   ├── AthleteDashboard.tsx
│   │   │   ├── CoachDashboard.tsx
│   │   │   ├── RoutineWizard.tsx
│   │   │   └── ...
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # Utilities and API client
│   │   └── main.tsx           # App entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── src/                        # Backend (Python)
│   ├── domain/                # Business models and interfaces
│   ├── application/           # Use cases and business logic
│   ├── infrastructure/        # Database, AI, external services
│   └── interfaces/            # API endpoints and DTOs
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md        # Architecture details
│   └── ROADMAP.md            # Development roadmap
├── tests/                      # Backend tests
├── requirements.txt
└── README.md
```

## 🔑 Roles and Permissions

| Role | Permissions |
|------|-------------|
| **Admin** | Complete system management, role assignment |
| **Trainer** | Create/edit workout plans, approve plans for clients |
| **Nutritionist** | Create/edit nutrition plans, approve nutrition plans |
| **Client** | View plans, generate AI plans, activate approved plans |

## 📖 API Usage Examples

### Register a User

```bash
POST /users/register
{
  "name": "John Doe",
  "email": "john@example.com",
  "profile": {
    "age": 30,
    "gender": "male",
    "goal": "muscle_gain",
    "activity_level": "moderate"
  }
}
```

### Generate Workout Plan

```bash
POST /plans/workout
Headers: { "X-User-Id": "<user_id>" }
```

### Assign Trainer Role (Admin only)

```bash
POST /admin/roles/assign
{
  "user_id": "<trainer_id>",
  "role": "trainer"
}
```

## 🎨 Frontend Features

- **Welcome Screen**: Onboarding with feature highlights
- **Role Selector**: Choose between Athlete or Coach experience
- **Athlete Dashboard**: 
  - Quick stats overview
  - Generate workout and nutrition plans
  - View and activate approved plans
  - Track progress
- **Coach Dashboard**:
  - Review pending plans
  - Manage athletes
  - Approve or request changes
  - View activity feed
- **Routine Wizard**: Step-by-step plan generation
  - Goal selection
  - Experience level
  - Schedule preferences
  - Equipment availability
  - Custom preferences
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Telegram Integration**: Native experience in Telegram Mini App

## 🔄 Switching AI Providers

Edit `.env` to switch between Gemini and OpenAI:

```env
DEFAULT_AI_PROVIDER=openai  # or "gemini"
OPENAI_API_KEY=sk-...
```

The system will switch automatically without code changes.

## 📝 Documentation

- [**Architecture Guide**](docs/ARCHITECTURE.md) - Detailed architecture documentation
- [**Development Roadmap**](docs/ROADMAP.md) - Feature roadmap and future plans
- [**API Documentation**](http://localhost:8000/docs) - Interactive API docs (when running)

## 🛠️ Development Tools

### Backend
- **FastAPI Docs**: http://localhost:8000/docs
- **Database Browser**: Use DB Browser for SQLite to inspect the database

### Frontend
- **Vite Dev Server**: Hot module replacement for instant updates
- **TypeScript**: Type checking during development
- **ESLint**: Code quality checks

## 🚧 Roadmap Highlights

- ✅ **Phase 0 (Complete)**: Backend with Clean Architecture, Modern React frontend
- 🔄 **Phase 1 (In Progress)**: MVP Athlete Experience with full API integration
- 🔜 **Phase 2**: Nutrition module with TDEE calculator
- 🔜 **Phase 3**: Complete coach review system
- 🔜 **Phase 4**: Progress tracking and analytics
- 🔜 **Phase 5**: Social features and community

See [ROADMAP.md](docs/ROADMAP.md) for complete details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style and architecture patterns
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License.

## 📧 Contact

For questions or suggestions, open an issue in the repository.

---

**Built with ❤️ using Clean Architecture, SOLID Principles, and Modern React**
