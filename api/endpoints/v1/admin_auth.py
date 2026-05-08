import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional

from api.endpoints import deps
from api.crud import auth as crud_auth
from api.schemas.auth import AdminLoginRequest, AdminUpdatePasswordRequest, UserAuthResponse, UserResponse
from api.schemas.base import ApnaStoreResponse
from api.core import security
from api.models.user import User

router = APIRouter()
tags: Optional[list] = ["Admin - Auth"]
logger = logging.getLogger(__name__)

@router.post("/login", response_model=ApnaStoreResponse, tags=tags)
def admin_login(*, db: Session = Depends(deps.get_db), body: AdminLoginRequest):
    """
    Login endpoint exclusively for admin users using email and password.
    """
    try:
        user = crud_auth.get_user_by_email(db, email=body.email)
        
        if not user or user.role != "admin":
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid admin credentials."
            )
            
        if not user.is_active:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_403_FORBIDDEN,
                message="Admin account is deactivated."
            )
            
        if not security.verify_password(body.password, user.password):
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid admin credentials."
            )
            
        # Generate Tokens
        access_token = security.create_access_token(subject=user.id, type="user")
        refresh_token = security.create_refresh_token(subject=user.id, type="user")

        return ApnaStoreResponse(
            success=True,
            data=UserAuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user=UserResponse.model_validate(user)
            ),
            status_code=status.HTTP_200_OK,
            message="Admin logged in successfully."
        )
    except Exception as e:
        logger.error(f"Error in admin login: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred during admin login."
        )

@router.put("/update-password", response_model=ApnaStoreResponse, tags=tags)
def admin_update_password(
    *, 
    db: Session = Depends(deps.get_db), 
    body: AdminUpdatePasswordRequest,
    current_user: User = Depends(crud_auth.get_current_user)
):
    """
    Update admin password.
    """
    if current_user.role != "admin":
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_403_FORBIDDEN,
            message="Only admin can update their password here."
        )
        
    try:
        if body.new_password != body.confirm_password:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message="New password and confirm password do not match."
            )
            
        if not security.verify_password(body.old_password, current_user.password):
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Incorrect old password."
            )
            
        # Update Password
        hashed_pass = security.get_password_hash(body.new_password)
        current_user.password = hashed_pass
        db.commit()
        
        return ApnaStoreResponse(
            success=True,
            data=None,
            status_code=status.HTTP_200_OK,
            message="Admin password updated successfully."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating admin password: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to update password."
        )
