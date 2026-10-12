import re
import unicodedata


def make_code_part(value: str, length: int = 3) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Za-z0-9]", "", value)
    return value.upper()[:length] or "UNK"


def generate_converter_prefix(
    country: str,
    brand: str,
) -> str:
    country_code = make_code_part(country)
    brand_code = make_code_part(brand)

    return f"{country_code}-{brand_code}"