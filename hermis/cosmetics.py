import os
from functools import lru_cache
from typing import Any

# Import clean_content para sanitização de texto Unicode
from .textutils import clean_content

# Definições de cores baseadas em Material Design
# Estrutura: {genero: {tipo: hex}}
MATERIAL_COLORS: dict[str, dict[str, str]] = {
    "política": {"primary": "#1976D2", "light": "#BBDEFB", "dark": "#0D47A1", "text": "#FFFFFF"},
    "fantasia": {"primary": "#303F9F", "light": "#C5CAE9", "dark": "#1A237E", "text": "#FFFFFF"},
    "científico": {"primary": "#00796B", "light": "#B2DFDB", "dark": "#004D40", "text": "#FFFFFF"},
    "história": {"primary": "#D32F2F", "light": "#FFCDD2", "dark": "#B71C1C", "text": "#FFFFFF"},
    "biografia": {"primary": "#5D4037", "light": "#D7CCC8", "dark": "#3E2723", "text": "#FFFFFF"},
    "autoajuda": {"primary": "#FBC02D", "light": "#FFF9C4", "dark": "#FF8F00", "text": "#000000"},
    "filosofia": {"primary": "#7B1FA2", "light": "#E1BEE7", "dark": "#4A148C", "text": "#FFFFFF"},
    "mistério": {"primary": "#455A64", "light": "#CFD8DC", "dark": "#263238", "text": "#FFFFFF"},
    "romance": {"primary": "#C2185B", "light": "#F8BBD0", "dark": "#880E4F", "text": "#FFFFFF"},
    "infantil": {"primary": "#8BC34A", "light": "#DCEDC8", "dark": "#558B2F", "text": "#000000"},
    "educação": {"primary": "#EF6C00", "light": "#FFECB3", "dark": "#E65100", "text": "#FFFFFF"},
    "economia": {"primary": "#607D8B", "light": "#CFD8DC", "dark": "#37474F", "text": "#FFFFFF"},
    "saúde": {"primary": "#66BB6A", "light": "#C8E6C9", "dark": "#388E3C", "text": "#FFFFFF"},
    "culinária": {"primary": "#FF7043", "light": "#FFCCBC", "dark": "#BF360C", "text": "#FFFFFF"},
    "viagem": {"primary": "#039BE5", "light": "#B3E5FC", "dark": "#01579B", "text": "#FFFFFF"},
    "arte": {"primary": "#E91E63", "light": "#F8BBD0", "dark": "#C2185B", "text": "#FFFFFF"},
    "tecnologia": {"primary": "#424242", "light": "#EEEEEE", "dark": "#212121", "text": "#FFFFFF"},
    "geral": {"primary": "#757575", "light": "#E0E0E0", "dark": "#424242", "text": "#FFFFFF"},
}


@lru_cache(maxsize=64)
def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Converte string hex (#RRGGBB) para tupla (R, G, B) com cache.

    Otimização: Cache LRU evita reconversões das mesmas cores.
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return (0, 0, 0)  # Fallback para preto
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def setup_fonts(font_path: str) -> tuple[Any, str]:
    """
    Cria instância FPDF limpa; a dependência é importada sob demanda.
    """
    from fpdf import FPDF

    pdf = FPDF()
    font_name = _get_font_name_cached(font_path)

    if font_name != "Arial":
        try:
            pdf.add_font(font_name, "", font_path, uni=True)
            try:
                pdf.add_font(font_name, "B", font_path, uni=True)
            except Exception:
                pass
            try:
                pdf.add_font(font_name, "I", font_path, uni=True)
            except Exception:
                pass
        except Exception:
            font_name = "Arial"

    return pdf, font_name


def _font_registered(pdf: Any, family: str, style: str = "") -> bool:
    return f"{family.lower()}{style.upper()}" in getattr(pdf, "fonts", {})


@lru_cache(maxsize=16)
def _get_font_name_cached(font_path: str) -> str:
    """Verifica e armazena em cache se a fonte pode ser carregada."""
    try:
        from fpdf import FPDF

        test_pdf = FPDF()
        test_pdf.add_font("CustomFont", "", font_path, uni=True)
        return "CustomFont"
    except Exception:
        return "Arial"


def create_cover_page(pdf: Any, author: str, title: str, genre: str, font_path: str):
    """
    Gera uma capa estilizada baseada no gênero do livro.

    Otimizações:
    - Usa cache em hex_to_rgb
    - Normaliza gênero uma vez
    - Sanitiza texto para Latin-1 se Arial for utilizado como fallback
    """
    # Normalização e busca de cores (suporta gêneros com e sem acento)
    genre_clean = clean_content(genre).lower() if genre else "geral"
    colors = MATERIAL_COLORS.get(genre_clean, MATERIAL_COLORS["geral"])

    # Pre-converte todas as cores necessárias (com cache)
    bg_rgb = hex_to_rgb(colors["primary"])
    text_rgb = hex_to_rgb(colors["text"])

    # Setup de fonte (tenta registrar customizada)
    pdf.add_page()
    active_font = "Arial"
    title_style = "B"
    genre_style = "I"
    if font_path and os.path.exists(font_path):
        try:
            if not _font_registered(pdf, "CustomFont"):
                pdf.add_font("CustomFont", "", font_path, uni=True)
            try:
                if not _font_registered(pdf, "CustomFont", "B"):
                    pdf.add_font("CustomFont", "B", font_path, uni=True)
            except Exception:
                title_style = ""
            try:
                if not _font_registered(pdf, "CustomFont", "I"):
                    pdf.add_font("CustomFont", "I", font_path, uni=True)
            except Exception:
                genre_style = ""
            active_font = "CustomFont"
        except Exception:
            active_font = "Arial"

    # 1. Fundo
    pdf.set_fill_color(*bg_rgb)
    pdf.rect(0, 0, pdf.w, pdf.h, "F")

    # 2. Configuração de Texto
    pdf.set_text_color(*text_rgb)

    # Cálculo de posições verticais (Responsividade básica para A4)
    h = pdf.h

    # Preparação dos textos sanitizados
    title_str = clean_content(title)
    author_str = clean_content(author)
    genre_str = clean_content(genre.capitalize()) if genre else ""

    if active_font == "Arial":
        title_str = title_str.encode("latin-1", "replace").decode("latin-1")
        author_str = author_str.encode("latin-1", "replace").decode("latin-1")
        genre_str = genre_str.encode("latin-1", "replace").decode("latin-1")

    # 3. Título (Centralizado e Grande)
    pdf.set_font(active_font, title_style, 48)
    pdf.set_xy(10, h * 0.3)
    pdf.multi_cell(0, 20, title_str, align="C")

    # 4. Autor (Menor, abaixo do título)
    pdf.set_font(active_font, "", 24)
    pdf.set_xy(10, pdf.get_y() + 20)
    pdf.multi_cell(0, 10, author_str, align="C")

    # 5. Gênero (Rodapé)
    if genre and genre.lower() != "geral":
        pdf.set_font(active_font, genre_style, 16)
        pdf.set_xy(10, h - 40)
        pdf.multi_cell(0, 10, genre_str, align="C")

    # Reseta cores para a próxima página de conteúdo.
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)


# Função auxiliar para obter paleta de cores (para debugging ou UI)
def get_genre_colors(genre: str) -> dict[str, str]:
    """Retorna paleta de cores para um gênero específico."""
    genre_key = genre.lower() if genre else "geral"
    return MATERIAL_COLORS.get(genre_key, MATERIAL_COLORS["geral"])


# Função auxiliar para validar se gênero existe
def is_valid_genre(genre: str) -> bool:
    """Verifica se gênero é válido."""
    return (genre or "").lower() in MATERIAL_COLORS
