from litellm import completion
from pathlib import Path
from tomllib import load
import sys
import pandas as pd

with open('config.toml', 'rb') as f:
    config = load(f)

MODEL = config['main']['MODEL']
API_BASE = config['main']['API_BASE']
SYSTEM_PROMPT = config['main']['SYSTEM_PROMPT']

 
def ask(question: str) -> str:
    response = completion(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        api_base=API_BASE,
        request_timeout=300,
    )
    return response.choices[0].message.content
 
posts = pd.read_csv('raw_data/Messages_Поступашки_ШАД,_Стажировки_и_Магистратура_01_08_2026__11_09_2026.csv', sep=';')
# print(posts.head()['message'])

message = 'message'

for ind, post in posts.iterrows():
    print(ind)
    print(ask(post[message]))
    print('======================')
    if ind ==5:
        break
