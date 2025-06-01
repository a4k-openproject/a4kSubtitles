import unicodedata

# Unicode punctuation
PUNCTUATION_CATEGORIES = {'Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po'}
# Unicode separator
SEPARATOR_CATEGORIES = {'Zs', 'Zl', 'Zp'}
# Unicode control
CONTROL_CATEGORIES = {'Cc', 'Cf', 'Cs', 'Co', 'Cn'}

# Latin script unicode block ranges (partial, for basic Latin and Latin-1 Supplement)
LATIN_RANGES = [
    (0x0041, 0x005A),  # A-Z
    (0x0061, 0x007A),  # a-z
    (0x00C0, 0x00D6),  # Latin-1 Supplement
    (0x00D8, 0x00F6),
    (0x00F8, 0x00FF),
]

def is_punctuation(char):
    return unicodedata.category(char) in PUNCTUATION_CATEGORIES

def is_separator(char):
    return unicodedata.category(char) in SEPARATOR_CATEGORIES

def is_control(char):
    return unicodedata.category(char) in CONTROL_CATEGORIES

def is_latin(char):
    codepoint = ord(char)
    return any(start <= codepoint <= end for start, end in LATIN_RANGES)

def remove_punctuation_separator_control(text):
    """
    Remove all punctuation, separator, and control characters from text.
    """
    return ''.join(c for c in text if not (is_punctuation(c) or is_separator(c) or is_control(c)))
