# Utility functions for Asian script detection

def is_han(char):
    codepoint = ord(char)
    # CJK Unified Ideographs
    return 0x4E00 <= codepoint <= 0x9FFF

def is_hangul(char):
    codepoint = ord(char)
    # Hangul Syllables
    return 0xAC00 <= codepoint <= 0xD7AF

def is_hiragana(char):
    codepoint = ord(char)
    return 0x3040 <= codepoint <= 0x309F

def is_katakana(char):
    codepoint = ord(char)
    return 0x30A0 <= codepoint <= 0x30FF

def is_asian(char):
    return is_han(char) or is_hangul(char) or is_hiragana(char) or is_katakana(char)
