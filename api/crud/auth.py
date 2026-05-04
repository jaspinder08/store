import random
from datetime import datetime, timedelta
from typing import Any, Tuple, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from api.endpoints import deps
from api.models.user import User
from api.models.otp import OTP

def get_current_user(
    db: Session = Depends(deps.get_db),
    token: HTTPAuthorizationCredentials = Depends(deps.security),
) -> User:

    payload = deps.decode_token(token.credentials)

    # ✅ ROLE CHECK
    if payload.get("type") != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized as user",
        )

    user_id = payload.get("sub")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def get_user_by_phone(db: Session, phone: str):
    return db.query(User).filter(User.phone == phone).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, *, phone: str = None, email: str = None):
    try:
        user = User(phone=phone, email=email, role="user")
        db.add(user)
        db.flush()
        return user
    except Exception as e:
        db.rollback()
        raise e

def create_otp(db: Session, *, user_id: Any) -> Tuple[Optional[OTP], int, int]:
    try:
        # 1. Enforce 30s cooldown
        last_otp = db.query(OTP).filter(
            OTP.user_id == user_id
        ).order_by(OTP.created_at.desc()).first()
        
        if last_otp:
            time_diff = datetime.utcnow() - last_otp.created_at
            if time_diff.total_seconds() < 30:
                retry_after = int(30 - time_diff.total_seconds())
                return None, retry_after, 0

        # 2. Invalidate previous OTPs
        db.query(OTP).filter(
            OTP.user_id == user_id, 
            OTP.is_active == True
        ).update({"is_active": False})
        
        # 3. Generate new OTP (3 mins expiry)
        generated_otp = str(random.randint(100000, 999999))
        expires_in = 180
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        db_otp = OTP(
            user_id=user_id,
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

def verify_otp_logic(db: Session, *, reference_id: Any, otp_code: str) -> Tuple[Optional[Any], Optional[str]]:
    try:
        db_otp = db.query(OTP).filter(OTP.reference_id == reference_id).first()
        
        if not db_otp:
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
            return None, "Maximum attempts reached. Please request a new OTP"
            
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
        db_otp.is_used = True
        db_otp.is_active = False
        db.commit()
        
        return db_otp.user_id, None
    except Exception as e:
        db.rollback()
        raise e

def get_otp_by_reference(db: Session, reference_id: Any):
    return db.query(OTP).filter(OTP.reference_id == reference_id).first()
