import random
import string

def generate_voucher_code(company_acronym: str, code_length: int = 6) -> str:
    """Generate unique voucher code using company acronym and random characters"""
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choice(chars) for _ in range(code_length))
    return f"{company_acronym}-{random_str}"