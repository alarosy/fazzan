"""
Arabic number-to-words conversion for financial documents.
تحويل المبالغ المالية إلى نص عربي — للاستخدام في الفواتير والسندات.
"""
from decimal import Decimal, ROUND_HALF_UP


# Units and teens
_ONES = [
    "", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة",
    "ستة", "سبعة", "ثمانية", "تسعة", "عشرة",
    "أحد عشر", "اثنا عشر", "ثلاثة عشر", "أربعة عشر", "خمسة عشر",
    "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر"
]

_TENS = [
    "", "", "عشرون", "ثلاثون", "أربعون", "خمسون",
    "ستون", "سبعون", "ثمانون", "تسعون"
]

_HUNDREDS = [
    "", "مئة", "مئتان", "ثلاثمئة", "أربعمئة", "خمسمئة",
    "ستمئة", "سبعمئة", "ثمانمئة", "تسعمئة"
]

_SCALES = [
    ("", ""),
    ("ألف", "آلاف"),
    ("مليون", "ملايين"),
    ("مليار", "مليارات"),
]


def _number_to_words_under_1000(n: int) -> str:
    """Convert integer 0-999 to Arabic words."""
    if n == 0:
        return ""
    
    parts = []
    
    hundreds = n // 100
    remainder = n % 100
    
    if hundreds > 0:
        parts.append(_HUNDREDS[hundreds])
    
    if remainder > 0:
        if remainder < 20:
            parts.append(_ONES[remainder])
        else:
            ones = remainder % 10
            tens = remainder // 10
            if ones > 0:
                parts.append(f"{_ONES[ones]} و{_TENS[tens]}")
            else:
                parts.append(_TENS[tens])
    
    return " و".join(parts)


def _integer_to_arabic(n: int) -> str:
    """Convert a non-negative integer to Arabic words."""
    if n == 0:
        return "صفر"
    
    if n < 0:
        return "سالب " + _integer_to_arabic(-n)
    
    parts = []
    scale_idx = 0
    
    while n > 0 and scale_idx < len(_SCALES):
        chunk = n % 1000
        n //= 1000
        
        if chunk > 0:
            chunk_words = _number_to_words_under_1000(chunk)
            singular, plural = _SCALES[scale_idx]
            
            if scale_idx == 0:
                parts.append(chunk_words)
            elif chunk == 1:
                parts.append(singular)
            elif chunk == 2:
                parts.append(f"{singular}ان" if singular else chunk_words)
            elif 3 <= chunk <= 10:
                parts.append(f"{chunk_words} {plural}")
            else:
                parts.append(f"{chunk_words} {singular}")
        
        scale_idx += 1
    
    parts.reverse()
    return " و".join(parts)


def amount_to_arabic_words(amount, currency: str = "دينار ليبي") -> str:
    """
    Convert a numeric amount to Arabic words with currency.
    يحوّل المبلغ الرقمي إلى نص عربي مع العملة.
    
    Args:
        amount: المبلغ الرقمي (int, float, Decimal, str)
        currency: اسم العملة (افتراضي: دينار ليبي)
    
    Returns:
        str: المبلغ بالحروف العربية مثل "ألف ومئتان وخمسون ديناراً ليبياً وخمسمئة درهم"
    
    Examples:
        >>> amount_to_arabic_words(1250.500)
        'ألف ومئتان وخمسون ديناراً ليبياً وخمسمئة درهم'
        >>> amount_to_arabic_words(0)
        'صفر ديناراً ليبياً'
    """
    # Normalize to Decimal with 3 decimal places (Libyan Dinar uses 3)
    if isinstance(amount, str):
        amount = Decimal(amount)
    elif isinstance(amount, (int, float)):
        amount = Decimal(str(amount))
    
    amount = amount.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    
    # Split into whole dinars and millimes (درهم)
    whole = int(amount)
    fractional = int((amount - whole) * 1000)
    
    # Build the text
    parts = []
    
    # Whole part
    whole_words = _integer_to_arabic(whole)
    
    # Currency name inflection (simplified)
    if currency == "دينار ليبي":
        currency_text = "ديناراً ليبياً"
        fraction_name = "درهم"
    else:
        currency_text = currency
        fraction_name = "جزء"
    
    parts.append(f"{whole_words} {currency_text}")
    
    # Fractional part
    if fractional > 0:
        frac_words = _integer_to_arabic(fractional)
        parts.append(f"{frac_words} {fraction_name}")
    
    return " و".join(parts)
