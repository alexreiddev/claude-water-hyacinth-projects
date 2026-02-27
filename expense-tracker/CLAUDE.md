# Expense Tracker — Claude Guide

Automatic expense tracking app. Ingests transactions from SMS, notifications, and PDFs; categorizes them; and surfaces them via a dashboard with tagging and notification overlays.

---

## Architecture

The project follows **Clean Architecture** with three concentric layers:

```
presentation  →  domain  ←  data
```

- **Presentation** depends on domain (never on data).
- **Data** depends on domain (implements repository interfaces).
- **Domain** has zero external dependencies.

### Module layout

```
expense-tracker/
├── app/
│   ├── presentation/
│   │   ├── dashboard/          # Main spending overview screen
│   │   ├── tagging_overlay/    # System overlay for tagging expenses on-the-fly
│   │   └── notifications_ui/  # Notification-based quick-action UI
│   ├── domain/
│   │   ├── model/              # Pure Kotlin data classes (Expense, Category, …)
│   │   ├── usecase/            # One class per use-case (GetExpenses, SaveExpense, …)
│   │   └── repository/        # Repository interfaces (no implementations here)
│   ├── data/
│   │   ├── local/
│   │   │   ├── db/             # Room database setup
│   │   │   ├── entity/         # Room @Entity classes
│   │   │   └── dao/            # Room @Dao interfaces
│   │   ├── ingestion/
│   │   │   ├── sms/            # BroadcastReceiver + SMS parser
│   │   │   ├── notifications/  # NotificationListenerService integration
│   │   │   └── pdf/            # PDF statement parser (PdfBox / iText)
│   │   └── categorization/
│   │       ├── fts/            # SQLite full-text search rules
│   │       ├── rules/          # Deterministic regex/keyword rules
│   │       └── ml/             # On-device ML model (TFLite)
│   ├── system/
│   │   ├── permissions/        # Runtime permission helpers
│   │   ├── overlays/           # SYSTEM_ALERT_WINDOW overlay management
│   │   └── security/           # Encryption helpers (EncryptedSharedPrefs, BiometricPrompt)
│   └── di/                     # Hilt modules wiring the whole graph
```

---

## Domain Model

| Class | Description |
|---|---|
| `Expense` | Core entity: amount, description, category, tags, source, timestamp |
| `Category` | Enum: FOOD, TRANSPORT, UTILITIES, ENTERTAINMENT, HEALTH, SHOPPING, OTHER |
| `IngestionSource` | Enum: SMS, NOTIFICATION, PDF, MANUAL |

---

## Key Conventions

### Coroutines
- Use `Flow<T>` for observable data streams (lists from DB).
- Use `suspend fun` for one-shot reads and writes.
- `viewModelScope` in ViewModels; `CoroutineScope(Dispatchers.IO)` in services.

### Naming
- Use-cases are named `<Verb><Noun>UseCase` (e.g., `GetExpensesUseCase`, `SaveExpenseUseCase`).
- Repository implementations live in `data/` and are named `<Noun>RepositoryImpl`.
- Room entities are suffixed `Entity`; domain models have no suffix.

### Dependency Injection
- Hilt is the DI framework. All modules live in `app/di/`.
- Use `@Singleton` scope for repositories and DB; `@ViewModelScoped` for use-cases.

---

## Build & Development

### Prerequisites
- JDK 17+
- Gradle 8.5 (via wrapper — do **not** install Gradle globally)

### Common commands

```bash
# Build
./gradlew :app:assemble

# Unit tests
./gradlew :app:test

# Lint (ktlint)
./gradlew :app:ktlintCheck

# Auto-fix lint issues
./gradlew :app:ktlintFormat

# Run a single test class
./gradlew :app:test --tests "com.expensetracker.domain.model.ExpenseTest"
```

### Running tests for a specific layer
```bash
# Domain layer tests only
./gradlew :app:test --tests "com.expensetracker.domain.*"

# Categorization tests
./gradlew :app:test --tests "com.expensetracker.data.categorization.*"
```

---

## Ingestion Pipeline

```
Raw signal (SMS / Notification / PDF)
        │
        ▼
   Parser (layer-specific)
        │  extracts: merchant, amount, currency
        ▼
  CategorizationEngine
        │  priority: ML > rules > FTS fallback
        ▼
  ExpenseRepository.save()
        │
        ▼
  Room DB  ──►  Flow to UI
```

### Adding a new ingestion source
1. Create a parser in `data/ingestion/<source>/` that returns a `RawTransaction`.
2. Wire it to `CategorizationEngine` in `di/IngestionModule.kt`.
3. Add the corresponding `IngestionSource` enum value.
4. Write a unit test for the parser in `app/src/test/`.

---

## Categorization

Three-tier fallback strategy:

1. **ML** (`ml/`) — TFLite model trained on labelled transaction descriptions. Fastest for common merchants.
2. **Rules** (`rules/`) — Regex/keyword rules defined in `categorization_rules.json`. Editable without recompile.
3. **FTS** (`fts/`) — SQLite FTS5 index over historic expense descriptions for fuzzy fallback.

---

## Overlay System

The tagging overlay uses `SYSTEM_ALERT_WINDOW` permission.

- Request flow: `PermissionHelper.requestOverlayPermission()` → settings deeplink → `onActivityResult`.
- Overlay lifecycle is managed by `OverlayManager` (a bound `Service`).
- Keep overlay views **stateless** — push all state via `StateFlow` from `OverlayViewModel`.

---

## Security

- All stored amounts and descriptions are encrypted at rest via **EncryptedSharedPreferences** and **SQLCipher** (Room integration).
- Biometric authentication gates the dashboard. Implement using `BiometricPrompt` from `system/security/`.
- Never log raw SMS content or transaction amounts — use redacted placeholders in debug logs.

---

## Testing Philosophy

| Layer | Test type | Tools |
|---|---|---|
| Domain models & use-cases | Pure unit tests | kotlin.test, MockK |
| Repository implementations | Unit tests with fake DAO | MockK |
| Parsers | Unit tests with fixture files | kotlin.test |
| Categorization | Unit + property-based | kotlin.test, Kotest |
| ViewModels | Unit tests with `Turbine` | MockK, Turbine |

Integration and UI tests (Espresso) live in `androidTest/` and require a device/emulator.
