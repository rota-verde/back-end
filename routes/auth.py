auth_router = APIRouter()
from fastapi import APIRouter, Depends, HTTPException

from schemas.user import UserCreate, UserLogin

@auth_router.post("/register")
async def register_user(user: UserCreate): ...

@auth_router.post("/login")
async def login_user(credentials: UserLogin): ...

@auth_router.post("/forgot-password")
async def forgot_password(telefone: str): ...

@auth_router.post("/reset-password")
async def reset_password(token: str, new_password: str): ...

@auth_router.delete("/delete-account/{user_id}")
async def delete_account(user_id: str): ...

@auth_router.post("/2fa/enable/{user_id}")
async def enable_2fa(user_id: str): ...

@auth_router.post("/2fa/verify")
async def verify_2fa(data: TwoFAVerification): ... # type: ignore

@auth_router.get("/terms-of-service")
async def get_terms_of_service(): ...

@auth_router.get("/privacy-policy")
async def get_privacy_policy(): ...
