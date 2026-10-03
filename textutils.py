"""
Utilitários de processamento de texto - Centralizado para evitar circular imports.
"""

import re
import unicodedata

# Compilar regex uma vez (otimização)
THINK_TAG_PATTERN = re.compile(r"<think>.*?</think>", flags=re.DOTALL)
CONTROL_CHARS_PATTERN = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\u009F]")

# Mapeamento estático e global (Otimização O(1) na inicialização)
_TRANSLATION_TABLE = str.maketrans(
    {
        "\u00a0": " ",
        "\u200b": "",
        "\ufeff": "",
        "\u2013": "-",
        "\u2014": "-",
        "\u2015": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "*",
        "\u00ab": '"',
        "\u00bb": '"',
        "\u2026": "...",  # Otimização: 1:N mapeamento elimina .replace()
        # Mapeamento preemptivo O(1) dos piores ofensores do Latin-1:
        "\u25a0": "-",
        "\u25cf": "*",
        "\u25cb": "*",
        "\u2023": ">",
        # Superscript characters (⁰¹²³⁴⁵⁶⁷⁸⁹)
        "\u2070": "0",
        "\u00b9": "1",
        "\u00b2": "2",
        "\u00b3": "3",
        "\u2074": "4",
        "\u2075": "5",
        "\u2076": "6",
        "\u2077": "7",
        "\u2078": "8",
        "\u2079": "9",
        # Subscript characters (₀₁₂₃⁴₅₆₇₈₉)
        "\u2080": "0",
        "\u2081": "1",
        "\u2082": "2",
        "\u2083": "3",
        "\u2084": "4",
        "\u2085": "5",
        "\u2086": "6",
        "\u2087": "7",
        "\u2088": "8",
        "\u2089": "9",
        # Fractions and other common unicode
        "\u00bc": "1/4",
        "\u00bd": "1/2",
        "\u00be": "3/4",
        "\u2150": "1/7",
        "\u2151": "1/9",
        "\u2152": "1/10",
        "\u2153": "1/3",
        "\u2154": "2/3",
        "\u2155": "1/5",
        "\u2156": "2/5",
        "\u2157": "3/5",
        "\u2158": "4/5",
        "\u2159": "1/6",
        "\u215a": "5/6",
        "\u215b": "1/8",
        "\u215c": "3/8",
        "\u215d": "5/8",
        "\u215e": "7/8",
    }
)


def strip_think_tags(text: str) -> str:
    """Remove blocos de pensamento <think>...</think> emitidos por LLMs de raciocínio."""
    if not text:
        return ""
    return THINK_TAG_PATTERN.sub("", text)


def clean_content(text: str) -> str:
    """Limpa conteúdo em passagem única via C-level str.translate e regex compilado."""
    if not text:
        return ""
    text = strip_think_tags(text)
    text = text.translate(_TRANSLATION_TABLE)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")
    return CONTROL_CHARS_PATTERN.sub("", text)


def normalize_text(text: str) -> str:
    """Normaliza texto de forma eficiente."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = clean_content(text)
    return text.strip()
