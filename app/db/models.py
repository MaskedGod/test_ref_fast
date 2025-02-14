from typing import List
from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    referral_code: Mapped["ReferralCode"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    referrals: Mapped[List["Referral"]] = relationship(
        back_populates="referrer", foreign_keys="[Referral.referrer_id]"
    )


class ReferralCode(Base):
    __tablename__ = "referral_codes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    expiry_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="referral_code")
    referees: Mapped[List["Referral"]] = relationship(
        back_populates="referral_code", foreign_keys="[Referral.referral_code_id]"
    )


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    referee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    referral_code_id: Mapped[int] = mapped_column(
        ForeignKey("referral_codes.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    referrer: Mapped["User"] = relationship(
        foreign_keys=[referrer_id], back_populates="referrals"
    )
    referral_code: Mapped["ReferralCode"] = relationship(back_populates="referees")
