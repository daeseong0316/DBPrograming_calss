USE cookDB;

-- 1. 수정 전: 회원 10명의 누적 구매금액과 예상 등급을 확인합니다.
SELECT u.userID, COALESCE(p.totalPrice, 0) AS totalPrice,
       CASE WHEN COALESCE(p.totalPrice, 0) >= 1000 THEN 'GOLD'
            WHEN COALESCE(p.totalPrice, 0) >= 100 THEN 'SILVER'
            ELSE 'BASIC' END AS expectedGrade
FROM userTBL AS u
LEFT JOIN (
    SELECT userID, SUM(price * amount) AS totalPrice
    FROM buyTBL GROUP BY userID
) AS p ON u.userID = p.userID
ORDER BY u.userID;

-- 2. 최초 한 번만 실행합니다. 이미 열이 있으면 ALTER 문은 건너뜁니다.
ALTER TABLE userTBL ADD COLUMN memberGrade TINYINT NOT NULL DEFAULT 0;

-- 3. 구매 기록이 없는 회원도 LEFT JOIN으로 포함해 BASIC으로 저장합니다.
-- 구매 데이터가 바뀌면 이 UPDATE와 COMMIT을 다시 실행해 등급을 갱신합니다.
START TRANSACTION;
UPDATE userTBL AS u
LEFT JOIN (
    SELECT userID, SUM(price * amount) AS totalPrice
    FROM buyTBL GROUP BY userID
) AS p ON u.userID = p.userID
SET u.memberGrade = CASE
    WHEN COALESCE(p.totalPrice, 0) >= 1000 THEN 2
    WHEN COALESCE(p.totalPrice, 0) >= 100 THEN 1
    ELSE 0
END;
COMMIT;

-- 4. 저장 결과 확인: 아래 SELECT들을 Workbench에서 웹과 비교합니다.
SHOW COLUMNS FROM userTBL LIKE 'memberGrade';

SELECT u.userID, COALESCE(p.totalPrice, 0) AS totalPrice, u.memberGrade,
       CASE u.memberGrade WHEN 0 THEN 'BASIC' WHEN 1 THEN 'SILVER'
            WHEN 2 THEN 'GOLD' END AS gradeLabel
FROM userTBL AS u
LEFT JOIN (
    SELECT userID, SUM(price * amount) AS totalPrice
    FROM buyTBL GROUP BY userID
) AS p ON u.userID = p.userID
ORDER BY u.userID;

SELECT memberGrade, COUNT(*) AS memberCount
FROM userTBL GROUP BY memberGrade ORDER BY memberGrade;
-- 기대 결과: BASIC(0)=7, SILVER(1)=1, GOLD(2)=2

SELECT COUNT(*) AS totalMembers FROM userTBL;
-- 기대 결과: 10

SELECT userID FROM userTBL WHERE memberGrade = 2 ORDER BY userID;
-- GOLD: KHD, PSH / SILVER: KYM / 나머지 7명: BASIC
