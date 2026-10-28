"""cookDB 첫 실습: 회원 목록을 Streamlit 웹 화면에 표시합니다."""

import mysql.connector
import streamlit as st

st.set_page_config(page_title="cookDB 첫 웹 앱", page_icon="☕", layout="wide")
st.title("cookDB 회원 관리 - 첫 웹 앱")
st.caption("MySQL → Python → Streamlit → 웹 브라우저")


def run_query(sql, params=()):
    """기존 MySQL 설정으로 조회하고 연결을 닫습니다."""
    config = dict(st.secrets["mysql"])
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def load_members(search_name="", only_missing=False, grade=None):
    """이름에 검색어가 포함된 회원을 조회하며, 빈 검색어는 전체 조회합니다."""
    sql = """
        SELECT userID, userName, addr, birthYear, mDate,
               COALESCE(email, '미등록') AS email,
               CASE memberGrade
                   WHEN 0 THEN 'BASIC'
                   WHEN 1 THEN 'SILVER'
                   WHEN 2 THEN 'GOLD'
                   ELSE '알 수 없음'
               END AS memberGrade
        FROM userTBL
        """
    conditions = []
    params = []
    if search_name:
        conditions.append("userName LIKE %s")
        params.append(f"%{search_name}%")
    if only_missing:
        conditions.append("email IS NULL")
    if grade is not None:
        conditions.append("memberGrade = %s")
        params.append(grade)
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY userID"
    return run_query(sql, tuple(params))


def load_purchases(user_id):
    # 선택한 회원의 상품, 분류, 단가, 수량과 구매금액을 구매 번호순으로 조회합니다.
    return run_query(
        """
        SELECT prodName, groupName, price, amount, price * amount AS totalPrice
        FROM buyTBL
        WHERE userID = %s
        ORDER BY num
        """,
        (user_id,),
    )


def load_deliveries(status=None):
    sql = """
        SELECT num, userID, prodName, price, amount,
               price * amount AS totalPrice,
               CASE deliveryStatus
                   WHEN 0 THEN '주문접수'
                   WHEN 1 THEN '배송중'
                   WHEN 2 THEN '배송완료'
                   ELSE '알 수 없음'
               END AS deliveryLabel
        FROM buyTBL
    """
    params = ()
    if status is not None:
        sql += " WHERE deliveryStatus = %s"
        params = (status,)
    sql += " ORDER BY num"
    return run_query(sql, params)


def load_purchase_ranking():
    # 구매 기록을 회원별로 묶어 구매 건수와 총액을 계산하고 총액이 큰 순서로 조회합니다.
    return run_query(
        """
        SELECT userID, COUNT(*) AS purchaseCount,
               SUM(price * amount) AS totalPrice
        FROM buyTBL
        GROUP BY userID
        ORDER BY totalPrice DESC, userID
        """
    )


st.subheader("회원 목록 · 이름 검색")
search_name = st.text_input("회원 이름 검색", placeholder="예: 김")
only_missing = st.checkbox("이메일 미등록 회원만")
grade_options = {"전체": None, "BASIC": 0, "SILVER": 1, "GOLD": 2}
selected_grade = st.selectbox("회원등급", list(grade_options))
grade = grade_options[selected_grade]


try:
    all_members = load_members()
    members = load_members(search_name, only_missing, grade) if search_name or only_missing or grade is not None else all_members
    email_counts = run_query(
        """SELECT COUNT(*) AS total, COUNT(email) AS registered,
                  COUNT(*) - COUNT(email) AS missing FROM userTBL"""
    )[0]
except Exception as exc:
    st.error("DB 연결 또는 데이터 조회에 실패했습니다. MySQL 실행 여부와 secrets.toml을 확인하세요.")
    st.caption(f"오류 유형: {type(exc).__name__}")
    st.stop()

st.metric("조회된 회원 수", len(members))
st.caption(
    f"전체 회원 수 {email_counts['total']}명 / "
    f"이메일 등록 {email_counts['registered']}명 / 미등록 {email_counts['missing']}명"
)
st.dataframe(members, hide_index=True, use_container_width=True)
if not members:
    st.info("검색 결과가 없습니다.")
st.success("성공! cookDB의 실제 회원 데이터를 브라우저에 표시했습니다.")

st.subheader("회원 구매 내역")
selected_user_id = st.selectbox(
    "구매 내역을 조회할 회원 ID",
    [member["userID"] for member in all_members],
)

try:
    purchases = load_purchases(selected_user_id) if selected_user_id is not None else []
    ranking = load_purchase_ranking()
except Exception as exc:
    st.error("구매 데이터 조회에 실패했습니다. MySQL 실행 여부와 테이블을 확인하세요.")
    st.caption(f"오류 유형: {type(exc).__name__}")
    st.stop()

st.metric("구매 건수", len(purchases))
st.metric("구매 합계", sum(purchase["totalPrice"] for purchase in purchases))
st.dataframe(
    purchases,
    column_order=["prodName", "groupName", "price", "amount", "totalPrice"],
    hide_index=True,
    use_container_width=True,
)
if selected_user_id is None:
    st.info("조회할 회원이 없습니다.")
elif not purchases:
    st.info("선택한 회원의 구매 기록이 없습니다.")

st.subheader("회원별 구매금액 순위")
st.dataframe(
    ranking,
    column_order=["userID", "purchaseCount", "totalPrice"],
    hide_index=True,
    use_container_width=True,
)
if not ranking:
    st.info("구매 기록이 없습니다.")

st.subheader("배송상태별 구매 내역")
delivery_options = {"전체": None, "주문접수": 0, "배송중": 1, "배송완료": 2}
selected_delivery = st.selectbox("배송상태", list(delivery_options))
try:
    deliveries = load_deliveries(delivery_options[selected_delivery])
except Exception as exc:
    st.error("배송상태 조회에 실패했습니다. buyTBL의 deliveryStatus 열을 확인하세요.")
    st.caption(f"오류 유형: {type(exc).__name__}")
    st.stop()

st.metric("배송 조회 건수", len(deliveries))
st.metric("배송 조회 구매금액 합계", sum(row["totalPrice"] for row in deliveries))
st.dataframe(
    deliveries,
    column_order=["num", "userID", "prodName", "price", "amount", "totalPrice", "deliveryLabel"],
    hide_index=True,
    use_container_width=True,
)
if not deliveries:
    st.info("선택한 배송상태의 구매 내역이 없습니다.")
