"""
AI Report Service — خدمات التحليل المالي والتقارير الذكية المدعومة بالذكاء الاصطناعي (AI Insights).
"""
from decimal import Decimal
from core.database import get_session
from models.project import Project
from models.contract import Contract
from models.cash_register import CashRegister
from models.enums import RegisterType


def generate_ai_financial_report() -> str:
    """
    توليد تقرير تحليل مالي وتوصيات ذكية باللغة العربية بناءً على البيانات الحية.
    """
    with get_session() as session:
        # Fetch totals
        projects = session.query(Project).filter(Project.is_deleted == False).all()  # noqa: E712
        contracts = session.query(Contract).filter(Contract.is_deleted == False).all()  # noqa: E712
        
        # Calculate cash logs
        logs = session.query(CashRegister).all()
        total_rev = Decimal("0.00")
        total_exp = Decimal("0.00")
        for log in logs:
            if log.transaction_type == "in":
                total_rev += log.amount
            else:
                total_exp += log.amount
                
        net_profit = total_rev - total_exp
        
        # Active contracts sum
        active_contracts_val = sum(c.value for c in contracts if c.status.name == "ACTIVE")
        
        # Budget spent ratios
        project_details = []
        warning_projects = []
        for p in projects:
            allocated = p.budget_allocated or p.budget or Decimal("0.00")
            spent = p.budget_spent or Decimal("0.00")
            ratio = (spent / allocated * 100) if allocated > 0 else 0
            project_details.append(f" - {p.name}: تم استهلاك {spent:.2f} LYD من أصل {allocated:.2f} LYD ({ratio:.1f}%)")
            if ratio > 90:
                warning_projects.append(p.name)

        # AI Insights synthesis
        insights = []
        insights.append("=== 📊 تقرير التحليل المالي والتقارير الذكية (AI Insights) ===")
        insights.append(f"تاريخ التوليد: {dt_now()}")
        insights.append("\n--- [1] ملخص الأداء المالي التراكمي ---")
        insights.append(f" - إجمالي الإيرادات المسجلة بالخزينة: {total_rev:.2f} LYD")
        insights.append(f" - إجمالي المصروفات التشغيلية والرواتب: {total_exp:.2f} LYD")
        insights.append(f" - صافي التدفق النقدي والأرباح: {net_profit:.2f} LYD")
        
        # Health status check
        if net_profit > 0:
            insights.append(" - الحالة المالية العامة: 🟢 مستقرة وإيجابية (فائض سيولة).")
        elif net_profit < 0:
            insights.append(" - الحالة المالية العامة: 🔴 عجز مالي مؤقت (زيادة في المصروفات التشغيلية).")
        else:
            insights.append(" - الحالة المالية العامة: 🟡 ركود مالي (أرصدة الخزينة صفرية أو متوازنة تماماً).")

        insights.append("\n--- [2] تحليل العقود والمشاريع الجارية ---")
        insights.append(f" - عدد العقود النشطة: {len([c for c in contracts if c.status.name == 'ACTIVE'])}")
        insights.append(f" - القيمة الإجمالية للعقود الجارية: {active_contracts_val:.2f} LYD")
        insights.append(" - تفاصيل استهلاك ميزانيات المشاريع:")
        if project_details:
            insights.extend(project_details)
        else:
            insights.append("   (لا توجد مشاريع مسجلة حالياً)")

        insights.append("\n--- [3] التوصيات والتحليل التنبئي (AI Recommendations) ---")
        
        # Financial health triggers
        if net_profit > 0 and len(warning_projects) == 0:
            insights.append(" ✅ أداء ممتاز. يُنصح باستثمار الفائض النقدي في توسعة القاعات التدريبية أو شراء أصول جديدة.")
        
        if warning_projects:
            insights.append(f" ⚠️ تنبيه حرج: المشاريع التالية تجاوزت 90% من ميزانيتها المحددة: ({', '.join(warning_projects)}).")
            insights.append("    التوصية: مراجعة فواتير ومصروفات هذه المشاريع فوراً، وإيقاف شحن رواتب إضافية عليها.")
            
        if active_contracts_val < total_exp:
            insights.append(" 📈 تنبيه تسويقي: حجم العقود الجارية أقل من إجمالي المصاريف التشغيلية.")
            insights.append("    التوصية: تعزيز جهود المبيعات لزيادة العقود الاستشارية وحجوزات القاعات لتغطية الأعباء.")
            
        if not warning_projects and active_contracts_val >= total_exp:
            insights.append(" 👍 مؤشرات الكفاءة التشغيلية ممتازة. النظام يسير في منحنى تصاعدي صحي.")

        return "\n".join(insights)


def dt_now() -> str:
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
