import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from scipy.signal import savgol_filter

# Предполагаем, что posts_data.py существует
from posts_data import get_posts_data

# --- Вспомогательная функция для унификации временных зон ---
def make_naive(dt_series):
    """
    Приводит серию дат к 'naive' формату (без timezone).
    Если timezone есть - конвертирует в UTC и убирает метку.
    Если нет - возвращает как есть.
    """
    if dt_series.empty:
        return dt_series
    
    # Если серия уже datetime64[ns], проверяем наличие tz
    if dt_series.dt.tz is not None:
        # Конвертируем в UTC, затем убираем timezone info
        return dt_series.dt.tz_convert('UTC').dt.tz_localize(None)
    return dt_series

# Создаем папку, если её нет
os.makedirs('proc_data', exist_ok=True)

# --- Подготовка данных ---
data = pd.read_csv('raw_data/base.csv')

# Разделение даты и времени
data[['date', 'time']] = data['Время'].str.split(' ', expand=True)

# Конвертация типов
data['date'] = pd.to_datetime(data['date'], format='%d.%m.%Y')
data['time'] = pd.to_datetime(data['time'], format='%H:%M:%S')
data['Время'] = pd.to_datetime(data['Время'], format='%d.%m.%Y %H:%M:%S')

data = data.sort_values(by='date')

# Очистка и конвертация суммы
data['Сумма'] = (
    data['Сумма']
    .str.replace(r'\s+', '', regex=True)
    .str.replace(',', '.', regex=False)
)
data['Сумма'] = pd.to_numeric(data['Сумма'], errors='coerce')

# ВАЖНО: Унифицируем даты в основном датафрейме
data['date'] = make_naive(data['date'])
data['Время'] = make_naive(data['Время'])

# Группировка по курсам и датам
data_for_revenue = data.groupby(['Курс', 'date']).agg(course_revenue=('Сумма', 'sum')).reset_index()

# Получение данных о постах
posts_fr, posts_data = get_posts_data()

adv_qual = {'Распродажа': 'brown', "промокод": 'yellow', "прямое предложение": 'violet'}

# Сбор дат рекламных постов по типам
adv_posts_dates = {}
for _, post in posts_data.iterrows():
    post_type = str(post['post_type']) if pd.notna(post['post_type']) else ""
    
    for qual in adv_qual:
        if qual.lower() in post_type.lower():
            adv_date = post['date_utc']
            
            # Конвертируем дату поста в naive формат сразу при сохранении
            if isinstance(adv_date, pd.Timestamp):
                adv_date = make_naive(pd.Series([adv_date]))[0]
            elif isinstance(adv_date, str):
                adv_date = pd.to_datetime(adv_date)
                adv_date = make_naive(pd.Series([adv_date]))[0]
            
            adv_posts_dates[qual] = adv_posts_dates.get(qual, []) + [adv_date]

# Конфигурация метрик
metrics_config = [
    {
        'suffix': '_revenue',
        'unit': 'руб.',
        'column': 'course_revenue',
        'agg_func': ('Сумма', 'sum')
    },
    {
        'suffix': '_orders',
        'unit': 'ед.сделок',
        'column': 'num_orders',
        'agg_func': (None, 'size')
    }
]

# Глобальные границы оси X (тоже делаем naive, на случай если to_datetime вернет tz)
x_min = pd.to_datetime('2026-08-01')
x_max = pd.to_datetime('2026-09-15')
# Явно убеждаемся, что они naive
x_min = make_naive(pd.Series([x_min]))[0]
x_max = make_naive(pd.Series([x_max]))[0]

unique_courses = data['Курс'].unique()

for config in metrics_config:
    # Формируем агрегированные данные для текущего метрика
    if config['agg_func'][0] is None:
        plot_data = data.groupby(['Курс', 'date']).size().reset_index(name=config['column'])
    else:
        plot_data = data.groupby(['Курс', 'date']).agg(**{config['column']: config['agg_func']}).reset_index()
    
    # Еще раз убеждаемся, что дата в plot_data naive (наследство от data)
    plot_data['date'] = make_naive(plot_data['date'])

    for course in unique_courses:
        temp = plot_data[plot_data['Курс'] == course].copy()
        
        if temp.empty:
            continue

        # Настройка окна для сглаживания
        window_size = len(temp)
        roll_window = max(1, window_size // 5)
        
        sg_window = min(window_size, 5)
        if sg_window % 2 == 0:
            sg_window -= 1
        if sg_window < 3:
            sg_window = None # Отключаем SavGol, если данных мало

        fig, ax = plt.subplots(figsize=(10, 6))

        # 1. Сырые данные (столбцы)
        ax.bar(temp['date'], temp[config['column']], color='green', alpha=0.6, label='Raw Data')

        # 2. Скользящее среднее
        ma_series = temp[config['column']].rolling(window=roll_window, center=True, min_periods=1).mean()
        ax.plot(temp['date'], ma_series, color='blue', linewidth=2, label=f'MA (w={roll_window})')

        # 3. Фильтр Савицкого-Голея
        if sg_window is not None and window_size >= sg_window:
            try:
                sg_series = savgol_filter(temp[config['column']], window_length=sg_window, polyorder=2)
                ax.plot(temp['date'], sg_series, color='red', linewidth=2, linestyle='--', label=f'SavGol (w={sg_window})')
            except Exception:
                pass

        # 4. Вертикальные линии для рекламных постов
        leg_handlers = []
        for key, dates_list in adv_posts_dates.items():
            if not dates_list:
                continue
            
            color = adv_qual[key]
            label = key.strip()
            leg_handlers.append(Line2D([], [], color=color, linewidth=4, label=label))
            
            for adv_date in dates_list:
                # adv_date уже naive благодаря make_naive выше
                if x_min <= adv_date <= x_max:
                    ax.axvline(x=adv_date, color=color, linewidth=1.5, alpha=0.8)

        # Оформление
        ax.set_title(f'{course} - {config["unit"]}')
        ax.set_xlabel('Дата')
        ax.set_ylabel(config['unit'])
        
        ax.set_xlim(x_min, x_max)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        ax.grid(True, axis='x', linestyle='--', alpha=0.3)

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles + leg_handlers)

        safe_course_name = "".join([c if c.isalnum() else "_" for c in str(course)])
        file_name = f"proc_data/{safe_course_name}{config['suffix']}.png"
        
        print(f"Saving: {file_name}")
        
        fig.autofmt_xdate()
        plt.savefig(file_name, dpi=300, bbox_inches='tight')
        plt.close(fig)
