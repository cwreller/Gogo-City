# Trey - Route Instances & Sharing

## Sprint 2 (DONE)

- [x] Build POST `/api/instances` - import a template into a personal route instance
- [x] Build GET `/api/instances` - list my route instances
- [x] Build GET `/api/instances/{id}` - get a single instance with tasks and progress
- [x] Instance snapshotting logic (copy template tasks into instance tasks on import)
- [x] Progress tracking (calculate completed vs total tasks)
- [x] Build GET `/api/routes/share/{share_code}` - preview a shared route
- [x] Build POST `/api/routes/import/{share_code}` - import a shared route into your account
- [x] Tests for all of the above

### Known Issue
- `user_id` is currently passed in the request body - this will need to change once Lucas adds auth (user_id will come from JWT token instead). Don't worry about it for now.

### Route Management
- [x] Build DELETE `/api/instances/{id}` - let users delete/archive a route instance
- [x] Build PATCH `/api/instances/{id}` - update status (active → completed, active → archived)
- [x] Auto-mark instance as "completed" when all tasks are checked in

### Route Editing
- [x] Build PATCH `/api/instances/{id}/tasks/{task_id}` - let users add notes to tasks
- [x] Build DELETE `/api/instances/{id}/tasks/{task_id}` - remove a task from an instance

### Template Discovery (built but TBD if we use it)
- [x] Build GET `/api/templates/public` - list all public templates
- [x] Build PATCH `/api/templates/{id}` - let author toggle `is_public` on their templates
- [x] Add filtering/search to public templates (by city, vibe tags)

## Key Files
- `app/api/routes/instances.py`
- `app/api/routes/sharing.py`
- `app/services/instance_service.py`
- `app/schemas/instances.py`