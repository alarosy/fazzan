"""
Accommodation models — خدمات السكن والإقامة.
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from models import Base


class AccommodationBooking(Base):
    """
    نموذج حجز السكن.
    يتابع توفير الشقق السكنية والضيافة للمتدربين والمحاضرين.
    """
    __tablename__ = 'accommodation_bookings'

    id = Column(Integer, primary_key=True)
    proposal_id = Column(Integer, ForeignKey('financial_proposals.id'), nullable=True) # ForeignKey للمرحلة D
    apartment_type = Column(String(5), nullable=False)  # "A" / "B" / "C"
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)

    # Relationships
    extra_services = relationship('AccommodationExtra', back_populates='booking', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<AccommodationBooking(id={self.id}, apartment_type='{self.apartment_type}')>"


class AccommodationExtra(Base):
    """
    الخدمات الإضافية المرفقة بحجز السكن.
    مثال: خدمة تنظيف إضافية، إنترنت سريع، غسيل ملابس.
    """
    __tablename__ = 'accommodation_extras'

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('accommodation_bookings.id'), nullable=False)
    service_name = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    # Relationships
    booking = relationship('AccommodationBooking', back_populates='extra_services')

    def __repr__(self):
        return f"<AccommodationExtra(id={self.id}, service_name='{self.service_name}')>"
