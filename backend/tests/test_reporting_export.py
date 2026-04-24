from docx.shared import RGBColor

from src.services.reporting_export import _get_reason_color_docx, _get_reason_color_pdf, _split_reason


def test_split_reason_with_colon():
    factor, result = _split_reason("rainfall: inside optimal range")
    assert factor == "rainfall"
    assert result == "inside optimal range"


def test_split_reason_without_colon():
    factor, result = _split_reason("suitable rainfall")
    assert factor == ""
    assert result == "suitable rainfall"


def test_split_reason_extra_colons():
    factor, result = _split_reason("rainfall: below minimum: by 200mm")
    assert factor == "rainfall"
    assert result == "below minimum: by 200mm"


def test_split_reason_strips_whitespace():
    factor, result = _split_reason("  ph :  inside range  ")
    assert factor == "ph"
    assert result == "inside range"


def test_get_reason_color_pdf_green():
    assert _get_reason_color_pdf("inside optimal range") == (0, 128, 0)
    assert _get_reason_color_pdf("exact match") == (0, 128, 0)
    assert _get_reason_color_pdf("plateau") == (0, 128, 0)


def test_get_reason_color_pdf_red():
    assert _get_reason_color_pdf("below minimum") == (220, 0, 0)
    assert _get_reason_color_pdf("above maximum") == (220, 0, 0)


def test_get_reason_color_pdf_amber():
    assert _get_reason_color_pdf("marginal") == (200, 120, 0)
    assert _get_reason_color_pdf("unknown result") == (200, 120, 0)


def test_get_reason_color_docx_green():
    assert _get_reason_color_docx("inside optimal range") == RGBColor(0, 128, 0)
    assert _get_reason_color_docx("exact match") == RGBColor(0, 128, 0)
    assert _get_reason_color_docx("plateau") == RGBColor(0, 128, 0)


def test_get_reason_color_docx_red():
    assert _get_reason_color_docx("below minimum") == RGBColor(220, 0, 0)
    assert _get_reason_color_docx("above maximum") == RGBColor(220, 0, 0)


def test_get_reason_color_docx_amber():
    assert _get_reason_color_docx("marginal") == RGBColor(200, 120, 0)
    assert _get_reason_color_docx("unknown result") == RGBColor(200, 120, 0)
