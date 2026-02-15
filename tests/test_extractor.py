import sys
sys.path.append('src')

from processing.extractor import extract_words

def test_extract_words_basic():
    text = "Hallo, wie geht es dir? Ich lerne Deutsch."
    words = extract_words(text)
    lemmas = [w[0] for w in words]
    # La fonction retourne "lernen" (lemmatisé) et "deutsch"
    assert "lernen" in lemmas
    assert "deutsch" in lemmas
    assert len(lemmas) >= 2
