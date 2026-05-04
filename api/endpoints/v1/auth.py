import logging
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from api.endpoints import deps
from api.crud import auth as auth_crud
from api.schemas.auth import (
    SendOTPRequest,
    VerifyOTPRequest,
    UserAuthResponse,
    SendOTPResponse,
    ResendOTPRequest
)
from api.schemas.base import ApnaStoreResponse
from api.utils.email import send_otp_email
from api.core import security
from api.models.user import User


router = APIRouter()
tags: Optional[list] = ["Auth"]
logger = logging.getLogger(__name__)


@router.post("/send-otp", response_model=ApnaStoreResponse, tags=tags, status_code=status.HTTP_200_OK)
def send_otp(
    *,
    request: Request,
    db: Session = Depends(deps.get_db),
    body: SendOTPRequest
):
    try:
        user = None

        # 🔍 Check user by phone or email
        if body.phone:
            user = auth_crud.get_user_by_phone(db, phone=body.phone)
            if not user:
                user = auth_crud.create_user(db, phone=body.phone)

        elif body.email:
            user = auth_crud.get_user_by_email(db, email=body.email)
            if not user:
                user = auth_crud.create_user(db, email=body.email)

        else:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Email or Phone is required"
            )

        # 🔐 Generate OTP with refactored logic
        db_otp, cooldown, expires_in = auth_crud.create_otp(db, user_id=user.id)
        if not db_otp:
            return ApnaStoreResponse(
                success=False,
                data={"retry_after": cooldown},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                message=f"Please wait {cooldown}s before requesting a new OTP"
            )

        # 📩 Send OTP
        if body.email:
            send_otp_email(body.email, db_otp.otp)

        if body.phone:
            # Placeholder for SMS service
            print(f"OTP for phone {body.phone}: {db_otp.otp} (Ref: {db_otp.reference_id})")

        return ApnaStoreResponse(
            success=True,
            data=SendOTPResponse(
                reference_id=db_otp.reference_id,
                cooldown_seconds=cooldown,
                expires_in=expires_in
            ),
            status_code=status.HTTP_200_OK,
            message="OTP sent successfully"
        )

    except Exception as e:
        logger.error(f"Error sending OTP: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred"
        )

@router.post("/verify-otp", response_model=ApnaStoreResponse, tags=tags, status_code=status.HTTP_200_OK)
def verify_otp(
    *,
    db: Session = Depends(deps.get_db),
    body: VerifyOTPRequest
):
    try:
        # 1. Verify OTP using service logic
        user_id, error_message = auth_crud.verify_otp_logic(
            db, 
            reference_id=body.reference_id, 
            otp_code=body.otp
        )
        
        if error_message:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=error_message
            )
        
        # 2. Get user
        user = db.query(User).filter(User.id == user_id).first()
        
        # 3. Generate Tokens
        access_token = security.create_access_token(subject=user.id, type="user")
        refresh_token = security.create_refresh_token(subject=user.id, type="user")
        
        return ApnaStoreResponse(
            success=True,
            data=UserAuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user=user
            ),
            status_code=status.HTTP_200_OK,
            message="OTP verified successfully"
        )
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Verification failed"
        )

@router.post("/resend-otp", response_model=ApnaStoreResponse, tags=tags, status_code=status.HTTP_200_OK)
def resend_otp(
    *,
    db: Session = Depends(deps.get_db),
    body: ResendOTPRequest
):
    try:
        # 1. Find existing OTP
        db_otp_old = auth_crud.get_otp_by_reference(db, reference_id=body.reference_id)
        if not db_otp_old or not db_otp_old.user_id:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Invalid reference ID"
            )

        # 2. Get User
        user = db.query(User).filter(User.id == db_otp_old.user_id).first()
        if not user:
             return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
                message="User not found"
            )

        # 3. Create New OTP
        db_otp, cooldown, expires_in = auth_crud.create_otp(db, user_id=user.id)
        
        if not db_otp:
            return ApnaStoreResponse(
                success=False,
                data={"retry_after": cooldown},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                message=f"Please wait {cooldown}s before requesting a new OTP"
            )

        # 4. Send OTP
        if user.email:
            send_otp_email(user.email, db_otp.otp)

        if user.phone:
            print(f"Resent OTP for phone {user.phone}: {db_otp.otp} (Ref: {db_otp.reference_id})")

        return ApnaStoreResponse(
            success=True,
            data=SendOTPResponse(
                reference_id=db_otp.reference_id,
                cooldown_seconds=cooldown,
                expires_in=expires_in
            ),
            status_code=status.HTTP_200_OK,
            message="OTP resent successfully"
        )
    except Exception as e:
        logger.error(f"Error resending OTP: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to resend OTP"
        )