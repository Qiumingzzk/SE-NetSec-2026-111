import sqlite3

def get_user(username):
    # SQL 注入漏洞：直接拼接字符串
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchall()

def delete_file(filename):
    # 命令注入：使用 os.system
    import os
    os.system("rm " + filename)