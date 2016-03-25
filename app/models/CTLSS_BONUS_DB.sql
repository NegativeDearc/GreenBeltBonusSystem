CREATE TABLE [MEMBER_INFO] (
  [PROJECT_NUMBER] CHAR NOT NULL ON CONFLICT FAIL UNIQUE ON CONFLICT FAIL, 
  [ININTIALOR] CHAR COLLATE NOCASE, 
  [LEADER] CHAR COLLATE NOCASE, 
  [MAJOR_PARTICIPATOR] CHAR COLLATE NOCASE, 
  [MINIOR_PARTICIPATOR] CHAR COLLATE NOCASE, 
  [MAJOR_PARTICIPATOR_COUNT] INT, 
  [MINIOR_PARTICIPATOR_COUNT] INT);


CREATE TABLE [MONTHLY_ACTION] (
  [PROJECT_NUM] CHAR NOT NULL ON CONFLICT ROLLBACK, 
  [DATE] DATE, 
  [ACTION] CHAR, 
  [SCORE] INT DEFAULT 0);


CREATE TABLE [PROJECT_INFO] (
  [PROJECT_NUMBER] CHAR NOT NULL ON CONFLICT FAIL UNIQUE ON CONFLICT FAIL, 
  [PROJECT_NAME] CHAR, 
  [PROJECT_DUE_TIME] DATE, 
  [CHECK_POINT_3_MONTH] DATE, 
  [CHECK_POINT_6_MONTH] DATE, 
  [3_MONTH_CHECK] BOOLEAN DEFAULT null, 
  [6_MONTH_CHECK] BOOLEAN DEFAULT null, 
  CONSTRAINT [sqlite_autoindex_PROJECT_INFO_1] PRIMARY KEY ([PROJECT_NUMBER]) ON CONFLICT FAIL);

CREATE TRIGGER [MONTH_3]
AFTER INSERT
ON [PROJECT_INFO]
FOR EACH ROW
BEGIN
UPDATE [PROJECT_INFO]
SET CHECK_POINT_3_MONTH = DATE(PROJECT_DUE_TIME, '+90 days');
END;

CREATE TRIGGER [MONTH_6]
AFTER INSERT
ON [PROJECT_INFO]
FOR EACH ROW
BEGIN
UPDATE [PROJECT_INFO]
SET CHECK_POINT_6_MONTH = DATE(PROJECT_DUE_TIME,'+180 days');
END;


CREATE TABLE [SCORE_CARD] (
  [PROJECT_NUMBER] CHAR DEFAULT NULL, 
  [GOLDEN_IDEA_LEVEL] CHAR, 
  [GOLDEN_IDEA_SCORE] INT, 
  [PROJECT_SCORE_LEVEL] CHAR, 
  [PROJECT_SCORE] INT, 
  [TARGET_SCORE] INT, 
  [ACTIVE_SCORE] INT DEFAULT 0, 
  [DUPLICABILITY] INT, 
  [RESOURCE_USAGE] INT, 
  [IMPLEMENT_PERIOD] INT, 
  [KPI_IMPACT] INT, 
  [COST_SAVING] MONEY);

CREATE TRIGGER [S]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = 100
                    WHERE GOLDEN_IDEA_LEVEL = "S1";
                    END;

CREATE TRIGGER [P]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = 200
                    WHERE GOLDEN_IDEA_LEVEL = "P1";
                    END;

CREATE TRIGGER [K]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = 500
                    WHERE GOLDEN_IDEA_LEVEL = "K1";
                    END;

CREATE TRIGGER [G1]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = 800
                    WHERE GOLDEN_IDEA_LEVEL = "G1";
                    END;

CREATE TRIGGER [G2]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = 1000
                    WHERE GOLDEN_IDEA_LEVEL = "G2";
                    END;

CREATE TRIGGER [G3]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = 1500
                    WHERE GOLDEN_IDEA_LEVEL = "G3";
                    END;

CREATE TRIGGER [B1]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = 2000
                    WHERE GOLDEN_IDEA_LEVEL = "B1";
                    END;

CREATE TRIGGER [B2]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = 3000
                    WHERE GOLDEN_IDEA_LEVEL = "B2";
                    END;

CREATE TRIGGER [B3]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET GOLDEN_IDEA_SCORE = 4000
                    WHERE GOLDEN_IDEA_LEVEL = "B3";
                    END;

CREATE TRIGGER [P_S]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET PROJECT_SCORE = 200
                    WHERE PROJECT_SCORE_LEVEL = "S";
                    END;

CREATE TRIGGER [P_P]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET PROJECT_SCORE = 800
                    WHERE PROJECT_SCORE_LEVEL = "P";
                    END;

CREATE TRIGGER [P_K]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET PROJECT_SCORE = 1500
                    WHERE PROJECT_SCORE_LEVEL = "K";
                    END;

CREATE TRIGGER [P_G]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET PROJECT_SCORE = 2500
                    WHERE PROJECT_SCORE_LEVEL = "G";
                    END;

CREATE TRIGGER [P_B]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET PROJECT_SCORE = 3500
                    WHERE PROJECT_SCORE_LEVEL = "B";
                    END;

CREATE TRIGGER [ACTIVE]
                    AFTER INSERT
                    ON [SCORE_CARD]
                    FOR EACH ROW
                    BEGIN
                    UPDATE [SCORE_CARD]
                    SET ACTIVE_SCORE = 100 + TARGET_SCORE
                    WHERE GOLDEN_IDEA_LEVEL = 'S1' ;

                    UPDATE [SCORE_CARD]
                    SET ACTIVE_SCORE = 200 + TARGET_SCORE
                    WHERE GOLDEN_IDEA_LEVEL = 'P1' ;

                    UPDATE [SCORE_CARD]
                    SET ACTIVE_SCORE = TARGET_SCORE
                    WHERE (GOLDEN_IDEA_LEVEL = 'K1'
                    OR GOLDEN_IDEA_LEVEL = 'G1'
                    OR GOLDEN_IDEA_LEVEL = 'G2'
                    OR GOLDEN_IDEA_LEVEL = 'G3'
                    OR GOLDEN_IDEA_LEVEL = 'B1'
                    OR GOLDEN_IDEA_LEVEL = 'B2'
                    OR GOLDEN_IDEA_LEVEL = 'B3');
                    END;


CREATE TABLE [USER_ID] (
  [ID] CHAR NOT NULL ON CONFLICT ROLLBACK, 
  [NAME] CHAR COLLATE NOCASE, 
  [FORMAT_NAME] CHAR COLLATE NOCASE);

CREATE TRIGGER [format_name]
AFTER INSERT
ON [USER_ID]
FOR EACH ROW
BEGIN
UPDATE USER_ID 
SET FORMAT_NAME='('||ID||')'||NAME;
END;


CREATE TABLE [USER_PASSWORD] (
  [USER] CHAR NOT NULL ON CONFLICT ROLLBACK UNIQUE ON CONFLICT ROLLBACK, 
  [PASSWORD] CHAR NOT NULL ON CONFLICT ROLLBACK);


CREATE VIEW [REPORT] AS 
SELECT AA.[PROJECT_NUM],AA.[DATE],AA.[ACTION],AA.[SCORE],MM.[ININTIALOR],MM.[LEADER],MM.[MAJOR_PARTICIPATOR],MM.[MAJOR_PARTICIPATOR_COUNT],
MM.[MINIOR_PARTICIPATOR],MM.[MINIOR_PARTICIPATOR_COUNT],SS.[GOLDEN_IDEA_LEVEL],SS.[PROJECT_SCORE_LEVEL]
FROM MONTHLY_ACTION AS AA
LEFT JOIN MEMBER_INFO AS MM
 ON AA.[PROJECT_NUM] = MM.[PROJECT_NUMBER]
  LEFT JOIN SCORE_CARD AS SS
   ON AA.[PROJECT_NUM] = SS.[PROJECT_NUMBER];


CREATE VIEW [TOTAL] AS 
SELECT P.[PROJECT_NUMBER],P.[PROJECT_NAME],S.[PROJECT_SCORE_LEVEL],P.[PROJECT_DUE_TIME],P.[CHECK_POINT_3_MONTH],P.[CHECK_POINT_6_MONTH],P.[3_MONTH_CHECK],P.[6_MONTH_CHECK],M.[ININTIALOR],M.[LEADER],
M.[MAJOR_PARTICIPATOR],M.[MAJOR_PARTICIPATOR_COUNT],M.[MINIOR_PARTICIPATOR],M.[MINIOR_PARTICIPATOR_COUNT],S.[GOLDEN_IDEA_SCORE],S.[PROJECT_SCORE],S.[ACTIVE_SCORE]
FROM PROJECT_INFO AS P
INNER JOIN MEMBER_INFO AS M
ON P.[PROJECT_NUMBER] = M.[PROJECT_NUMBER] 
  INNER JOIN SCORE_CARD AS S
  ON P.[PROJECT_NUMBER] = S.[PROJECT_NUMBER];