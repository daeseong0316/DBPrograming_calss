USE cookDB;

-- 1차 확인: 변경할 테이블과 열 (email VARCHAR(50) NULL)
SHOW COLUMNS FROM userTBL;

-- 2차 확인: UPDATE 전에 대상이 정확히 두 명인지 확인
SELECT userID, userName FROM userTBL WHERE userID IN ('YJS', 'KHD');

-- email 열이 없는 DB에서만 다음 줄을 선택하여 실행하세요.
-- ALTER TABLE userTBL ADD COLUMN email VARCHAR(50) NULL;

SELECT userID, userName, email FROM userTBL WHERE userID IN ('YJS', 'KHD');
START TRANSACTION;
UPDATE userTBL SET email = 'yjs@example.com' WHERE userID = 'YJS';
UPDATE userTBL SET email = 'khd@example.com' WHERE userID = 'KHD';
COMMIT;

-- 3차 확인: Workbench와 Streamlit의 전체 목록 및 필터 결과 비교
SELECT userID, userName, COALESCE(email, '미등록') AS email
FROM userTBL ORDER BY userID;
SELECT userID, userName, COALESCE(email, '미등록') AS email
FROM userTBL WHERE email IS NULL ORDER BY userID;
SELECT COUNT(*) AS total, COUNT(email) AS registered,
       COUNT(*) - COUNT(email) AS missing FROM userTBL;
-- 기대 결과: total=10, registered=2, missing=8
