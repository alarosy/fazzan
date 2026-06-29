"""
Accommodation Service — خدمات السكن والإقامة.
"""
from typing import List, Optional
from sqlalchemy.orm import joinedload

from core.database import get_session
from models.accommodation import AccommodationBooking, AccommodationExtra


def get_all_bookings() -> List[AccommodationBooking]:
    """جلب جميع حجوزات السكن."""
    with get_session() as session:
        results = session.query(AccommodationBooking).options(
            joinedload(AccommodationBooking.extra_services)
        ).order_by(AccommodationBooking.check_in_date.desc()).all()
        
        for r in results:
            if r in session:
                session.expunge(r)
                for ex in r.extra_services:
                    if ex in session:
                        session.expunge(ex)
        return results


def get_booking_by_id(booking_id: int) -> Optional[AccommodationBooking]:
    """جلب حجز سكن بالمعرّف."""
    with get_session() as session:
        booking = session.query(AccommodationBooking).options(
            joinedload(AccommodationBooking.extra_services)
        ).filter(AccommodationBooking.id == booking_id).first()
        
        if booking:
            if booking in session:
                session.expunge(booking)
                for ex in booking.extra_services:
                    if ex in session:
                        session.expunge(ex)
        return booking


def create_booking(booking_data: dict, extras: List[dict] = None) -> AccommodationBooking:
    """إنشاء حجز سكن جديد مع خدماته الإضافية."""
    # Logic verification
    if booking_data.get("check_in_date") and booking_data.get("check_out_date"):
        if booking_data["check_in_date"] >= booking_data["check_out_date"]:
            raise ValueError("تاريخ الدخول يجب أن يكون قبل تاريخ المغادرة")

    with get_session() as session:
        booking = AccommodationBooking(**booking_data)
        session.add(booking)
        session.flush()
        
        if extras:
            for ex in extras:
                extra = AccommodationExtra(booking_id=booking.id, **ex)
                session.add(extra)
        
        session.flush()
        
        # Re-query
        result = session.query(AccommodationBooking).options(
            joinedload(AccommodationBooking.extra_services)
        ).filter(AccommodationBooking.id == booking.id).first()
        
        if result in session:
            session.expunge(result)
            for ex in result.extra_services:
                if ex in session:
                    session.expunge(ex)
        return result


def update_booking(booking_id: int, booking_data: dict, extras: List[dict] = None) -> Optional[AccommodationBooking]:
    """تحديث حجز سكن وخدماته الإضافية."""
    if booking_data.get("check_in_date") and booking_data.get("check_out_date"):
        if booking_data["check_in_date"] >= booking_data["check_out_date"]:
            raise ValueError("تاريخ الدخول يجب أن يكون قبل تاريخ المغادرة")

    with get_session() as session:
        booking = session.query(AccommodationBooking).filter(AccommodationBooking.id == booking_id).first()
        if not booking:
            return None
        
        for key, value in booking_data.items():
            if hasattr(booking, key):
                setattr(booking, key, value)
        
        # If extras provided, clear old and add new
        if extras is not None:
            session.query(AccommodationExtra).filter(AccommodationExtra.booking_id == booking_id).delete()
            for ex in extras:
                extra = AccommodationExtra(booking_id=booking_id, **ex)
                session.add(extra)
        
        session.flush()
        
        # Re-query
        result = session.query(AccommodationBooking).options(
            joinedload(AccommodationBooking.extra_services)
        ).filter(AccommodationBooking.id == booking_id).first()
        
        if result in session:
            session.expunge(result)
            for ex in result.extra_services:
                if ex in session:
                    session.expunge(ex)
        return result


def delete_booking(booking_id: int) -> bool:
    """حذف حجز سكن بالكامل."""
    with get_session() as session:
        booking = session.query(AccommodationBooking).filter(AccommodationBooking.id == booking_id).first()
        if not booking:
            return False
        session.delete(booking)
        return True
