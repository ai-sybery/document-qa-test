import streamlit as st
import google.generativeai as genai
import time

# Настройка API ключа - ЗАМЕНИТЕ НА СВОЙ КЛЮЧ
api_key = "AIzaSyCJy8Mh3MDuQy3FxI11PxO5UBhe-sczgdA"

# Конфигурация клиента
genai.configure(api_key=api_key)

# Инициализация модели Gemini
model = genai.GenerativeModel("gemini-1.5-flash")

# Системный промпт
system_prompt = """Вы полезный и информативный помощник. Отвечайте на русском языке. Всегда отвечайте только на основе предоставленного документа. Если ответ не найден в документе, скажите: «Я не могу ответить на этот вопрос на основе предоставленного документа." """

# Заголовок и описание приложения
st.title("📄 Document Question Answering")
st.write(
    "Загрузите документ ниже и задайте вопрос – Gemini ответит! "
    "Для использования этого приложения вам необходим API ключ Google."
)

# Загрузка файла
uploaded_file = st.file_uploader(
    "Загрузите документ (.txt, .md или .pdf)", type=("txt", "md", "pdf")
)

# Ввод вопроса
question = st.text_area(
    "Теперь задайте вопрос о документе!",
    placeholder="Можете ли вы дать мне краткое резюме?",
    disabled=not uploaded_file,
)


if uploaded_file and question:
    try:
        document = None
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
            import PyPDF2
            try:
                reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                document = text
            except Exception as e:
                st.error(f"Ошибка при обработке PDF файла: {e}")
                document = None
        else:
            st.error("Неподдерживаемый тип файла")
            document = None


        if document is None:
            st.error("Не удалось прочитать файл.")
        else:
            try:
                # Генерация ответа с использованием Gemini
                prompt = f"""{system_prompt}\nВот документ: {document}\n\nВопрос: {question}\n\nПожалуйста, предоставьте ответ на основе содержимого документа."""

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

    except Exception as e:
        st.error(f"Произошла неизвестная ошибка: {e}")