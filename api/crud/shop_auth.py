import random
from datetime import datetime, timedelta
from typing import Any, Tuple, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from api.endpoints import deps
from api.models.shop import Shop
from api.models.otp import OTP

def get_current_shop(
    db: Session = Depends(deps.get_db),
    token: HTTPAuthorizationCredentials = Depends(deps.security),
) -> Shop:

    payload = deps.decode_token(token.credentials)

    # ✅ ROLE CHECK
    if payload.get("type") != "shop":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized as shop",
        )

    shop_id = payload.get("sub")

    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    return shop

def get_shop_by_email(db: Session, email: str):
    return db.query(Shop).filter(Shop.email == email).first()

def get_shop_by_phone(db: Session, phone: str):
    return db.query(Shop).filter(Shop.phone == phone).first()

def create_shop(
    db: Session, 
    *, 
    shop_name: str, 
    email: str, 
    phone: str = None,
    owner_name: str = None,
    shop_type: str = None,
    gst_number: str = None,
    shop_image: str = None
):
    try:
        db_shop = Shop(
            shop_name=shop_name, 
            email=email, 
            phone=phone, 
            owner_name=owner_name,
            shop_type=shop_type,
            gst_number=gst_number,
            shop_image=shop_image,
            role="shop"
        )
        db.add(db_shop)
        db.commit()
        db.refresh(db_shop)
        return db_shop
    except Exception as e:
        db.rollback()
        raise e

def update_shop_password(db: Session, *, shop_id: Any, hashed_password: str):
    try:
        db_shop = db.query(Shop).filter(Shop.id == shop_id).first()
        if db_shop:
            db_shop.password = hashed_password
            db.commit()
            db.refresh(db_shop)
            return db_shop
        return None
    except Exception as e:
        db.rollback()
        raise e

def create_shop_otp(db: Session, *, shop_id: Any) -> Tuple[Optional[OTP], int, int]:
    try:
        # Enforce 30s cooldown
        last_otp = db.query(OTP).filter(OTP.shop_id == shop_id).order_by(OTP.created_at.desc()).first()
        if last_otp:
            time_diff = datetime.utcnow() - last_otp.created_at
            if time_diff.total_seconds() < 30:
                retry_after = int(30 - time_diff.total_seconds())
                return None, retry_after, 0

        # Invalidate previous OTPs
        db.query(OTP).filter(OTP.shop_id == shop_id, OTP.is_active == True).update({"is_active": False})
        
        generated_otp = str(random.randint(100000, 999999))
        expires_in = 180
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        db_otp = OTP(
            shop_id=shop_id,
            otp=generated_otp,
            expires_at=expires_at,
        )
        db.add(db_otp)
        db.commit()
        db.refresh(db_otp)
        
        return db_otp, 30, expires_in
    except Exception as e:
        db.rollback()
        raise e

def verify_shop_otp_logic(
    db: Session, 
    *, 
    reference_id: Any, 
    otp_code: str,
    mark_used: bool = True
) -> Tuple[Optional[Any], Optional[str]]:
    try:
        db_otp = db.query(OTP).filter(OTP.reference_id == reference_id).first()
        
        if not db_otp or not db_otp.shop_id:
            return None, "Invalid reference ID"
        
        if not db_otp.is_active or db_otp.is_used:
            return None, "This OTP is no longer valid"
            
        if db_otp.expires_at < datetime.utcnow():
            db_otp.is_active = False
            db.commit()
            return None, "OTP has expired"
            
        if db_otp.attempts >= 3:
            db_otp.is_active = False
            db.commit()
            return None, "Maximum attempts reached"
            
        if db_otp.otp != otp_code:
            db_otp.attempts += 1
            db.commit()
            attempts_left = 3 - db_otp.attempts
            if attempts_left <= 0:
                db_otp.is_active = False
                db.commit()
                return None, "Maximum attempts reached. OTP invalidated"
            return None, f"Invalid OTP. {attempts_left} attempts remaining"
            
        # Success!
        if mark_used:
            db_otp.is_used = True
            db_otp.is_active = False
            db.commit()
        
        return db_otp.shop_id, None
    except Exception as e:
        db.rollback()
        raise e

def get_otp_by_reference(db: Session, reference_id: Any):
    return db.query(OTP).filter(OTP.reference_id == reference_id).first()