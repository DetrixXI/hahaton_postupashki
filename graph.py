import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from scipy.signal import savgol_filter

from posts_data import get_posts_data

data = pd.read_csv('raw_data/base.csv')
temp = data
data[['date', 'time']] = data['Время'].str.split(' ', expand = True)
# del data['Время']
data['date'] = pd.to_datetime(data['date'], format='%d.%m.%Y')
data['time'] = pd.to_datetime(data['time'], format='%H:%M:%S')
data['Время'] = pd.to_datetime(data['Время'], format='%d.%m.%Y %H:%M:%S')
data = data.sort_values(by='date')


data['Сумма'] =  (
    data['Сумма']
    .str.replace(r'\s+', '', regex=True)
    .str.replace(',', '.', regex=False)
)
data['Сумма'] = pd.to_numeric(data['Сумма'], errors='coerce')
data_for_revenue =  data.groupby(['Курс', 'date']).agg(course_revenue = ('Сумма', 'sum')).reset_index()

posts_fr, posts_data = get_posts_data()

adv_qual = {'Распродажа':'brown', " промокод":'yellow', " прямое предложение ":'violet'}
adv_posts_dates = dict()

adv_dates = []
for _, post in posts_data.iterrows():
    # input(post)
    for qual in adv_qual:
        if qual not in post['post_type']:
            continue
        adv_posts_dates[qual] = adv_posts_dates.get(qual, []) + [[post['date_utc'], post['courses']]]


fig_name = ['proc_data/total_course_revenue_by_dates.png', 'proc_data/total_course_num_orders_by_dates.png']
temp = [data.groupby(['Курс', 'date']).agg(course_revenue = ('Сумма', 'sum')).reset_index(), 
    data.groupby(['Курс', 'date']).size().reset_index(name='num_orders')]
units = ['руб.', 'ед.сделок']
columns = ['course_revenue', 'num_orders']
all_data_temp = zip(fig_name, temp, units, columns)

for fig_name, data, unit, column in all_data_temp:
    fig, axes = plt.subplots(
        nrows=5, 
        ncols=4, 
        figsize=(12, 14), constrained_layout=True, sharex = True)


    x_min = pd.to_datetime('2026-08-01')
    x_max = pd.to_datetime('2026-09-15')

    for ind, course in enumerate(data['Курс'].unique()):
        temp = data[data['Курс'] == course]

        row = ind // 4
        col = ind % 4
        ax = axes[row, col]
        window = len(temp[column])
        
        # тут сглаживание 2шт., и голые данные, п.с. савгол берет окно, внутри полином.апр. и для точки берется значение пол. в ней самой
        ax.plot(temp['date'], temp[column].rolling(window=window//5, center=True).mean(), color='blue', label='MA') # скользящее среднее
        ax.plot(temp['date'], savgol_filter(temp[column], window_length=min(window, 5), polyorder=2), color='red', label='SavGol') # фильтр савгол
        ax.bar(temp['date'], temp[column], color='green', label='raw') # сырые данные 

        leg_handler = []
        for key, value in adv_posts_dates.items():
            leg_mess = Line2D([],[],
                            color=adv_qual[key],
                            linewidth=4,
                            label=key.strip()
                            )
            leg_handler.append(leg_mess)
            for adv_date, adv_type in value:
                if course not in adv_type:
                    break
                x_pos = pd.to_datetime(adv_date)
                ax.axvline(x=x_pos + pd.Timedelta(hours=3), color=adv_qual[key])
        
        ax.set_title(course)
        ax.set_xlim(x_min, x_max)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

        ax.legend(handles=ax.get_legend_handles_labels()[0] + leg_handler)
        ax.set_ylabel(unit)
        ax.grid(True, axis='y')
        ax.grid(True, axis='x')

    fig.autofmt_xdate()
    # plt.tight_layout()
    plt.show()
    fig.savefig(fig_name)
    plt.close(fig)






