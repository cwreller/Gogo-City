"""Route generation endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.route_generation import GenerateRouteRequest, GenerateRouteResponse
from app.services.route_service import RouteService

router = APIRouter()


@router.post("/generate", response_model=GenerateRouteResponse)
def generate_route(
    request: GenerateRouteRequest,
    db: Session = Depends(get_db),
    # TODO: Add auth dependency to get real user_id
    # user_id: UUID = Depends(get_current_user_id),
):
    """Generate a personalized route based on user preferences.
    
    Takes user preferences (city, budget, time, vibe tags, etc.) and uses AI
    to select the best matching tasks from our curated list.
    
    Returns a new route template with the selected tasks.
    """
    # TODO: Get real user_id from auth
    # For now, get any user from the database for testing
    from app.models import User
    test_user = db.query(User).first()
    if not test_user:
        raise HTTPException(status_code=400, detail="No users in database. Run seed script first.")
    user_id = test_user.id
    
    try:
        service = RouteService(db)
        return service.generate_route(request, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the error for debugging
        import traceback
        print(f"Error generating route: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate route: {str(e)}")
