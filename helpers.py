import pickle
import pyodbc
import pymysql

import nltk
from nltk.corpus import stopwords
russian_stopwords = stopwords.words("russian")

def save_obj(obj, name):                                                       
    with open(name + '.pkl', 'wb') as f:                                        
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)                            
                                                                                
def load_obj(name):                                                            
    with open(name + '.pkl', 'rb') as f:                                        
        return pickle.load(f) 

def get_sql_conn():
    server = 'localhost\MSSQLSERVER01' 
    database = 'ir' 
    return pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';DATABASE=ir;UID=sa;PWD=1')

def get_sphinx_conn():
    return pymysql.connect(host='127.0.0.1',port=9306,user='',passwd='',charset='utf8',db='')

def select_from_sphinx_wrapper(query, index, fileds, limit, ranker):
    with get_sphinx_conn() as sphinx_conn:
        rows = select_from_sphinx(sphinx_conn, query, index, fileds, limit, ranker)
    return rows

def cut_query(query):
    query_words = query.split()
    if len(query_words) > 100:
        query_words_wo_stop = [w for w in query_words if w not in russian_stopwords]
        query_words_wo_stop = query_words_wo_stop[:100]
        query = ' '.join(query_words_wo_stop)
    return query

def select_from_sphinx(sphinx_conn, query, index, fileds, limit, ranker):
    query = cut_query(query)
    with sphinx_conn.cursor() as cursor:
        match = '\'"' + query + '"/1\''
        fileds_str = ', '.join(fileds)
        query = f'SELECT {fileds_str} FROM {index} WHERE MATCH({match}) LIMIT 0, {str(limit)} OPTION ranker={ranker}'
        cursor.execute(query)
        rows = cursor.fetchall()
    return rows