import streamlit as st
import google.generativeai as genai
import time
import PyPDF2
from docx import Document

# Настройка API ключа - ЗАМЕНИТЕ НА СВОЙ КЛЮЧ
api_key = "AIzaSyCJy8Mh3MDuQy3FxI11PxO5UBhe-sczgdA"

# Конфигурация клиента
genai.configure(api_key=api_key)

# Инициализация модели Gemini
# варианты: "gemini-1.5-pro-exp-0827", "gemini-1.5-pro", "gemini-1.5-flash",  ???check	"gemini-experimental"
model = genai.GenerativeModel("gemini-1.5-pro-exp-0827")

# Системный промпт
system_prompt = """Вы полезный и информативный помощник. Отвечайте на русском языке. Всегда отвечайте только на основе предоставленного документа." """

# Заголовок и описание приложения
st.title("📄 Document Question Answering")
st.write(
    "Загрузите документы ниже и задайте вопрос – Gemini ответит! "
    "Для использования этого приложения вам необходим API ключ Google."
)

# Загрузка файлов
uploaded_files = st.file_uploader(
    "Загрузите документы (.txt, .md, .pdf, .docx)", type=("txt", "md", "pdf", "docx"), accept_multiple_files=True
)

# Ввод вопроса
question = st.text_area(
    "Теперь задайте вопрос о документах!",
    placeholder="Можете ли вы дать мне краткое резюме?",
    disabled=not uploaded_files,
)

if uploaded_files and question:
    documents = []
    for uploaded_file in uploaded_files:
        document = None
        try:
            # Обработка разных типов файлов
            if uploaded_file.name.lower().endswith(('.txt', '.md')):
                uploaded_file.seek(0)
                encodings = ['utf-8-sig', 'utf-8', 'cp1251', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        uploaded_file.seek(0)
                        document = uploaded_file.read().decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
            elif uploaded_file.name.lower().endswith('.pdf'):
                try:
                    reader = PyPDF2.PdfReader(uploaded_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    document = text
                except Exception as e:
                    st.error(f"Ошибка при обработке PDF файла: {e}")
            elif uploaded_file.name.lower().endswith('.docx'):
                try:
                    doc = Document(uploaded_file)
                    text = "\n".join([para.text for para in doc.paragraphs])
                    document = text
                except Exception as e:
                    st.error(f"Ошибка при обработке DOCX файла: {e}")
            else:
                st.error("Неподдерживаемый тип файла")

            if document:
                documents.append(document)

        except Exception as e:
            st.error(f"Произошла ошибка при обработке файла {uploaded_file.name}: {e}")

    if documents:
        try:
            # Объединение всех документов в один
            combined_document = "\n\n".join(documents)

            # Генерация ответа с использованием Gemini
            prompt = f"""{system_prompt}\nВот документы: {combined_document}\n\nВопрос: {question}\n\nПожалуйста, предоставьте ответ на основе содержимого документов."""

            response = model.generate_content(prompt, stream=True)
            time.sleep(17)  # Задержка, чтобы избежать ошибки 429

            # Потоковый вывод ответа
            response_container = st.empty()
            full_response = ""

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    response_container.markdown(full_response)

        except Exception as e:
            if "429" in str(e):
                st.error("Превышен лимит запросов к API. Пожалуйста, повторите попытку позже.")
            else:
                st.error(f"Ошибка при генерации ответа: {str(e)}")