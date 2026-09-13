import pandas as pd

def get_posts_data():
    data = pd.read_csv('raw_data/posts_classified_corrected.csv', sep=';')
    # print(data["post_type"].reset_index().groupby('post_type').agg(num=('index', 'count')).sort_values('num', ascending=False))
    type_posts = (data['post_type'].str.split(';', expand = True))
    type_cols = type_posts.columns
    posts_type_frq = type_posts.stack().value_counts()

    # temp = data[data['courses_from_link'] != 'Не подтверждены по содержимому цели']['courses_from_link']

    # for _, el in data.iterrows():
    #     print(el[['courses']])
    #     if _ > 10:
    #         break

    return(posts_type_frq, data)
    

    # return posts_data['message_id', 'date_utc', 'classification_note'].head()
    # return posts_data.columns



if __name__ == "__main__":
    get_posts_data()