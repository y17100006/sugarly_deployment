import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Enum, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.database import Base

class ReadingType(str, enum.Enum):
    fasting = "fasting"
    before_meal = "before_meal"
    after_meal = "after_meal"
    before_sleep = "before_sleep"
    random = "random"

class RoleType(str, enum.Enum):
    user = "user"
    assistant = "assistant"

class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True) # مربوط بـ auth.users(id)
    email = Column(String, unique=True, index=True, nullable=True)
    name = Column(String)
    
    # الخصائص السريرية المنقولة من الباك أند القديم
    carb_ratio = Column(Float, nullable=True)
    sensitivity_factor = Column(Float, nullable=True)
    target_sugar = Column(Float, default=100.0)

    # العلاقات
    readings = relationship("SugarReading", back_populates="user", cascade="all, delete")
    meals = relationship("Meal", back_populates="user", cascade="all, delete")
    chats = relationship("ChatHistory", back_populates="user", cascade="all, delete")


class SugarReading(Base):
    __tablename__ = "sugar_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    sugar_level = Column(Float, nullable=False)
    reading_type = Column(Enum(ReadingType, name="reading_type"), nullable=False)
    notes = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="readings")

class FoodAnalysis(Base):
    __tablename__ = "food_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    food_name = Column(String, nullable=False)
    calories = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    protein = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)
    fiber = Column(Float, default=0.0)
    analyzed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="food_analyses")

class Meal(Base):
    __tablename__ = "meals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    description = Column(String, nullable=True)
    meal_type = Column(Enum(MealType, name="meal_type"), nullable=True)
    
    # البيانات الغذائية
    total_carbs = Column(Float, default=0.0)
    
    insulin_dose_taken = Column(Float, default=0.0)
    
    # قراءات السكر كأرقام عادية قبل وبعد الوجبة
    sugar_before = Column(Float, nullable=True)
    sugar_after = Column(Float, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="meals")

class InsulinRecord(Base):
    __tablename__ = "insulin_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    daily_units = Column(Float, nullable=False)
    long_acting_units = Column(Float, default=0)
    remaining_units = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="insulin_records")


class HourlyLog(Base):
    __tablename__ = "hourly_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False) # الوقت مقتطع للساعة
    avg_sugar = Column(Float, default=0.0)
    total_carbs = Column(Float, default=0.0)
    total_insulin = Column(Float, default=0.0)


class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(Enum(RoleType, name="role_type"), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="chats")
