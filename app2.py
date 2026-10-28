import mysql.connector
import streamlit as st
def fetch_all(sql, params=()):
    conn = mysql.connector.connect(**dict(st.secrets["mysql"]))
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

st.subheader("이메일 등록 현황")
only_missing = st.checkbox("이메일 미등록 회원만")
sql = """SELECT userID, userName,
    IFNULL(email, '미등록') AS email
    FROM userTBL"""
if only_missing:
    sql += " WHERE email IS NULL"
sql += " ORDER BY userID"
rows = fetch_all(sql)
st.dataframe(rows, hide_index=True, use_container_width=True)
st.caption(f"조회 결과: {len(rows)}명")