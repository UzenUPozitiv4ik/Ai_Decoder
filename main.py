import google.generativeai as genai
import sys
import os
import string
import re
from collections import Counter
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QSize, QPoint, QThread, pyqtSignal
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QGraphicsOpacityEffect

# Частотные словари и алфавиты для английского и русского языков.
eng_alphabet = string.ascii_uppercase
eng_freq = {
    "A": 8.167,
    "B": 1.492,
    "C": 2.782,
    "D": 4.253,
    "E": 12.702,
    "F": 2.228,
    "G": 2.015,
    "H": 6.094,
    "I": 6.966,
    "J": 0.153,
    "K": 0.772,
    "L": 4.025,
    "M": 2.406,
    "N": 6.749,
    "O": 7.507,
    "P": 1.929,
    "Q": 0.095,
    "R": 5.987,
    "S": 6.327,
    "T": 9.056,
    "U": 2.758,
    "V": 0.978,
    "W": 2.360,
    "X": 0.150,
    "Y": 1.974,
    "Z": 0.074,
}

rus_alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
rus_freq = {
    "А": 8.01,
    "Б": 1.59,
    "В": 4.54,
    "Г": 1.70,
    "Д": 2.98,
    "Е": 8.45,
    "Ё": 0.04,
    "Ж": 0.94,
    "З": 1.65,
    "И": 7.35,
    "Й": 1.21,
    "К": 3.49,
    "Л": 4.40,
    "М": 3.21,
    "Н": 6.70,
    "О": 10.97,
    "П": 2.81,
    "Р": 4.73,
    "С": 5.47,
    "Т": 6.26,
    "У": 2.62,
    "Ф": 0.26,
    "Х": 0.97,
    "Ц": 0.48,
    "Ч": 1.44,
    "Ш": 0.73,
    "Щ": 0.36,
    "Ъ": 0.04,
    "Ы": 1.90,
    "Ь": 1.74,
    "Э": 0.32,
    "Ю": 0.64,
    "Я": 2.01,
}


def detect_language(text):
    if re.search(r"[А-Яа-яЁё]", text):
        return rus_alphabet, rus_freq
    else:
        return eng_alphabet, eng_freq


def get_ic(text):
    freq = Counter(text)
    n = len(text)
    if n <= 1:
        return 0
    ic = sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))
    return ic


def guess_key_length(ciphertext, max_key_length, alphabet):
    potential = []
    for key_length in range(1, max_key_length + 1):
        ic_list = []
        for i in range(key_length):
            seq = ciphertext[i::key_length]
            ic_list.append(get_ic(seq))
        avg_ic = sum(ic_list) / len(ic_list)
        potential.append((key_length, avg_ic))
    typical_ic = 0.0667 if alphabet == eng_alphabet else 0.055
    potential.sort(key=lambda x: abs(x[1] - typical_ic))
    guessed_length = potential[0][0]
    return guessed_length


def chi_squared(text, alphabet, freq):
    total = len(text)
    if total == 0:
        return float("inf")
    freq_count = Counter(text)
    chi2 = 0
    for letter in alphabet:
        observed = freq_count.get(letter, 0)
        expected = freq[letter] * total / 100
        if expected > 0:
            chi2 += ((observed - expected) ** 2) / expected
    return chi2


def find_shift_for_substring(substring, alphabet, freq):
    best_shift = 0
    best_chi = float("inf")
    n = len(alphabet)
    for shift in range(n):
        shifted = "".join(
            alphabet[(alphabet.index(c) - shift) % n] for c in substring
        )
        current_chi = chi_squared(shifted, alphabet, freq)
        if current_chi < best_chi:
            best_chi = current_chi
            best_shift = shift
    return best_shift


def find_key(ciphertext, key_length, alphabet, freq):
    key = ""
    for i in range(key_length):
        substring = ciphertext[i::key_length]
        shift = find_shift_for_substring(substring, alphabet, freq)
        key += alphabet[shift]
    return key


def vigenere_decrypt(text, key, alphabet):
    plaintext = []
    key_index = 0
    key_length = len(key)
    n = len(alphabet)
    for char in text:
        if char.upper() in alphabet:
            k = key[key_index % key_length]
            shift = alphabet.index(k)
            if char.isupper():
                idx = alphabet.index(char)
                new_idx = (idx - shift) % n
                decrypted = alphabet[new_idx]
            else:
                idx = alphabet.index(char.upper())
                new_idx = (idx - shift) % n
                decrypted = alphabet[new_idx].lower()
            plaintext.append(decrypted)
            key_index += 1
        else:
            plaintext.append(char)
    return "".join(plaintext)


def prepare_text(text, alphabet):
    return "".join(filter(lambda c: c.upper() in alphabet, text.upper()))


def vigenere_text(ciphertext_raw):
    alphabet, freq = detect_language(ciphertext_raw)
    cleaned_ciphertext = prepare_text(ciphertext_raw, alphabet)
    max_key_length = 20  # можно настроить по необходимости
    key_length = guess_key_length(cleaned_ciphertext, max_key_length, alphabet)
    key = find_key(cleaned_ciphertext, key_length, alphabet, freq)
    plaintext = vigenere_decrypt(ciphertext_raw, key, alphabet)
    return plaintext


def atbash_text(ciphertext):
    original_lower = "abcdefghijklmnopqrstuvwxyz"
    reversed_lower = original_lower[::-1]
    original_upper = original_lower.upper()
    reversed_upper = original_upper[::-1]

    original_ru_lower = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    reversed_ru_lower = original_ru_lower[::-1]
    original_ru_upper = original_ru_lower.upper()
    reversed_ru_upper = original_ru_upper[::-1]

    mapping = {
        **{
            o: r
            for o, r in zip(
                original_lower + original_upper,
                reversed_lower + reversed_upper,
            )
        },
        **{
            o: r
            for o, r in zip(
                original_ru_lower + original_ru_upper,
                reversed_ru_lower + reversed_ru_upper,
            )
        },
    }

    return "".join([mapping.get(char, char) for char in ciphertext])


def caesar_text(ciphertext):
    results = []
    ru_upper = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    ru_lower = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    max_shifts = max(len(ru_upper), 26)

    for key in range(max_shifts):
        decrypted = []
        for char in ciphertext:
            if char in ru_upper:
                index = ru_upper.index(char)
                shifted = (index - key) % len(ru_upper)
                decrypted.append(ru_upper[shifted])
            elif char in ru_lower:
                index = ru_lower.index(char)
                shifted = (index - key) % len(ru_lower)
                decrypted.append(ru_lower[shifted])
            elif "A" <= char <= "Z":
                base = ord("A")
                alphabet_length = 26
                shifted = (ord(char) - base - key) % alphabet_length
                decrypted.append(chr(base + shifted))
            elif "a" <= char <= "z":
                base = ord("a")
                alphabet_length = 26
                shifted = (ord(char) - base - key) % alphabet_length
                decrypted.append(chr(base + shifted))
            else:
                decrypted.append(char)
        results.append("".join(decrypted))
    return results


# Worker для вызова Gemini API в отдельном потоке.
class ApiWorker(QThread):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key, ciphertext):
        super().__init__()
        self.api_key = api_key
        self.ciphertext = ciphertext

    def run(self):
        try:
            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config=generation_config,
            )
            chat_session = model.start_chat(history=[])

            # Если последний символ не является знаком препинания,
            # добавляем точку для стабильного результата.
            text = self.ciphertext
            if text and text[-1] not in ".!?":
                text += "."

            vigenere_result = vigenere_text(text)
            atbash_result = atbash_text(text)
            caesar_results = "\n".join(caesar_text(text))

            prompt = (
                "Есть ли среди следующих текстов читаемый для человека? Если да, то "
                "выведи его и ничего больше:\n"
                f"{vigenere_result}\n{atbash_result}\n{caesar_results}"
            )
            response = chat_session.send_message(prompt)
            self.result_ready.emit(response.text)
        except Exception as e:
            self.error_occurred.emit(str(e))


class CryptoAnalyzerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Дешифратор")
        self.setGeometry(200, 200, 700, 500)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2C2F38;
                color: #E4E6E9;
            }
            QLabel {
                font-size: 14px;
                color: #B0B3B8;
            }
            QLineEdit {
                background-color: #3A3D47;
                border: 1px solid #5B626C;
                color: #E4E6E9;
                padding: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #A6A9B3;
            }
            QPushButton {
                background-color: #5A6A76;
                border: 1px solid #6F7C88;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #6F7C88;
            }
            QTextEdit {
                background-color: #3A3D47;
                color: #E4E6E9;
                border: 1px solid #5B626C;
                padding: 10px;
                font-size: 14px;
            }
            """
        )

        layout = QVBoxLayout()

        api_layout = QHBoxLayout()
        self.api_key_label = QLabel("API Key:")
        self.api_key_entry = QLineEdit()
        self.api_key_entry.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.api_key_label)
        api_layout.addWidget(self.api_key_entry)

        input_layout = QHBoxLayout()
        self.ciphertext_label = QLabel("Введите шифр:")
        self.ciphertext_input = QLineEdit()
        input_layout.addWidget(self.ciphertext_label)
        input_layout.addWidget(self.ciphertext_input)

        self.process_button = QPushButton("Расшифровать 🕵")
        self.process_button.clicked.connect(self.process_text)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        layout.addLayout(api_layout)
        layout.addLayout(input_layout)
        layout.addWidget(self.process_button)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

        # Настройка отображения GIF.
        self.gif_label = QLabel(self)
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setFixedSize(500, 500)
        self.gif_label.setAttribute(Qt.WA_TranslucentBackground)
        self.gif_label.setStyleSheet("background:transparent;")
        self.gif_label.hide()

        self.gif_effect = QGraphicsOpacityEffect(self.gif_label)
        self.gif_label.setGraphicsEffect(self.gif_effect)
        self.gif_effect.setOpacity(0)

        self.api_worker = None

    def start_gif(self):
        gif_path = r"C:\Users\ilnar\Documents\Python_projects\emoji.gif"
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.movie.loopCount = 1
            self.gif_label.setMovie(self.movie)
            self.movie.start()
            self.movie.frameChanged.connect(self.check_movie_finished)
        else:
            self.gif_label.setText("GIF not found.")
        self.fade_in_gif(duration=300)
        center_point = self.rect().center()
        gif_size = self.gif_label.size()
        new_pos = QPoint(
            center_point.x() - gif_size.width() // 2,
            center_point.y() - gif_size.height() // 2,
        )
        self.gif_label.move(new_pos)
        self.gif_label.raise_()
        self.gif_label.show()

    def check_movie_finished(self, frame):
        if (
            self.movie.loopCount != -1
            and self.movie.currentFrameNumber() == self.movie.frameCount() - 1
        ):
            self.fade_out_gif(duration=300)

    def fade_in_gif(self, duration=300):
        self.anim = QPropertyAnimation(self.gif_effect, b"opacity")
        self.anim.setDuration(duration)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def fade_out_gif(self, duration=300):
        self.anim = QPropertyAnimation(self.gif_effect, b"opacity")
        self.anim.setDuration(duration)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.start()
        self.anim.finished.connect(self.gif_label.hide)

    def process_text(self):
        api_key = self.api_key_entry.text().strip()
        if not api_key:
            self.show_error("API Error", "Please enter your API key.")
            return

        ciphertext = self.ciphertext_input.text().strip()
        if not ciphertext:
            self.show_error(
                "Ciphertext Error", "Please enter the ciphertext to process."
            )
            return

        self.start_gif()
        self.result_text.setText("Загрузка...")

        # Отключаем кнопку, чтобы избежать повторного нажатия
        self.process_button.setEnabled(False)

        # Запуск фонового потока с API запросом
        self.api_worker = ApiWorker(api_key, ciphertext)
        self.api_worker.result_ready.connect(self.on_result_ready)
        self.api_worker.error_occurred.connect(self.on_error)
        self.api_worker.start()

    def on_result_ready(self, result):
        self.result_text.setText(result)
        self.process_button.setEnabled(True)

    def on_error(self, error_msg):
        self.show_error("API Error", f"An error occurred: {error_msg}")
        self.process_button.setEnabled(True)

    def show_error(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryptoAnalyzerApp()
    window.show()
    sys.exit(app.exec_())
