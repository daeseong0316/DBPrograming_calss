USE cookDB;

-- 변경 전: 테이블 구조와 수정 대상 12건을 확인합니다.
SHOW COLUMNS FROM buyTBL;
SELECT num, userID, prodName, price, amount FROM buyTBL
WHERE num BETWEEN 1 AND 12 ORDER BY num;

-- 최초 한 번만 실행합니다. 이미 열이 있으면 ALTER 문은 다시 실행하지 않습니다.
ALTER TABLE buyTBL ADD COLUMN deliveryStatus TINYINT NOT NULL DEFAULT 0;

START TRANSACTION;
UPDATE buyTBL SET deliveryStatus = 0 WHERE num BETWEEN 1 AND 4;
UPDATE buyTBL SET deliveryStatus = 1 WHERE num BETWEEN 5 AND 8;
UPDATE buyTBL SET deliveryStatus = 2 WHERE num BETWEEN 9 AND 12;
COMMIT;

-- 저장 확인: Workbench에서 아래 SELECT만 다시 실행해 웹과 비교합니다.
SELECT num, userID, prodName, price, amount, price * amount AS totalPrice,
       deliveryStatus,
       CASE deliveryStatus WHEN 0 THEN '주문접수' WHEN 1 THEN '배송중'
            WHEN 2 THEN '배송완료' ELSE '알 수 없음' END AS deliveryLabel
FROM buyTBL ORDER BY num;

SELECT deliveryStatus, COUNT(*) AS purchaseCount,
       SUM(price * amount) AS totalPrice
FROM buyTBL GROUP BY deliveryStatus ORDER BY deliveryStatus;
-- 기대 결과: 0=4건/2260, 1=4건/1055, 2=4건/185

SELECT COUNT(*) AS purchaseCount, SUM(price * amount) AS totalPrice FROM buyTBL;
-- 기대 결과: 12건 / 3500

-- 웹의 '배송중' 선택 결과와 비교 (5~8번, 4건)
SELECT num, userID, prodName, price, amount, price * amount AS totalPrice
FROM buyTBL WHERE deliveryStatus = 1 ORDER BY num;
