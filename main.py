from tkinter import *
from tkinter import messagebox
import os
from openai import OpenAI
import pyperclip

#Выводит лист, как текст
def text_normalization(ans):
    answer=str(ans)
    answer1=""
    for i in answer:
        if i == "'" or i == "[" or i == "]":
            continue
        if i == ",":
            answer1+="."
            continue
        answer1+=i
    return answer1

#Расшифровка шифра Гронсфельда при заданном ключе
def decrypt_gronsfeld(key):
    global answer
    new_text=""
    counter=0
    for i in text:
        if counter == len(key):
            counter=0
        f=ABC.find(i)
        new_text+=(ABC[f+key[counter]])
        counter+=1
    answer.append(new_text)

#рекурсивный перебор для шифра Гронсфельда
def recursive_combinations(length):
    global key
    if length == 3:
        return
    for i in range(10):
        key.append(i)
        decrypt_gronsfeld(key)
        recursive_combinations(length+1)
        key.pop()

def paste_api():
    h_tf.insert(0, pyperclip.paste)

def paste_text():
    w_tf.insert(0, pyperclip.paste)

def main():
    global answer, key,text,ABC
    api = h_tf.get()
    text = w_tf.get()
    #Загрузка api ключа для работы ChatGpt 3.5 turbo
    client = OpenAI(api_key=api)
    def src(text):
        response = client.chat.completions.create(
            messages=[
               {
                    "role": "user",
                    "content": text,
                }
            ],
            model="gpt-3.5-turbo",
        )
        return response.choices[0].message.content
    #распознование языка
    language=26
    ABC="abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ                                                                                                                                          "
    ABC_Atbash="zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBAZYXWVUTSRQPONMLKJIHGFEDCBA      "
    if "р" in src("Какой алфавит используется в следующем предложении"+text+".В ответе напиши только название"):
        language=33
        ABC="абвгдеёжзийклмнопрстуфхцчшщъыьэюяабвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ                                                                                                                                          "
        ABC_Atbash="яюэьыъщшчцхфутсрпонмлкйизжёедгвбаяюэьыъщшчцхфутсрпонмлкйизжёедгвбаЯЮЭЬЫЪЩШЧЦХФУТСРПОНМЛКЙИЗЖЁЕДГВБАЯЮЭЬЫЪЩШЧЦХФУТСРПОНМЛКЙИЗЖЁЕДГВБА          "
    ans=[]


    #Шифр цезаря
    for i in range(language):
        new_text=""
        for j in text:
            f=ABC.find(j)
            new_text+=(ABC[f+i])
        ans.append(new_text)


    # Шифр Атбаш
    Atbash=""
    for i in text:
        Atbash+=ABC_Atbash[ABC.find(i)]
    ans.append(Atbash)


    #Вывод ответов
    print(text_normalization(ans))
    if "yes" != messagebox.askquestion("Дешифратор с использованием ИИ", "Вы довольны следующему результату?"+"\n"+src("Есть ли в следующих предлжениях, такое предложение, что его смысл понятен человеку? "+text_normalization(ans))):
        answer=[]
        key=[]
        for i in range(10):
            key.append(i)
            recursive_combinations(1)
            key.pop()
        messagebox.showinfo("Дешифратор с использованием ИИ", src("Есть ли в следующих предлжениях, такое предложение, что его смысл понятен человеку? "+text_normalization(answer)))

#для интерфейса
window = Tk()
window.title('Дешифратор с использованием ИИ')
window.geometry('400x300')
frame = Frame(window,padx=10,pady=10)
frame.pack(expand=True)
h_lb = Label(frame,text="Введите api key")
h_lb.grid(row=3, column=1)
w_lb = Label(frame,text="Введите зашифрованный текст ",)
w_lb.grid(row=4, column=1)
h_tf = Entry(frame,)
h_tf.grid(row=3, column=2, pady=5)
w_tf = Entry(frame,)
w_tf.grid(row=4, column=2, pady=5)
cal_btn = Button(frame,text='Расшифровать',command=main)
cal_btn.grid(row=5, column=2)
btn = Button(text='Вставить api ключ из буфера', command=paste_api).pack()
btn = Button(text='Вставить текст из буфера', command=paste_text).pack()
window.mainloop()
