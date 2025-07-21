import streamlit as st
import requests
import json
from parse_hh import get_html, extract_vacancy_data, extract_resume_data

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat-r1"  # Специальная русскоязычная модель

SYSTEM_PROMPT = """
Проскорь кандидата, насколько он подходит для данной вакансии.

1. Сначала сделай анализ по пунктам:
   - Соответствие навыков требованиям вакансии
   - Релевантность опыта работы
   - Качество заполнения резюме (понятно ли описаны задачи и решения?)
   
2. Отдельно оцени качество резюме по шкале от 1 до 5

3. Выставь итоговую оценку соответствия от 1 до 10

4. В конце добавь рекомендации по улучшению резюме

ОБЯЗАТЕЛЬНО придерживайся этой структуры!
""".strip()

def request_deepseek(system_prompt, user_prompt, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
        "stop_token_ids": [32021]  # Важно для русской локализации
    }
    
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка API: {str(e)}")
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        st.error(f"Ошибка обработки ответа: {str(e)}")
        return None

# UI
st.title('🧠 CV Scoring App (DeepSeek-R1)')

with st.expander("ℹ️ Инструкция"):
    st.write("""
    1. Вставьте ссылку на вакансию с hh.ru
    2. Вставьте ссылку на резюме с hh.ru
    3. Нажмите кнопку анализа
    """)

col1, col2 = st.columns(2)
with col1:
    job_url = st.text_input('Ссылка на вакансию hh.ru', placeholder="https://hh.ru/vacancy/12345")
with col2:
    resume_url = st.text_input('Ссылка на резюме hh.ru', placeholder="https://hh.ru/resume/abcde")

if st.button("🔍 Проанализировать соответствие", use_container_width=True):
    if not job_url or not resume_url:
        st.warning("Пожалуйста, введите обе ссылки!")
        st.stop()

    with st.spinner("⏳ Парсим данные и анализируем через DeepSeek-R1..."):
        try:
            # Парсинг данных
            job_html = get_html(job_url).text
            resume_html = get_html(resume_url).text

            job_text = extract_vacancy_data(job_html)
            resume_text = extract_resume_data(resume_html)
            
            # Логирование длины текста (для отладки)
            st.session_state['last_job_len'] = len(job_text)
            st.session_state['last_resume_len'] = len(resume_text)

            # Формирование промпта
            prompt = f"""
            ## ВАКАНСИЯ
            {job_text}
            
            ## РЕЗЮМЕ КАНДИДАТА
            {resume_text}
            
            ПРОАНАЛИЗИРУЙ строго по инструкции выше!
            """.strip()

            # Отправка в DeepSeek
            api_key = st.secrets["DEEPSEEK_API_KEY"]
            response = request_deepseek(SYSTEM_PROMPT, prompt, api_key)
            
            if response:
                st.success("Анализ завершен!")
                st.subheader("📊 Результат анализа DeepSeek-R1")
                st.markdown(response)
                
                # Дополнительная информация
                with st.expander("ℹ️ Техническая информация"):
                    st.write(f"Модель: {DEEPSEEK_MODEL}")
                    st.write(f"Длина вакансии: {len(job_text)} символов")
                    st.write(f"Длина резюме: {len(resume_text)} символов")
            else:
                st.error("Не удалось получить ответ от DeepSeek API")

        except Exception as e:
            st.error(f"Критическая ошибка: {str(e)}")
            st.exception(e)
