import requests
import json
import pandas as pd

df = pd.read_csv('matters_for_article_counts.csv')


def article_count(client, firm):
	key  =  '49e6aeb75bbf4073922724efb125b3da'
	payload = {'key':key, 'format':'json', 'limit': 200, 'filter_duplicates': 'TRUE', 'sort_by_relevance':'TRUE', 'query':'{fclient} AND {ffirm} AND harvestDate:[2018-04-01T00:00:01Z TO 2019-03-31T23:59:59Z]'.format(fclient=client, ffirm=firm)}
	r = requests.get('http://metabase.moreover.com/api/v10/searchArticles', params=payload)
	y = r.json()
	try:
		article_count = y['totalResults']
		print(article_count)
		return article_count
	except:
		return 0
		pass

articles = []

for i in df.index:
	count = article_count(df['NameOfClient'][i], df['Firmname'][i])
	articles.append(count)
	print(i)

df['article_counts'] = articles

df.to_csv('matters_with_counts.csv')


