import os
import threading
import warnings
from collections.abc import Callable

try:
    import ebooklib
    from ebooklib import epub
except ImportError:
    ebooklib = None
    epub = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import mobireader
except ImportError:
    mobireader = None


class OCRManager:
    """Singleton otimizado para gerenciar dependências OCR com lazy loading."""

    _reader = None
    _fitz = None
    _pil_image = None
    _easyocr = None
    _has_attempted_load = False
    _lock = threading.RLock()

    @classmethod
    def load_dependencies(cls):
        """Carrega dependências apenas uma vez (lazy loading)."""
        with cls._lock:
            if cls._has_attempted_load:
                return cls._fitz, cls._pil_image, cls._easyocr

            try:
                import fitz

                cls._fitz = fitz
            except ImportError as e:
                print(f"Aviso: PyMuPDF/fitz ausente: {e}")

            try:
                from PIL import Image

                cls._pil_image = Image
            except ImportError as e:
                print(f"Aviso: PIL ausente: {e}")

            try:
                import easyocr

                cls._easyocr = easyocr
            except ImportError as e:
                print(f"Aviso: EasyOCR ausente; PDFs nativos ainda serão lidos: {e}")

            cls._has_attempted_load = True
            return cls._fitz, cls._pil_image, cls._easyocr

    @classmethod
    def get_reader(cls):
        """Obtém reader OCR com inicialização lazy e verificação de CUDA."""
        _fitz_mod, _, easyocr_mod = cls.load_dependencies()
        if not easyocr_mod:
            return None

        with cls._lock:
            if cls._reader is None:
                use_gpu = False
                try:
                    import torch

                    use_gpu = torch.cuda.is_available()
                except Exception:
                    use_gpu = False

                print(f"Inicializando modelo OCR Local (EasyOCR) [GPU={use_gpu}]...")
                try:
                    cls._reader = easyocr_mod.Reader(["pt", "en"], gpu=use_gpu, verbose=False)
                except Exception as e:
                    print(
                        f"Aviso ao inicializar EasyOCR com GPU={use_gpu}: {e}. Tentando modo CPU..."
                    )
                    try:
                        cls._reader = easyocr_mod.Reader(["pt", "en"], gpu=False, verbose=False)
                    except Exception as err:
                        print(f"Erro ao inicializar EasyOCR em modo CPU: {err}")
                        cls._reader = None

            return cls._reader


def _extract_text_from_html(html_content) -> str:
    """Extrai texto de HTML/bytes preservando parágrafos."""
    if not BeautifulSoup or not html_content:
        return ""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        # Preserva quebras de linha entre elementos de bloco
        return soup.get_text(separator="\n\n").strip()
    except Exception:
        return ""


def epub_to_text(epub_path: str, update_log_callback: Callable | None = None) -> str:
    """Extrai texto de EPUB respeitando a ordem de leitura do spine."""
    if not all([ebooklib, epub, BeautifulSoup]):
        missing = []
        if not ebooklib or not epub:
            missing.append("ebooklib")
        if not BeautifulSoup:
            missing.append("beautifulsoup4")
        msg = f"[AVISO] Dependências ausentes para ler EPUB: {', '.join(missing)}.\n"
        if update_log_callback:
            update_log_callback(msg)
        else:
            print(msg)
        return ""

    if not os.path.exists(epub_path):
        if update_log_callback:
            update_log_callback(f"[ERRO EPUB] Arquivo não encontrado: {epub_path}\n")
        return ""

    text_parts = []

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            book = epub.read_epub(epub_path)

        # Tenta obter os itens na ordem do spine (ordem real de leitura)
        doc_items = []
        if hasattr(book, "spine") and book.spine:
            for item_ref in book.spine:
                item_id = item_ref[0] if isinstance(item_ref, (tuple, list)) else item_ref
                item = book.get_item_with_id(item_id)
                if item and item.get_type() == ebooklib.ITEM_DOCUMENT:
                    doc_items.append(item)

        # Fallback caso o spine falhe ou esteja incompleto
        if not doc_items:
            doc_items = [
                item for item in book.get_items() if item.get_type() == ebooklib.ITEM_DOCUMENT
            ]

        for item_index, item in enumerate(doc_items, 1):
            try:
                content = item.get_content()
                extracted = _extract_text_from_html(content)
                if extracted:
                    text_parts.append(extracted)
            except Exception as exc:
                if update_log_callback:
                    update_log_callback(
                        f"[AVISO EPUB] Não foi possível extrair o item {item_index}: {exc}\n"
                    )

    except Exception as e:
        if update_log_callback:
            update_log_callback(f"[ERRO EPUB] Falha ao extrair texto do EPUB: {e}\n")
        return ""

    return "\n\n".join(text_parts).strip()


def mobi_to_text(mobi_path: str, update_log_callback: Callable | None = None) -> str:
    """Extrai texto de MOBI com processamento otimizado."""
    if not all([mobireader, BeautifulSoup]):
        missing = []
        if not mobireader:
            missing.append("mobireader")
        if not BeautifulSoup:
            missing.append("beautifulsoup4")
        msg = f"[AVISO] Dependências ausentes para ler MOBI: {', '.join(missing)}.\n"
        if update_log_callback:
            update_log_callback(msg)
        else:
            print(msg)
        return ""

    if not os.path.exists(mobi_path):
        if update_log_callback:
            update_log_callback(f"[ERRO MOBI] Arquivo não encontrado: {mobi_path}\n")
        return ""

    text_parts = []

    try:
        book = mobireader.MobiFile(mobi_path)

        for record_index, record in enumerate(book.read_text_records(), 1):
            try:
                html_content = record
                extracted = _extract_text_from_html(html_content)
                if extracted:
                    text_parts.append(extracted)
            except Exception as exc:
                if update_log_callback:
                    update_log_callback(
                        f"[AVISO MOBI] Não foi possível extrair o registro {record_index}: {exc}\n"
                    )

    except Exception as e:
        if update_log_callback:
            update_log_callback(f"[ERRO MOBI] Falha ao extrair texto do MOBI: {e}\n")
        return ""

    return "\n\n".join(text_parts).strip()


def pdf_to_text_with_ocr(
    pdf_path: str,
    update_log_callback: Callable | None = None,
    max_workers: int = 4,
    ocr_threshold: int = 50,
) -> str:
    """
    Extrai texto de PDF com OCR seguro e baixo pico de memória.

    Args:
        pdf_path: Caminho do arquivo PDF
        update_log_callback: Callback para logs
        max_workers: Mantido por compatibilidade; processamento atual é sequencial
            para limitar pico de memória.
        ocr_threshold: Limite de caracteres para disparar OCR (padrão: 50)
    """
    fitz_mod, _, easyocr_mod = OCRManager.load_dependencies()

    if not fitz_mod:
        if update_log_callback:
            update_log_callback("Erro: PyMuPDF/fitz não encontrado para ler PDF.\n")
        return ""

    if not os.path.exists(pdf_path):
        return ""

    doc = None
    try:
        reader = OCRManager.get_reader() if easyocr_mod else None
        doc = fitz_mod.open(pdf_path)
        total_pages = len(doc)
        if update_log_callback:
            update_log_callback(f"Processando PDF ({total_pages} páginas)...\n")

        if total_pages == 0:
            return ""

        page_texts = []
        ocr_count = 0

        for page_num, page in enumerate(doc):
            text = page.get_text("text")

            if reader and len(text.strip()) < ocr_threshold:
                try:
                    pix = page.get_pixmap(dpi=300)
                    image_bytes = pix.tobytes("png")
                    del pix
                    ocr_results = reader.readtext(image_bytes, detail=0, paragraph=True)
                    if ocr_results:
                        text = "\n".join(ocr_results)
                    ocr_count += 1
                except Exception as e:
                    if update_log_callback:
                        update_log_callback(f"Aviso: OCR falhou na página {page_num + 1}: {e}\n")

            page_texts.append(text)

        doc.close()
        doc = None

        if update_log_callback and ocr_count > 0:
            update_log_callback(f"OCR aplicado em {ocr_count} páginas.\n")

        # Reconstrói texto na ordem correta
        full_text_parts = []
        for text in page_texts:
            if text:
                full_text_parts.append(text)
                full_text_parts.append("<docpagebreak/>")

        return "\n\n".join(full_text_parts).strip()

    except Exception as e:
        if update_log_callback:
            update_log_callback(f"Erro no processamento do PDF: {e}\n")
        return ""
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass
