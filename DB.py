import psycopg2

def query(str):
    result = []
    conn = psycopg2.connect(user="tsender", password="1234", database="tsender2", host="127.0.0.1", port="5432")
    cursor = conn.cursor()
    cursor.execute(str)
    try:
        conn.commit()
    except:
        pass
    try:
        result = cursor.fetchall()
    except:
        pass
    conn.close()
    return result
