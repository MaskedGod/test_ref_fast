import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.db.models import User, ReferralCode, Referral
from app.schemas.referral import (
    ReferralCodeResponse,
    ReferralResponse,
)
from app.core.security import get_current_user
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import hash_password

ref_router = APIRouter(prefix="/referral", tags=["Referral System"])


@ref_router.post(
    "/create", response_model=ReferralCodeResponse, status_code=status.HTTP_201_CREATED
)
async def create_referral_code(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    existing_code = await db.execute(
        select(ReferralCode).where(
            ReferralCode.user_id == current_user.id, ReferralCode.is_active == True
        )
    )
    if existing_code.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active referral code",
        )

    code = secrets.token_urlsafe(6).upper()

    expiry_date = datetime.now(timezone.utc) + timedelta(days=1)

    new_code = ReferralCode(
        code=code, user_id=current_user.id, expiry_date=expiry_date, is_active=True
    )
    db.add(new_code)
    await db.commit()
    await db.refresh(new_code)

    return new_code


@ref_router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_referral_code(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    referral_code = await db.execute(
        select(ReferralCode).where(
            ReferralCode.user_id == current_user.id, ReferralCode.is_active == True
        )
    )
    referral_code = referral_code.scalars().first()

    if not referral_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active referral code found",
        )

    referral_code.is_active = False
    await db.commit()


@ref_router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_with_referral_code(
    user_data: UserCreate, referral_code: str, db: AsyncSession = Depends(get_db)
):
    code = await db.execute(
        select(ReferralCode).where(
            ReferralCode.code == referral_code,
            ReferralCode.is_active == True,
            ReferralCode.expiry_date > datetime.now(timezone.utc),
        )
    )
    code = code.scalars().first()

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired referral code",
        )

    hashed_password = hash_password(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_password)
    db.add(new_user)
    await db.flush()

    new_referral = Referral(
        referrer_id=code.user_id, referee_id=new_user.id, referral_code_id=code.id
    )
    db.add(new_referral)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@ref_router.get("/referees", response_model=list[ReferralResponse])
async def get_referees(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    referrals = await db.execute(
        select(Referral, User.email)
        .join(User, Referral.referee_id == User.id)
        .where(Referral.referrer_id == current_user.id)
    )
    results = referrals.all()

    return [
        ReferralResponse(referee_email=email, created_at=referral.created_at)
        for referral, email in results
    ]
