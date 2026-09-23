import re
from decimal import Decimal, InvalidOperation


def validar_email(email):
    if not email:
        return False

    padrao = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.match(padrao, email) is not None


def converter_preco(valor):
    try:
        if valor is None or valor == "":
            raise ValueError

        preco = Decimal(str(valor))

        if preco < 0:
            raise ValueError

        return preco

    except (InvalidOperation, ValueError):
        return None


def converter_inteiro(valor):
    try:
        if valor is None or valor == "":
            return None

        return int(valor)

    except (ValueError, TypeError):
        return None
