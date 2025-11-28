# AI Fitness Agent 🏋️‍♂️

Intelligent workout and nutrition planning system with clean architecture, role-based access control (RBAC), and AI-powered automated plan generation.

## 🚀 Key Features

- **Intelligent Plan Generation**: Uses Google Gemini or OpenAI to create personalized workout and nutrition plans
- **Role-Based Access Control (RBAC)**: Admins, Trainers, Nutritionists, and Clients with specific permissions
- **State Management**: Plans with states (draft, approved, active, archived)
- **Version History**: Complete tracking of plan changes
- **Comment System**: Communication between professionals and clients
- **Notifications**: Real-time alerts on plan updates
- **REST API**: Complete interface with FastAPI
- **Web Frontend**: Intuitive user interface

## 🏗️ Architecture

The project follows **Clean Architecture** with strict application of SOLID principles:

```
src/
├── domain/           # Modelos de negocio y contratos de repositorios
├── application/      # Lógica de negocio y casos de uso
├── infrastructure/   # Implementaciones (DB, IA, etc.)
│   ├── repositories/ # Persistencia con SQLAlchemy
│   └── ai/          # Proveedores de IA (Gemini, OpenAI)
└── interfaces/       # Puntos de entrada (API, Frontend)
    ├── api/         # Endpoints REST + DTOs
    └── frontend/    # Interfaz web
```

📖 **Detailed documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md)

## 📋 Requirements

- Python 3.9+
- Google Gemini or OpenAI API Key

## 🔧 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd agent_fitness
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=sqlite:///./fitness_agent.db

# AI Provider (gemini or openai)
DEFAULT_AI_PROVIDER=gemini

# API Keys (configure according to your provider)
GEMINI_API_KEY=your_api_key_here
# OPENAI_API_KEY=your_api_key_here
```

### 5. Initialize the database

```bash
python -m src.infrastructure.database
```

If you need to migrate an existing database with RBAC:

```bash
python migrate_rbac.py
```

## 🚀 Running

### Development server

```bash
uvicorn src.interfaces.api.main:app --reload
```

The application will be available at:
- **API**: http://localhost:8000
- **Frontend**: http://localhost:8000/static/index.html
- **API Documentation**: http://localhost:8000/docs

## 🧪 Testing

```bash
# Basic tests
python tests/test_core.py

# Advanced features tests
python tests/test_advanced_features.py
```

## 📚 Basic Usage

### 1. Create a user

```bash
POST /users/register
{
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "profile": {
    "age": 30,
    "gender": "male",
    "goal": "muscle_gain",
    "activity_level": "moderate"
  }
}
```

### 2. Generate workout plan

```bash
POST /plans/workout
Headers: { "X-User-Id": "<user_id>" }
```

### 3. Assign trainer role (Admin only)

```bash
POST /admin/roles/assign
{
  "user_id": "<trainer_id>",
  "role": "trainer"
}
```

## 🔑 Roles and Permissions

| Role | Permissions |
|------|-------------|
| **Admin** | Complete system management, role assignment |
| **Trainer** | Create/edit workout plans for their clients |
| **Nutritionist** | Create/edit nutrition plans for their clients |
| **Client** | View their plans, activate approved plans |

## 🛠️ Technologies

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI**: Google Gemini AI / OpenAI GPT
- **Architecture**: Clean Architecture, SOLID, DDD

## 🎨 Implemented Design Patterns

- **Repository Pattern**: Persistence abstraction
- **Dependency Injection**: Component decoupling
- **Template Method**: Reusable AI services
- **Strategy Pattern**: Interchangeable AI providers
- **Factory Pattern**: Complex object construction
- **DTO Pattern**: Separation of presentation and domain layers

## 📁 Key File Structure

```
agent_fitness/
├── src/
│   ├── config.py              # Configuración centralizada
│   ├── dependencies.py        # Inyección de dependencias
│   ├── domain/
│   │   ├── models.py         # Entidades de negocio
│   │   ├── repositories.py   # Interfaces de repositorios
│   │   └── permissions.py    # Definición de roles
│   ├── application/
│   │   ├── user_service.py
│   │   ├── planning_service.py
│   │   ├── role_service.py
│   │   └── interfaces.py     # Contratos de servicios externos
│   ├── infrastructure/
│   │   ├── ai/
│   │   │   ├── base.py       # Template base para IA
│   │   │   ├── gemini.py
│   │   │   └── openai.py
│   │   └── repositories/      # Implementaciones SQLAlchemy
│   └── interfaces/
│       ├── api/
│       │   ├── routers.py
│       │   └── dto/          # Data Transfer Objects
│       └── frontend/
├── tests/
├── ARCHITECTURE.md           # Documentación de arquitectura
└── README.md                # Este archivo
```

## 🔄 Switching AI Provider

To switch between Gemini and OpenAI, edit `.env`:

```env
DEFAULT_AI_PROVIDER=openai  # or "gemini"
OPENAI_API_KEY=sk-...
```

The system will switch automatically without code changes.

## 📝 Future Improvements

- [ ] Telegram Bot integration
- [ ] Migrate to PostgreSQL
- [ ] Cache system with Redis
- [ ] Real-time notifications (WebSockets)
- [ ] Dockerization
- [ ] CI/CD Pipeline

## 🤝 Contributing

Contributions are welcome. Please:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📧 Contact

For questions or suggestions, open an issue in the repository.

---

**Built with ❤️ using Clean Architecture and SOLID Principles**
