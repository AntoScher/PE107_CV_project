import requests
from bs4 import BeautifulSoup

def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Проверка что это hh.ru
        if "hh.ru" not in url:
            raise ValueError("Поддерживаются только ссылки с hh.ru")
            
        return response
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка сети: {str(e)}")
    except Exception as e:
        raise Exception(f"Ошибка парсинга: {str(e)}")

def extract_vacancy_data(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Проверка на капчу
        if "captcha" in html.lower():
            raise ValueError("Обнаружена капча! Попробуйте позже")
        
        # Извлечение данных
        title = soup.find('h1').text.strip() if soup.find('h1') else "Нет названия"
        salary = soup.find('span', {'data-qa': 'vacancy-salary'}).text.strip() if soup.find('span', {'data-qa': 'vacancy-salary'}) else "Не указана"
        company = soup.find('a', {'data-qa': 'vacancy-company-name'}).text.strip() if soup.find('a', {'data-qa': 'vacancy-company-name'}) else "Компания скрыта"
        
        # Основное описание
        description_div = soup.find('div', {'data-qa': 'vacancy-description'})
        description = description_div.get_text(separator="\n").strip() if description_div else "Описание не найдено"
        
        # Ключевые навыки
        skills = []
        skills_container = soup.find('div', class_='bloko-tag-list')
        if skills_container:
            skills = [skill.text.strip() for skill in skills_container.find_all('span', class_='bloko-tag__section_text')]
        
        markdown = f"# {title}\n\n"
        markdown += f"**Компания:** {company}\n\n"
        markdown += f"**Зарплата:** {salary}\n\n"
        markdown += f"## Описание вакансии\n{description}\n\n"
        markdown += f"## Ключевые навыки\n{', '.join(skills) if skills else 'Не указаны'}"
        
        return markdown
        
    except Exception as e:
        return f"Ошибка извлечения данных вакансии: {str(e)}"

def extract_resume_data(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Базовая информация
        name = soup.find('h2', {'data-qa': 'resume-personal-name'}).text.strip() if soup.find('h2', {'data-qa': 'resume-personal-name'}) else "Имя не указано"
        position = soup.find('span', {'data-qa': 'resume-block-title-position'}).text.strip() if soup.find('span', {'data-qa': 'resume-block-title-position'}) else "Должность не указана"
        
        # Опыт работы
        experiences = []
        for exp in soup.find_all('div', {'data-qa': 'resume-block-experience'}):
            try:
                period = exp.find('div', class_='resume-block__period').text.strip() if exp.find('div', class_='resume-block__period') else "Период не указан"
                company = exp.find('div', class_='resume-block__sub-title').text.strip() if exp.find('div', class_='resume-block__sub-title') else "Компания не указана"
                position = exp.find('div', class_='resume-block__title').text.strip() if exp.find('div', class_='resume-block__title') else "Должность не указана"
                description = exp.find('div', class_='resume-block__description').text.strip() if exp.find('div', class_='resume-block__description') else "Описание отсутствует"
                
                experiences.append(
                    f"**{period}**\n"
                    f"*{company}*\n"
                    f"**{position}**\n"
                    f"{description}\n"
                )
            except:
                continue
                
        # Навыки
        skills = []
        skills_section = soup.find('div', {'data-qa': 'skills-table'})
        if skills_section:
            skills = [skill.text.strip() for skill in skills_section.find_all('span', class_='bloko-tag__section_text')]
        
        markdown = f"# {name}\n\n"
        markdown += f"**Целевая должность:** {position}\n\n"
        markdown += "## Опыт работы\n" + ("\n---\n".join(experiences) if experiences else "Опыт не указан") + "\n\n"
        markdown += "## Ключевые навыки\n" + (', '.join(skills) if skills else "Навыки не указаны")
        
        return markdown
        
    except Exception as e:
        return f"Ошибка извлечения данных резюме: {str(e)}"
