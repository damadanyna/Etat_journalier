from fastapi import APIRouter
from controller.Credits import Credits

router = APIRouter()
credits = Credits()

@router.get("/credits")
def get_credits():
    return credits.get_data()

api_router = router
