import os
import google.generativeai as genai
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import messagebox  


def filter_alphabets(text):
    return ''.join([c.upper() for c in text if c.isalpha()])

def index_of_coincidence(text):
    freq = {}
    n = len(text)
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    ic = 0.0
    for count in freq.values():
        ic += count * (count - 1)
    if n <= 1:
        return 0
    ic /= n * (n - 1)
    return ic

def guess_key_length(ciphertext, max_length=20):
    filtered_text = filter_alphabets(ciphertext)
    max_length = min(max_length, len(filtered_text) // 2)
    best_ic = 0
    best_length = 1
    for L in range(1, max_length + 1):
        groups = [filtered_text[i::L] for i in range(L)]
        total_ic = 0.0
        valid_groups = 0
        for group in groups:
            if len(group) >= 2:
                total_ic += index_of_coincidence(group)
                valid_groups += 1
        avg_ic = total_ic / valid_groups if valid_groups else 0
        if avg_ic > best_ic:
            best_ic, best_length = avg_ic, L
    return best_length

english_freq = {
    'A': 0.08167, 'B': 0.01492, 'C': 0.02782, 'D': 0.04258,
    'E': 0.12702, 'F': 0.02228, 'G': 0.02015, 'H': 0.06094,
    'I': 0.06966, 'J': 0.00153, 'K': 0.00772, 'L': 0.04025,
    'M': 0.02406, 'N': 0.06749, 'O': 0.07507, 'P': 0.01929,
    'Q': 0.00095, 'R': 0.05987, 'S': 0.06327, 'T': 0.09056,
    'U': 0.02758, 'V': 0.00978, 'W': 0.02360, 'X': 0.00150,
    'Y': 0.01974, 'Z': 0.00074
}

russian_freq = {
    'А': 7.64,  'Б': 2.01,  'В': 4.38,  'Г': 1.72,
    'Д': 3.09,  'Е': 8.75,  'Ж': 1.01,  'З': 1.48,
    'И': 7.09,  'Й': 1.21,  'К': 3.30,  'Л': 4.96,
    'М': 3.17,  'Н': 6.78,  'О': 11.18, 'П': 2.47,
    'Р': 4.23,  'С': 4.97,  'Т': 6.09,  'У': 2.22,
    'Ф': 0.21,  'Х': 0.95,  'Ц': 0.39,  'Ч': 1.40,
    'Ш': 0.72,  'Щ': 0.30,  'Ъ': 0.02,  'Ы': 2.36,
    'Ь': 1.84,  'Э': 0.36,  'Ю': 0.47,  'Я': 1.96
}
English_Alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
Russian_Alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

def detect_language(text):
    en_count = sum(1 for c in text if c in English_Alphabet)
    ru_count = sum(1 for c in text if c in Russian_Alphabet)
    return 'en' if en_count > ru_count else 'ru'

def frequency_analysis(text, lang):
    alphabet = English_Alphabet if lang == 'en' else Russian_Alphabet
    freq = english_freq if lang == 'en' else russian_freq
    best_shift, best_score = 0, 0
    for shift in range(len(alphabet)):
        score = 0.0
        for c in text:
            if c not in alphabet:
                continue
            decrypted_char = alphabet[(alphabet.index(c) - shift) % len(alphabet)]
            score += freq.get(decrypted_char, 0)
        if score > best_score:
            best_shift, best_score = shift, score
    return best_shift

def get_key(ciphertext, key_length):
    filtered_text = filter_alphabets(ciphertext)
    key = []
    for i in range(key_length):
        group = filtered_text[i::key_length]
        lang = detect_language(group)
        lang_group = [c for c in group if c in (English_Alphabet if lang == 'en' else Russian_Alphabet)]
        if not lang_group:
            key.append((0, 'en'))  
            continue
        shift = frequency_analysis(lang_group, lang)
        key.append((shift, lang))
    return key

def shifts_to_key(shifts):
    key = []
    for shift, lang in shifts:
        alphabet = English_Alphabet if lang == 'en' else Russian_Alphabet
        key.append(alphabet[shift % len(alphabet)])
    return ''.join(key)

def vigenere_decrypt(ciphertext, key):
    key_shifts = []
    for k_char in key:
        if k_char.upper() in English_Alphabet:
            key_shifts.append( (English_Alphabet.index(k_char.upper()), 'en') )
        else:
            key_shifts.append( (Russian_Alphabet.index(k_char.upper()), 'ru') )
    
    plaintext = []
    key_idx = 0
    for c in ciphertext:
        if c.upper() in English_Alphabet:
            lang = 'en'
            alphabet = English_Alphabet
        elif c.upper() in Russian_Alphabet:
            lang = 'ru'
            alphabet = Russian_Alphabet
        else:
            plaintext.append(c)
            continue
        
        shift, key_lang = key_shifts[key_idx % len(key_shifts)]
        if lang != key_lang:
            shift = shift % len(alphabet)
        
        orig_idx = alphabet.index(c.upper())
        decrypted_char = alphabet[(orig_idx - shift) % len(alphabet)]
        plaintext.append(decrypted_char.lower() if c.islower() else decrypted_char)
        key_idx += 1
    
    return ''.join(plaintext)

def vigenere_text(ciphertext):
    key_length = guess_key_length(ciphertext)
    key_shifts = get_key(ciphertext, key_length)
    key = shifts_to_key(key_shifts)
    plaintext = vigenere_decrypt(ciphertext, key)
    return plaintext

def atbash_text(ciphertext):
    original_lower = 'abcdefghijklmnopqrstuvwxyz'
    reversed_lower = original_lower[::-1]
    original_upper = original_lower.upper()
    reversed_upper = original_upper[::-1]
    
    original_ru_lower = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    reversed_ru_lower = original_ru_lower[::-1]
    original_ru_upper = original_ru_lower.upper()
    reversed_ru_upper = original_ru_upper[::-1]
    
    mapping = {
        **{o: r for o, r in zip(original_lower + original_upper, reversed_lower + reversed_upper)},
        **{o: r for o, r in zip(original_ru_lower + original_ru_upper, reversed_ru_lower + reversed_ru_upper)}
    }
    
    return ''.join([mapping.get(char, char) for char in ciphertext])

def caesar_text(ciphertext):
    results = []
    for key in range(0, 32):
        decrypted = []
        for char in ciphertext:
            char_code = ord(char)
            base, alphabet_length = None, 0
            
            if 'А' <= char <= 'Я':
                base = ord('А')
                alphabet_length = 32
            elif 'а' <= char <= 'я':
                base = ord('а')
                alphabet_length = 32
            elif 'A' <= char <= 'Z':
                base = ord('A')
                alphabet_length = 26
            elif 'a' <= char <= 'z':
                base = ord('a')
                alphabet_length = 26
            
            if base is not None:
                shifted = (char_code - base - key) % alphabet_length
                decrypted_char = chr(base + shifted)
                decrypted.append(decrypted_char)
            else:
                decrypted.append(char) 
        
        results.append(''.join(decrypted))
    return results

def process_text():
    api_key = api_key_entry.get()
    if not api_key:
        messagebox.showerror("Ошибка", "Введите API ключ")
        return
    
    ciphertext = entry.get()
    if not ciphertext:
        messagebox.showerror("Ошибка", "Введите шифротекст")
        return

    try:
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=generation_config,
        )
        chat_session = model.start_chat(history=[])
        
        
        if ciphertext[-1] not in ".!?":
            ciphertext += "."
        
        vigenere_result = vigenere_text(ciphertext)
        atbash_result = atbash_text(ciphertext)
        caesar_results = "".join(caesar_text(ciphertext))
        
        response = chat_session.send_message(
            f"Есть ли среди следующих текстов читаемый для человека? Если да, то выведи его и ничего больше: "
            f"{vigenere_result}{atbash_result}{caesar_results}"
        )
        
        result_text.configure(state='normal')
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, response.text)
        result_text.configure(state='disabled')

    except Exception as e:
        messagebox.showerror("Ошибка API", f"Произошла ошибка: {str(e)}")

def paste_from_clipboard():
    try:
        clipboard_text = root.clipboard_get()
        entry.delete(0, tk.END)
        entry.insert(tk.END, clipboard_text)
    except tk.TclError:
        messagebox.showwarning("Ошибка", "Буфер обмена пуст или содержит не текст")

root = tk.Tk()
root.title("Crypto Analyzer")
root.geometry("600x450")

api_frame = ttk.Frame(root)
api_frame.pack(padx=10, pady=5, fill=tk.X)

ttk.Label(api_frame, text="API Key:").pack(side=tk.LEFT)
api_key_entry = ttk.Entry(api_frame, width=50, show="*")
api_key_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

input_frame = ttk.Frame(root)
input_frame.pack(padx=10, pady=5, fill=tk.X)

ttk.Label(input_frame, text="Ciphertext:").pack(side=tk.LEFT)
entry = ttk.Entry(input_frame, width=40)
entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

paste_btn = ttk.Button(input_frame, text="📋", width=3, command=paste_from_clipboard)
paste_btn.pack(side=tk.RIGHT, padx=3)

process_btn = ttk.Button(root, text="Decrypt and Analyze", command=process_text)
process_btn.pack(pady=10)

result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
result_text.pack(padx=10, pady=5, expand=True, fill=tk.BOTH)

root.mainloop()
