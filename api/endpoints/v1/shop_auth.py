import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from api.endpoints import deps
from api.crud import shop_auth
from api.schemas.shop_auth import (
    ShopLoginRequest, 
    ShopResponse, 
    ShopVerifyOTPRequest,
    ShopVerifyOTPRequest,
    ShopAuthResponse
)
from api.schemas.auth import SendOTPResponse, ResendOTPRequest # Reuse for consistency
from api.schemas.base import ApnaStoreResponse
from api.core import security
from api.utils.email import send_otp_email
from api.models.shop import Shop
from api.models.otp import OTP

router = APIRouter()
tags: Optional[list] = ["Shop - Auth"]
logger = logging.getLogger(__name__)

@router.post("/check-exists", response_model=ApnaStoreResponse, tags=tags)
def check_shop_exists(*, db: Session = Depends(deps.get_db), body: ShopLoginRequest):
    """
    Step 1: Check if a shop exists.
    Allows the frontend to decide next steps.
    """
    try:
        shop = None
        if body.email:
            shop = shop_auth.get_shop_by_email(db, email=body.email)
        elif body.phone:
            shop = shop_auth.get_shop_by_phone(db, phone=body.phone)
        
        if not shop:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Shop not found. Please contact admin to register."
            )
        
        if not shop.is_active:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_403_FORBIDDEN,
                message="Your shop account has been deactivated. Please contact admin."
            )
            
        return ApnaStoreResponse(
            success=True,
            data={"shop": ShopResponse.model_validate(shop)},
            status_code=status.HTTP_200_OK,
            message="Shop exists."
        )
    except Exception as e:
        logger.error(f"Error checking shop exists: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred."
        )

@router.post("/send-otp", response_model=ApnaStoreResponse, tags=tags)
def shop_send_otp(*, db: Session = Depends(deps.get_db), body: ShopLoginRequest):
    """Step 2 (Reset path): Send OTP to shop email/phone."""
    try:
        shop = None
        if body.email:
            shop = shop_auth.get_shop_by_email(db, email=body.email)
        elif body.phone:
            shop = shop_auth.get_shop_by_phone(db, phone=body.phone)
            
        if not shop:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Shop not registered."
            )
            
        if not shop.is_active:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_403_FORBIDDEN,
                message="Your shop account has been deactivated."
            )

        db_otp, cooldown, expires_in = shop_auth.create_shop_otp(db, shop_id=shop.id)
        
        if not db_otp:
            return ApnaStoreResponse(
                success=False,
                data={"retry_after": cooldown},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                message=f"Please wait {cooldown}s before requesting a new OTP."
            )

        if shop.email:
            send_otp_email(shop.email, db_otp.otp)
        
        if shop.phone:
            print(f"Shop OTP for {shop.phone}: {db_otp.otp} (Ref: {db_otp.reference_id})")

        return ApnaStoreResponse(
            success=True,
            data=SendOTPResponse(
                reference_id=db_otp.reference_id,
                cooldown_seconds=cooldown,
                expires_in=expires_in
            ),
            status_code=status.HTTP_200_OK,
            message="OTP sent successfully."
        )
    except Exception as e:
        logger.error(f"Error sending shop OTP: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to send OTP."
        )

@router.post("/verify-otp", response_model=ApnaStoreResponse, tags=tags)
def shop_verify_otp(*, db: Session = Depends(deps.get_db), body: ShopVerifyOTPRequest):
    """Step 3 (Reset path): Verify OTP. Marks it as verified in the DB."""
    try:
        shop_id, error_message = shop_auth.verify_shop_otp_logic(
            db, 
            reference_id=body.reference_id, 
            otp_code=body.otp,
            mark_used=True # Mark as used/verified now
        )
        
        if error_message:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=error_message
            )
        
        shop = db.query(Shop).filter(Shop.id == shop_id).first()
        
        access_token = security.create_access_token(subject=shop.id, type="shop")
        refresh_token = security.create_refresh_token(subject=shop.id, type="shop")

        return ApnaStoreResponse(
            success=True,
            data=ShopAuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                shop=ShopResponse.model_validate(shop)
            ),
            status_code=status.HTTP_200_OK,
            message="OTP verified successfully."
        )
    except Exception as e:
        logger.error(f"Error verifying shop OTP: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Verification failed."
        )



@router.post("/resend-otp", response_model=ApnaStoreResponse, tags=tags)
def shop_resend_otp(
    *, 
    db: Session = Depends(deps.get_db), 
    body: ResendOTPRequest
):
    """Resend OTP for a shop based on an existing reference ID."""
    try:
        # 1. Find existing OTP
        db_otp_old = shop_auth.get_otp_by_reference(db, reference_id=body.reference_id)
        if not db_otp_old or not db_otp_old.shop_id:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Invalid reference ID."
            )

        # 2. Get Shop
        shop = db.query(Shop).filter(Shop.id == db_otp_old.shop_id).first()
        if not shop:
             return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Shop not found."
            )
            
        if not shop.is_active:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_403_FORBIDDEN,
                message="Your shop account has been deactivated."
            )

        # 3. Create New OTP
        db_otp, cooldown, expires_in = shop_auth.create_shop_otp(db, shop_id=shop.id)
        
        if not db_otp:
            return ApnaStoreResponse(
                success=False,
                data={"retry_after": cooldown},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                message=f"Please wait {cooldown}s before requesting a new OTP."
            )

        # 4. Send OTP
        if shop.email:
            send_otp_email(shop.email, db_otp.otp)

        if shop.phone:
            print(f"Shop OTP Resent for {shop.phone}: {db_otp.otp}")

        return ApnaStoreResponse(
            success=True,
            data=SendOTPResponse(
                reference_id=db_otp.reference_id,
                cooldown_seconds=cooldown,
                expires_in=expires_in
            ),
            status_code=status.HTTP_200_OK,
            message="OTP resent successfully."
        )
    except Exception as e:
        logger.error(f"Error resending shop OTP: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to resend OTP."
        )

from api.schemas.shop_auth import ShopUpdateRequest
from api.crud.shop_auth import get_current_shop

@router.get("/profile", response_model=ApnaStoreResponse, tags=tags)
def get_shop_profile(
    current_shop: Shop = Depends(get_current_shop)
):
    """Get current logged-in shop profile."""
    return ApnaStoreResponse(
        success=True,
        data=ShopResponse.model_validate(current_shop),
        status_code=status.HTTP_200_OK,
        message="Profile retrieved successfully."
    )

@router.put("/profile", response_model=ApnaStoreResponse, tags=tags)
def update_shop_profile(
    body: ShopUpdateRequest,
    db: Session = Depends(deps.get_db),
    current_shop: Shop = Depends(get_current_shop)
):
    """
    Complete or update shop onboarding profile.
    Automatically calculates if profile_completed based on mandatory fields.
    """
    try:
        update_data = body.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(current_shop, k, v)
            
        # Mandatory fields check
        mandatory_fields = [
            current_shop.shop_name,
            current_shop.owner_name,
            current_shop.phone,
            current_shop.address,
            current_shop.city,
            current_shop.state,
            current_shop.pincode
        ]
        
        current_shop.profile_completed = all(bool(f and str(f).strip()) for f in mandatory_fields)
        
        db.commit()
        db.refresh(current_shop)
        
        return ApnaStoreResponse(
            success=True,
            data=ShopResponse.model_validate(current_shop),
            status_code=status.HTTP_200_OK,
            message="Profile updated successfully."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating shop profile: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Profile update failed."
        )