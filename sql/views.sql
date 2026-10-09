-- View 1: resumo das temperaturas por categoria de localização (In/Out).
-- O CSV não possui vários device_id: room_id/id aparece como "Room Admin"
-- para todas as 97.606 linhas verificadas. Por isso, esta análise usa out/in.
CREATE OR REPLACE VIEW avg_temp_por_categoria AS
SELECT
    "out/in" AS tipo_local,
    COUNT(*)::BIGINT AS total_leituras,
    ROUND(AVG(temp)::NUMERIC, 2) AS temp_media,
    MIN(temp) AS temp_min,
    MAX(temp) AS temp_max
FROM temperature_readings
GROUP BY "out/in";

-- View 2: distribuição das leituras por hora do dia (0 a 23).
CREATE OR REPLACE VIEW leituras_por_hora AS
SELECT
    EXTRACT(HOUR FROM noted_date)::INT AS hora,
    COUNT(*)::BIGINT AS contagem
FROM temperature_readings
GROUP BY EXTRACT(HOUR FROM noted_date)::INT
ORDER BY hora;

-- View 3: temperaturas mínima e máxima e média por data.
CREATE OR REPLACE VIEW temp_max_min_por_dia AS
SELECT
    CAST(noted_date AS DATE) AS data,
    MAX(temp) AS temp_max,
    MIN(temp) AS temp_min,
    ROUND(AVG(temp)::NUMERIC, 2) AS temp_media,
    COUNT(*)::BIGINT AS total_leituras
FROM temperature_readings
GROUP BY CAST(noted_date AS DATE)
ORDER BY data;
