import pandas as pd
from copy import deepcopy

data = pd.read_csv('raw_data/base.csv')

data['Сумма'] =  (
    data['Сумма']
    .str.replace(r'\s+', '', regex=True)
    .str.replace(',', '.', regex=False)
)
data['Сумма'] = pd.to_numeric(data['Сумма'], errors='coerce')

data[['date', 'time']] = data['Время'].str.split(' ', expand = True)
del data['Время']
data['date'] = pd.to_datetime(data['date'], format='%d.%m.%Y')
data['time'] = pd.to_datetime(data['time'], format='%H:%M:%S')


#распределение продаж по крусам 
course_stats = data.groupby('Курс').agg(
    purchases=('Номер студента', 'count'),
    unique_buyers=('Номер студента', 'nunique'),
    course_revenue=('Сумма', 'sum'),
    avg_amount=('Сумма', 'mean'),
).sort_values('course_revenue', ascending=False)

print('распределение продаж по крусам')
print(course_stats)
print('=================')
#количество покупок = количеству уникальных покупателей => редко возращаются в рамках 1.5 месяцев?
#мб потому что начало самих курсов привязано к какой то дате, а вот эти 1.5 месяца набирается народ в группы
#опять же из специфики набора редко покупаемыми курсами (Дискретка, например) могли оказаться те, что начнутся еще не скоро

#==========================
#пробуем найти пакетные покупки
# предполагается, что клиент берет два и больше курсов за раз (потому время округлили до минут)
# после соединили это все к кучу чтобы сделать группировку (получается уникальная строка из id клиента + дата + округленное время)

temp = deepcopy(data)
temp['package_order'] = temp['Номер студента'].astype(str) + '_' + temp['date'].astype(str) + '_' + temp['time'].dt.round('1Min').astype(str)

temp = temp.groupby('package_order').agg(
    student_id=('Номер студента', 'first'),
    n_courses=('Курс', 'count'),
    course_revenue=('Сумма', 'sum'),
    date=('date', 'first'),
    courses=('Курс', lambda x: tuple(x))
).reset_index()

#какие курсы пакетами берут чаще всего
total_temp = temp.groupby('courses').agg(
    n_students=('student_id', 'nunique'),
    course_revenue=('course_revenue', 'sum')
).sort_values('n_students', ascending=False).reset_index()

package_order = temp[temp['n_courses'] > 1]
print('Пакетные покупки тотал')
print(package_order.head)
print('=================')
print('Пакетные покупки по частоте')
print(total_temp[(total_temp['courses'].str.len() > 1) &
                 (total_temp['n_students'] > 2)])
print('=================')
# всего видим 153 строки уникальных, т.е из 795 нужно "уникальных" сделок меньше, т.к. как
# минимум 153 пакета по >=2 курса купили пользователи. Ну и нужно учесть, что кто то мог приобрести пару пакетов
# хотя шанс такого невелик, мне кажется (тип чел наверное рассчитывает нагрузку)
# п.с. если поставить округление до часа, все равно остается 153 строки 
# плюс, можно посмотреть, какие курсы чаще всего брали в пакетом, и сколько это принесло (отрезал все варианты, где 1-2 чела брали пакеты)


#повторные покупки (ltv)


purchase_counts = data.groupby('Номер студента').size()
# print(temp[temp['n_courses'] > 1]['student_id'])

# с учетом пакетных студентов
repeat_buyers_p_pack = (purchase_counts > 1).sum()
buyers = (purchase_counts).sum()
repeat_rate_p_pack = repeat_buyers_p_pack / data['Номер студента'].nunique()
print(f"Повторные покупатели: {repeat_buyers_p_pack} из {data['Номер студента'].nunique()} ({repeat_rate_p_pack:.1%})")
print("^ пакетные студенты остались в выборке ^")
# без учета пакетных студентов
package_students_id = temp[temp['n_courses'] > 1]['student_id']
purchase_counts_w_pack = data[~data['Номер студента'].isin(package_students_id)].groupby('Номер студента').size()
repeat_buyers_w_pack = (purchase_counts_w_pack > 1).sum()
buyers = (purchase_counts_w_pack).sum()
repeat_rate_w_pack = repeat_buyers_w_pack / data['Номер студента'].nunique()
print(f"Повторные покупатели: {repeat_buyers_w_pack} из {data['Номер студента'].nunique()} ({repeat_rate_w_pack:.1%})")
print("^ пакетные студенты исключены из выборки ^")

# выводы - по имеющимся данным ltv невысок, хотя опять же, смотрим лишь за месяц.......

