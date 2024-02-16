import os
from openai import OpenAI



#Загрузка api ключа для работы ChatGpt 3.5 turbo
client = OpenAI(
    api_key="Ваш-api-key"
)
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


text=input()


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
answer=str(ans)
answer1=""
for i in answer:
    if i == "'" or i == "[" or i == "]":
        continue
    if i == ",":
        answer1+="."
        continue
    answer1+=i
print("Возможные расшифровки")
print(answer1)
answer1=src("Есть ли в следующих предлжениях, такое предложение, что его смысл понятен человеку? "+answer1)
print(answer1)


if input("Вы довольны результатом? y/n - ") == "y":
    exit()


#Шифр Гронсфельда 
#длина ключа <= 6
answer=[]

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

def recursive_combinations(length):
    if length == 6:
        return
    for i in range(10):
        key.append(i)
        decrypt_gronsfeld(key)
        recursive_combinations(length+1)
        key.pop()


key=[]
for i in range(1,10):
    key.append(i)
    recursive_combinations(1)
    key.pop()


answer=str(ans)
answer1=""
for i in answer:
    if i == "'" or i == "[" or i == "]":
        continue
    if i == ",":
        answer1+="."
        continue
    answer1+=i
print(answer1)
answer1=src("Есть ли в следующих предлжениях, такое предложение, что его смысл понятен человеку? "+answer1)
print(answer1)
