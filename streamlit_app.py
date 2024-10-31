import streamlit as st
import google.generativeai as genai

# Настройка API ключа
api_key = "AIzaSyCJy8Mh3MDuQy3FxI11PxO5UBhe-sczgdA"

# Конфигурация клиента
genai.configure(api_key=api_key)

# Инициализация модели Gemini
model = genai.GenerativeModel("gemini-1.5-flash")

# Заголовок и описание приложения
st.title("📄 Document Question Answering")
st.write(
    "Upload a document below and ask a question about it – Gemini will answer! "
    "To use this app, you need to provide a Google API key."
)

# Загрузка файла
uploaded_file = st.file_uploader(
    "Upload a document (.txt or .md)", type=("txt", "md")
)

# Ввод вопроса
question = st.text_area(
    "Now ask a question about the document!",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

if uploaded_file and question:
    document = None
    # Сброс указателя файла на начало
    uploaded_file.seek(0)
    
    # Список кодировок для попытки
    encodings = ['utf-8-sig', 'utf-8', 'cp1251', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            # Сброс указателя файла перед каждой попыткой
            uploaded_file.seek(0)
            document = uploaded_file.read().decode(encoding)
            break  # Если успешно, прервать цикл
        except UnicodeDecodeError:
            continue
    
    if document is None:
        st.error("Не удалось прочитать файл. Пожалуйста, убедитесь, что файл содержит текст в корректной кодировке.")
    else:
        try:
            # Генерация ответа с использованием Gemini
            prompt = f"Here's a document: {document}\n\nQuestion: {question}\n\nPlease provide an answer based on the document content."
            
            response = model.generate_content(prompt, stream=True)
            
            # Потоковый вывод ответа
            response_container = st.empty()
            full_response = ""
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    response_container.markdown(full_response)
                    
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
