# Arquitectura del AI Fitness Agent

## Visión General

El proyecto sigue una **arquitectura en capas** inspirada en Clean Architecture y Domain-Driven Design, con estricta aplicación de los principios SOLID.

```mermaid
graph TB
    subgraph "Capa de Interfaces"
        API[API REST<br/>FastAPI]
        Frontend[Frontend<br/>HTML/JS]
    end
    
    subgraph "Capa de Aplicación"
        Services[Services<br/>UserService, PlanningService]
        Auth[Authentication<br/>& Authorization]
    end
    
    subgraph "Capa de Dominio"
        Models[Domain Models<br/>User, Plan, etc]
        Repos[Repository Interfaces<br/>Abstract Definitions]
        Permissions[Permissions<br/>& Roles]
    end
    
    subgraph "Capa de Infraestructura"
        RepoImpl[Repository Implementations<br/>SQLAlchemy]
        AI[AI Service<br/>Gemini]
        DB[(SQLite DB)]
    end
    
    API --> Services
    Frontend --> API
    Services --> Models
    Services --> Repos
    Auth --> Repos
    RepoImpl -.implements.-> Repos
    RepoImpl --> DB
    Services --> AI
    
    style Models fill:#e1f5ff
    style Repos fill:#e1f5ff
    style Services fill:#fff4e1
    style API fill:#f0e1ff
    style RepoImpl fill:#e1ffe1
```

---

## Estructura de Capas

### 1. **Domain Layer** (`src/domain/`)
**Responsabilidad**: Contiene la lógica de negocio pura, sin dependencias externas.

**Componentes**:
- **Models** ([models.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/domain/models.py)): Entidades del dominio (User, WorkoutPlan, NutritionPlan, etc.)
- **Repository Interfaces** ([repositories.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/domain/repositories.py)): Contratos abstractos para persistencia
- **Permissions** ([permissions.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/domain/permissions.py)): Definición de roles y permisos

### 2. **Application Layer** (`src/application/`)
**Responsabilidad**: Orquesta la lógica de negocio y coordina entre dominio e infraestructura.

**Componentes**:
- [services.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/application/services.py): `UserService`, `PlanningService`
- [role_service.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/application/role_service.py): Gestión de roles
- [version_service.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/application/version_service.py): Control de versiones
- [comment_service.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/application/comment_service.py): Comentarios en planes
- [notification_service.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/application/notification_service.py): Notificaciones

### 3. **Infrastructure Layer** (`src/infrastructure/`)
**Responsabilidad**: Implementaciones concretas de tecnologías y frameworks.

**Componentes**:
- **Repositories** (`repositories/`): Implementaciones SQLAlchemy de las interfaces del dominio
- [database.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/infrastructure/database.py): Configuración de base de datos
- [ai_service.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/infrastructure/ai_service.py): Integración con Gemini AI
- [orm_models.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/infrastructure/orm_models.py): Modelos ORM de SQLAlchemy

### 4. **Interface Layer** (`src/interfaces/`)
**Responsabilidad**: Puntos de entrada al sistema (API, CLI, etc.).

**Componentes**:
- **API** (`api/`):
  - [routers.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/interfaces/api/routers.py): Endpoints principales
  - [advanced_routers.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/interfaces/api/advanced_routers.py): Endpoints avanzados
  - [auth.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/interfaces/api/auth.py): Autenticación y autorización
- **Frontend** (`frontend/`): Interfaz web del cliente

### 5. **Dependency Injection** ([dependencies.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/dependencies.py))
**Responsabilidad**: Configuración centralizada de inyección de dependencias.

---

## Aplicación de Principios SOLID

### **S - Single Responsibility Principle**

Cada clase tiene una única responsabilidad bien definida:

```mermaid
graph LR
    UserService[UserService<br/>Gestión de usuarios] 
    PlanningService[PlanningService<br/>Generación de planes]
    VersionService[VersionService<br/>Historial de versiones]
    
    UserRepo[UserRepository<br/>Persistencia de usuarios]
    PlanRepo[PlanRepository<br/>Persistencia de planes]
    
    style UserService fill:#fff4e1
    style PlanningService fill:#fff4e1
    style VersionService fill:#fff4e1
    style UserRepo fill:#e1ffe1
    style PlanRepo fill:#e1ffe1
```

**Ejemplos**:
- `UserService`: Solo gestiona operaciones de usuario (registro, actualización de perfil)
- `PlanningService`: Solo gestiona generación y activación de planes
- `SqlAlchemyUserRepository`: Solo maneja persistencia de usuarios en BD

### **O - Open/Closed Principle**

El sistema está abierto a extensión pero cerrado a modificación:

**Ejemplo**: Cambiar de SQLite a PostgreSQL

```python
# NO se modifica código existente
# SOLO se crea nueva implementación

class PostgresUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        # Implementación PostgreSQL
        ...

# En dependencies.py
def get_user_repository() -> UserRepository:
    return PostgresUserRepository(db)  # ← Cambio aquí
```

### **L - Liskov Substitution Principle**

Cualquier implementación de una interfaz puede sustituir a otra sin romper el sistema:

```python
# Ambas implementaciones respetan el contrato
class SqlAlchemyUserRepository(UserRepository):
    def get_by_id(self, user_id: str) -> Optional[User]:
        # Implementación SQLAlchemy
        ...

class MockUserRepository(UserRepository):
    def get_by_id(self, user_id: str) -> Optional[User]:
        # Implementación mock para tests
        ...

# El servicio funciona con cualquiera
service = UserService(user_repo)  # user_repo puede ser cualquier implementación
```

### **I - Interface Segregation Principle**

Las interfaces están segregadas por dominio específico:

```mermaid
graph TB
    UserRepo[UserRepository<br/>get_by_id, save, update<br/>get_by_role, get_all]
    PlanRepo[WorkoutPlanRepository<br/>get_current_plan<br/>get_by_id, save, update]
    VersionRepo[PlanVersionRepository<br/>save, get_by_plan_id<br/>get_by_id]
    
    style UserRepo fill:#e1f5ff
    style PlanRepo fill:#e1f5ff
    style VersionRepo fill:#e1f5ff
```

**Beneficio**: Cada repositorio solo expone los métodos que necesita su dominio.

### **D - Dependency Inversion Principle**

Las capas de alto nivel NO dependen de capas de bajo nivel. Ambas dependen de abstracciones:

```mermaid
graph TB
    subgraph "Alto Nivel"
        PlanningService[PlanningService]
    end
    
    subgraph "Abstracción"
        IPlanRepo[WorkoutPlanRepository<br/>Interface]
        IAIService[AIService<br/>Interface]
    end
    
    subgraph "Bajo Nivel"
        SqlRepo[SqlAlchemyWorkoutPlanRepository]
        GeminiAI[GeminiAIService]
    end
    
    PlanningService --> IPlanRepo
    PlanningService --> IAIService
    SqlRepo -.implements.-> IPlanRepo
    GeminiAI -.implements.-> IAIService
    
    style PlanningService fill:#fff4e1
    style IPlanRepo fill:#e1f5ff
    style IAIService fill:#e1f5ff
    style SqlRepo fill:#e1ffe1
    style GeminiAI fill:#e1ffe1
```

**Implementación**: Usando FastAPI Dependency Injection

```python
# dependencies.py coordina todo
def get_planning_service(
    ai_service: AIService = Depends(get_ai_service),
    workout_repo: WorkoutPlanRepository = Depends(get_workout_repository),
    nutrition_repo: NutritionPlanRepository = Depends(get_nutrition_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> PlanningService:
    return PlanningService(ai_service, workout_repo, nutrition_repo, user_repo)

# routers.py usa la abstracción
@router.post("/plans/workout")
def generate_workout(
    current_user: User = Depends(get_current_user),
    service: PlanningService = Depends(get_planning_service)  # ← Inyección
):
    return service.generate_workout_plan(current_user.id)
```

---

## Flujo de Interacción de Componentes

### Ejemplo: Creación de Plan de Entrenamiento

```mermaid
sequenceDiagram
    participant C as Cliente (Frontend)
    participant R as Router (API)
    participant Auth as Auth Middleware
    participant PS as PlanningService
    participant AI as AIService
    participant WR as WorkoutRepository
    participant DB as Database
    
    C->>R: POST /plans/workout
    R->>Auth: Validar X-User-Id
    Auth->>WR: get_by_id(user_id)
    WR->>DB: SELECT * FROM users
    DB-->>WR: User data
    WR-->>Auth: User
    Auth-->>R: User autenticado
    
    R->>PS: generate_workout_plan(user_id)
    PS->>WR: get_current_plan(user_id)
    WR->>DB: SELECT * FROM workout_plans
    DB-->>WR: Plan existente (si hay)
    WR-->>PS: Current plan
    
    PS->>AI: generate_workout_plan(user_profile)
    AI-->>PS: Plan generado por IA
    
    PS->>WR: save(new_plan)
    WR->>DB: INSERT INTO workout_plans
    DB-->>WR: Success
    WR-->>PS: Plan guardado
    
    PS-->>R: WorkoutPlan
    R-->>C: JSON response
```

### Ejemplo: Actualización de Plan por Trainer

```mermaid
sequenceDiagram
    participant T as Trainer
    participant R as Router
    participant Auth as Auth
    participant RS as RoleService
    participant PS as PlanningService
    participant VS as VersionService
    participant NS as NotificationService
    participant WR as WorkoutRepository
    participant VR as VersionRepository
    participant NR as NotificationRepository
    
    T->>R: PUT /trainer/workout-plans/{id}
    R->>Auth: Verificar rol "trainer"
    Auth-->>R: Autorizado
    
    R->>RS: get_my_clients(trainer_id)
    RS-->>R: Lista de clientes
    
    R->>PS: get_plan(plan_id)
    PS->>WR: get_by_id(plan_id)
    WR-->>PS: Plan actual
    PS-->>R: Verificar ownership
    
    R->>VS: create_version(old_plan)
    VS->>VR: save(version)
    VR-->>VS: Version guardada
    
    R->>WR: update(updated_plan)
    WR-->>R: Plan actualizado
    
    R->>NS: create_notification(client_id, "Plan Updated")
    NS->>NR: save(notification)
    NR-->>NS: Notificación guardada
    
    R-->>T: Success
```

---

## Patrones de Diseño Aplicados

### 1. **Repository Pattern**
Abstrae la persistencia de datos del dominio.

### 2. **Dependency Injection**
Centralizado en [dependencies.py](file:///Users/felipe/Documents/software_propio/agent_fitness/src/dependencies.py), permite:
- Fácil testing con mocks
- Cambio de implementaciones sin modificar código
- Desacoplamiento total entre capas

### 3. **Service Layer Pattern**
Los servicios en `src/application/` orquestan operaciones complejas.

### 4. **Strategy Pattern**
Implementado implícitamente a través de interfaces (e.g., `AIService` puede tener múltiples implementaciones: Gemini, OpenAI, etc.)

---

## Ventajas de esta Arquitectura

1. **Testabilidad**: Cada capa puede probarse independientemente
2. **Mantenibilidad**: Código organizado y con responsabilidades claras
3. **Flexibilidad**: Fácil cambiar tecnologías (BD, AI provider, etc.)
4. **Escalabilidad**: Capas pueden dividirse en microservicios si es necesario
5. **Reusabilidad**: Servicios y repositorios son reutilizables

---

## Próximos Pasos Arquitectónicos

- [ ] Implementar caching con Redis
- [ ] Agregar event bus para notificaciones en tiempo real
- [ ] Migrar a PostgreSQL en producción
- [ ] Dockerizar la aplicación
- [ ] Implementar API Gateway si se escala a microservicios
