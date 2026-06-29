"""
Models package — imports Base and all model classes.
حزمة النماذج — تستورد Base وجميع الفئات لتسجيلها مع SQLAlchemy.
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models to register them with Base.metadata
# This ensures Alembic and create_all() can discover all tables
from models.partnership import Partnership    # noqa: E402, F401
from models.project import Project            # noqa: E402, F401
from models.hall import Hall                  # noqa: E402, F401
from models.employee import Employee          # noqa: E402, F401
from models.client import Client              # noqa: E402, F401
from models.training_program import TrainingProgram  # noqa: E402, F401
from models.trainee import Trainee            # noqa: E402, F401
from models.trainer import Trainer            # noqa: E402, F401
from models.course_enrollment import CourseEnrollment  # noqa: E402, F401
from models.consultant import Consultant              # noqa: E402, F401
from models.catering import CateringOrder, CateringExtra  # noqa: E402, F401
from models.accommodation import AccommodationBooking, AccommodationExtra  # noqa: E402, F401
from models.market_research import MarketResearch      # noqa: E402, F401
from models.financial_proposal import FinancialProposal  # noqa: E402, F401
from models.service_line_item import ServiceLineItem  # noqa: E402, F401
from models.invoice import Invoice                    # noqa: E402, F401
from models.voucher import Voucher                    # noqa: E402, F401
from models.expense import Expense                    # noqa: E402, F401
from models.asset import Asset                        # noqa: E402, F401
from models.cash_register import CashRegister          # noqa: E402, F401
from models.contract import Contract                  # noqa: E402, F401
from models.partner import Partner                    # noqa: E402, F401

