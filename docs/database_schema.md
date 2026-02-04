# GoGoCity Database Schema

## A) ERD Overview

### Concise Diagram (for presentations)

```mermaid
erDiagram
    users ||--o{ route_templates : authors
    users ||--o{ route_instances : owns
    cities ||--o{ curated_tasks : contains
    cities ||--o{ route_templates : has
    route_templates ||--o{ template_tasks : has
    route_templates ||--o{ route_instances : spawns
    route_instances ||--o{ instance_tasks : has
    instance_tasks ||--o| check_ins : completes

    users {
        uuid id PK
        string email UK
        string username UK
    }
    cities {
        uuid id PK
        string name
        string state
    }
    curated_tasks {
        uuid id PK
        uuid city_id FK
        string name
        string category
        string verification_type
    }
    route_templates {
        uuid id PK
        uuid author_id FK
        uuid city_id FK
        string title
        string share_code UK
    }
    template_tasks {
        uuid id PK
        uuid template_id FK
        string name
        string verification_type
    }
    route_instances {
        uuid id PK
        uuid user_id FK
        uuid source_template_id FK
        string status
    }
    instance_tasks {
        uuid id PK
        uuid instance_id FK
        string name
        string verification_type
    }
    check_ins {
        uuid id PK
        uuid instance_task_id FK
        uuid user_id FK
        string verified_by
    }
```

### Full Schema Diagram (all fields)

```mermaid
erDiagram
    users ||--o{ route_templates : "authors"
    users ||--o{ route_instances : "owns"
    users ||--o{ check_ins : "creates"
    
    cities ||--o{ route_templates : "has"
    cities ||--o{ curated_tasks : "contains"
    
    route_templates ||--o{ template_tasks : "contains"
    route_templates ||--o{ route_instances : "source_of"
    
    route_instances ||--o{ instance_tasks : "contains"
    
    instance_tasks ||--o| check_ins : "completed_by"

    users {
        uuid id PK
        string email UK
        string username UK
        string display_name
        string avatar_url
        timestamp created_at
        timestamp updated_at
    }

    cities {
        uuid id PK
        string name
        string state
        string country
        decimal lat
        decimal lng
        string timezone
        timestamp created_at
    }

    curated_tasks {
        uuid id PK
        uuid city_id FK
        string name
        string description
        string address
        decimal lat
        decimal lng
        string google_place_id
        string task_description
        string verification_hint
        string verification_type
        string category
        array vibe_tags
        array dietary_tags
        int price_level
        string best_for
        string pro_tips
        string photo_url
        array best_times
        int avg_duration_minutes
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    places_cache {
        uuid id PK
        string place_id UK
        string provider
        string name
        string address
        decimal lat
        decimal lng
        array place_types
        int price_level
        decimal rating
        int rating_count
        array photo_references
        jsonb raw_data
        timestamp fetched_at
        timestamp expires_at
    }

    route_templates {
        uuid id PK
        uuid author_id FK
        uuid city_id FK
        string title
        string description
        string share_code UK
        boolean is_public
        int estimated_duration_minutes
        int estimated_budget_cents
        array vibe_tags
        timestamp created_at
        timestamp updated_at
    }

    template_tasks {
        uuid id PK
        uuid template_id FK
        string place_id
        string provider
        string name
        string address
        decimal lat
        decimal lng
        array place_types
        string task_description
        string verification_hint
        string verification_type
        string notes
        timestamp created_at
    }

    route_instances {
        uuid id PK
        uuid user_id FK
        uuid source_template_id FK
        string title
        string description
        string status
        timestamp started_at
        timestamp completed_at
        timestamp created_at
        timestamp updated_at
    }

    instance_tasks {
        uuid id PK
        uuid instance_id FK
        uuid source_template_task_id
        string place_id
        string provider
        string name
        string address
        decimal lat
        decimal lng
        array place_types
        string task_description
        string verification_hint
        string verification_type
        string notes
        timestamp created_at
    }

    check_ins {
        uuid id PK
        uuid instance_task_id FK
        uuid user_id FK
        timestamp checked_in_at
        string verified_by
        decimal lat
        decimal lng
        string photo_url
        string notes
        int rating
    }
```

### Text Diagram (fallback)

```
┌─────────────┐
│   users     │
└─────────────┘
       │ 1:N (author)
       ▼
┌─────────────────┐       ┌────────────────┐
│ route_templates │──1:N──│ template_tasks │
└─────────────────┘       └────────────────┘
       │                          │
       │ N:1                      │ snapshot
       ▼                          ▼
┌─────────────┐       ┌───────────────┐
│   cities    │──1:N──│ curated_tasks │
└─────────────┘       └───────────────┘

┌─────────────────┐       ┌────────────────┐       ┌───────────┐
│ route_instances │──1:N──│ instance_tasks │──1:1──│ check_ins │
└─────────────────┘       └────────────────┘       └───────────┘
       │
       │ N:1 (owner)
       ▼
┌─────────────┐
│   users     │
└─────────────┘

┌──────────────┐
│ places_cache │  (standalone cache for Google Places API)
└──────────────┘
```

---

## B) Key Relationships

| Relationship | Type | Description |
|-------------|------|-------------|
| users → route_templates | 1:N | User authors templates |
| users → route_instances | 1:N | User owns instances |
| cities → curated_tasks | 1:N | City contains curated tasks |
| cities → route_templates | 1:N | Templates belong to a city |
| route_templates → template_tasks | 1:N | Template contains tasks |
| route_templates → route_instances | 1:N | Template spawns instances |
| route_instances → instance_tasks | 1:N | Instance contains snapshotted tasks |
| instance_tasks → check_ins | 1:1 | One check-in per task |

---

## C) Task Verification Types

Tasks can have three verification types:

| Type | Has Location | Has Task Action | Verification Method | Example |
|------|-------------|-----------------|---------------------|---------|
| `gps` | ✅ | ❌ | GPS proximity | "Go to Centennial Park" |
| `photo` | ❌ | ✅ | AI photo analysis | "Eat hot chicken" |
| `both` | ✅ | ✅ | GPS + AI photo | "Pet a dog at Centennial Park" |

---

## D) Data Flow

```
1. CURATION (you & Trey)
   └── Add tasks to curated_tasks for each city
       ├── Location-only: "Visit Hattie B's"
       ├── Task-only: "Eat hot chicken" 
       └── Combined: "Order Prince's Hot at Hattie B's"

2. GENERATION (AI)
   └── User submits preferences (vibes, budget, dietary, time)
       └── AI selects matching curated_tasks
           └── Creates route_template with template_tasks

3. IMPORT (user starts route)
   └── User imports template
       └── Creates route_instance with instance_tasks (snapshot)

4. COMPLETION (user plays)
   └── User completes each instance_task
       └── Creates check_in with verified_by (gps/photo/both)
```

---

## E) Tables Summary

| Table | Purpose |
|-------|---------|
| `users` | User identity (email, username, avatar) |
| `cities` | Cities with coordinates and timezone |
| `curated_tasks` | Master list of tasks per city (your curated content) |
| `places_cache` | Cached Google Places API responses |
| `route_templates` | Generated/shared route plans |
| `template_tasks` | Tasks within a template |
| `route_instances` | User's personal copy of a route |
| `instance_tasks` | Snapshotted tasks for the user's instance |
| `check_ins` | Task completion records with verification |
