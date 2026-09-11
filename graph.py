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

input(data.head())
data['Сумма'] =  (
    data['Сумма']
    .str.replace(r'\s+', '', regex=True)
    .str.replace(',', '.', regex=False)
)
data['Сумма'] = pd.to_numeric(data['Сумма'], errors='coerce')

data =  data.groupby(['Курс', 'date']).agg(course_revenue = ('Сумма', 'sum')).reset_index()

fig, axes = plt.subplots(
    nrows=5, 
    ncols=4, 
    figsize=(12, 14), constrained_layout=True)

for ind, course in enumerate(data['Курс'].unique()):
    temp = data[data['Курс'] == course]

    row = ind // 4
    col = ind % 4
    ax = axes[row, col]
    window = len(temp['course_revenue'])
    ax.plot(temp['date'].dt.strftime('%d.%m'), temp['course_revenue'].rolling(window=window//5, center=True).mean(), color='blue', label='MA')
    ax.plot(temp['date'].dt.strftime('%d.%m'), savgol_filter(temp['course_revenue'], window_length=min(window, 5), polyorder=2), color='red', label='SavGol')
    ax.plot(temp['date'].dt.strftime('%d.%m'), temp['course_revenue'], color='green', label='raw')
    ax.legend()
    ax.set_title(course)

    ax.tick_params(axis='x', labelsize=8)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

    ax.set_ylabel('руб.')
    ax.grid(True, axis='y')


plt.show()
fig.savefig('proc_data/total_course_revenue_by_dates.png')
plt.close(fig)






