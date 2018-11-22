import pandas as pd
from pandas.io import sql
from sqlalchemy import create_engine
from os import listdir
import re

dburl = 'mysql+pymysql://root:rootgroot@localhost/dell_aging_inv'
parse_lfiles = 1
parse_plist = 1

for fname in listdir('.'):
	m1 = re.match("l(\d+)\.csv", fname)
	m2 = re.match("l(\d+)_unsold\.csv", fname)
	if m1 and parse_lfiles:
		df = pd.read_csv(fname, header=None, names=['PRODUCT_NAME', 'PRODUCT_ID', 'TYPE', 'S1', 'S2', 'S3', 'S4', 'PRICE', 'COLOR', 'DELIVTIME', 'AGE', 'DELIVCITY'])
		df['PRODUCT_NAME'] = df['PRODUCT_NAME'].apply(lambda x: x.strip())
		df['PRODUCT_ID'] = df['PRODUCT_ID'].str[4:]
		df['3PLID'] = m1[1]
		df.insert(0, 'ID', 0)
		print(df.to_string())
		engine = create_engine(dburl)
		with engine.connect() as conn, conn.begin():
			df.to_sql('sales', conn, if_exists='append', index=False)
	elif m2 and parse_lfiles:
			df = pd.read_csv(fname, header=None, names=['PRODUCT_NAME', 'PRODUCT_ID', 'TYPE', 'S1', 'S2', 'S3', 'S4', 'PRICE', 'COLOR', 'AGE'])
			df['PRODUCT_NAME'] = df['PRODUCT_NAME'].apply(lambda x: x.strip())
			df['PRODUCT_ID'] = df['PRODUCT_ID'].str[4:]
			df['3PLID'] = m2[1]
			df.insert(0, 'ID', 0)
			print(df.to_string())
			engine = create_engine(dburl)
			with engine.connect() as conn, conn.begin():
				df.to_sql('inventory', conn, if_exists='append', index=False)
	elif fname=='product list.csv' and parse_plist:
		df = pd.read_csv(fname)
		df.rename(columns={'PRODUCT NAME': 'PRODUCT_NAME', 'S.NO': 'SNO', 'PRICE (₹)': 'PRICE'}, inplace=True)
		print(df.columns)
		df['PRODUCT_NAME'] = df['PRODUCT_NAME'].apply(lambda x: x.strip())
		df['PRODUCT_ID'] = df['PRODUCT_ID'].str[4:].astype(int)
		df['PRICE'] = df['PRICE'].apply(lambda x: x.strip('/-').replace(',', ''))
		print(df.to_string())
		engine = create_engine(dburl)
		with engine.connect() as conn, conn.begin():
			df.to_sql('product_list', conn, if_exists='replace', index=False)
