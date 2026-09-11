import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.signal import savgol_filter

data = pd.read_csv('raw_data/base.csv')
temp = data
data[['date', 'time']] = data['Время'].str.split(' ', expand = True)
del data['Время']
data['date'] = pd.to_datetime(data['date'], format='%d.%m.%Y')
data['time'] = pd.to_datetime(data['time'], format='%H:%M:%S')
data = data.sort_values(by='date')

data['Сумма'] =  (
    data['Сумма']
    .str.replace(r'\s+', '', regex=True)
    .str.replace(',', '.', regex=False)
)
data['Сумма'] = pd.to_numeric(data['Сумма'], errors='coerce')
data_for_revenue =  data.groupby(['Курс', 'date']).agg(course_revenue = ('Сумма', 'sum')).reset_index()


fig, axes = plt.subplots(
    nrows=5, 
    ncols=4, 
    figsize=(12, 14), constrained_layout=True, sharex = True)


x_min = pd.to_datetime('2026-08-01')
x_max = pd.to_datetime('2026-09-15')

for ind, course in enumerate(data_for_revenue['Курс'].unique()):
    temp = data_for_revenue[data_for_revenue['Курс'] == course]

    row = ind // 4
    col = ind % 4
    ax = axes[row, col]
    window = len(temp['course_revenue'])
    
    # тут сглаживание 2шт., и голые данные, п.с. савгол берет окно, внутри полином.апр. и для точки берется значение пол. в ней самой
    ax.plot(temp['date'], temp['course_revenue'].rolling(window=window//5, center=True).mean(), color='blue', label='MA') # скользящее среднее
    ax.plot(temp['date'], savgol_filter(temp['course_revenue'], window_length=min(window, 5), polyorder=2), color='red', label='SavGol') # фильтр савгол
    ax.bar(temp['date'], temp['course_revenue'], color='green', label='raw') # сырые данные 
    
    ax.set_title(course)
    ax.set_xlim(x_min, x_max)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

    ax.legend()
    ax.set_ylabel('руб.')
    ax.grid(True, axis='y')
    ax.grid(True, axis='x')

fig.autofmt_xdate()
plt.tight_layout()
plt.show()
fig.savefig('proc_data/total_course_revenue_by_dates.png')
plt.close(fig)


data_for_num_orders = data.groupby(['Курс', 'date']).size().reset_index(name='num_orders')
fig, axes = plt.subplots(
    nrows=5, 
    ncols=4, 
    figsize=(12, 14), constrained_layout=True, sharex = True)
for ind, course in enumerate(data_for_num_orders['Курс'].unique()):
    temp = data_for_num_orders[data_for_num_orders['Курс'] == course]

    row = ind // 4
    col = ind % 4
    ax = axes[row, col]
    window = len(temp['num_orders'])
    
    # тут сглаживание 2шт., и голые данные, п.с. савгол берет окно, внутри полином.апр. и для точки берется значение пол. в ней самой
    ax.plot(temp['date'], temp['num_orders'].rolling(window=window//5, center=True).mean(), color='blue', label='MA') # скользящее среднее
    ax.plot(temp['date'], savgol_filter(temp['num_orders'], window_length=min(window, 5), polyorder=2), color='red', label='SavGol') # фильтр савгол
    ax.bar(temp['date'], temp['num_orders'], color='green', label='raw') # сырые данные 
    
    ax.set_title(course)
    ax.set_xlim(x_min, x_max)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

    ax.legend()
    ax.set_ylabel('ед. сделок')
    ax.grid(True, axis='y')
    ax.grid(True, axis='x')

fig.autofmt_xdate()
plt.tight_layout()
plt.show()
fig.savefig('proc_data/total_course_num_orders_by_dates.png')
plt.close(fig)






