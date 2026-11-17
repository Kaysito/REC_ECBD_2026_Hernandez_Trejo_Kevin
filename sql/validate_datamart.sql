USE DryBean_DataMart;
GO
SET NOCOUNT ON;

SELECT 'dim_variedad' AS tabla, COUNT(*) AS registros FROM dbo.dim_variedad
UNION ALL SELECT 'dim_tamano', COUNT(*) FROM dbo.dim_tamano
UNION ALL SELECT 'dim_forma', COUNT(*) FROM dbo.dim_forma
UNION ALL SELECT 'fact_bean_morphology', COUNT(*) FROM dbo.fact_bean_morphology;

SELECT
    COUNT(*) AS hechos,
    COUNT(DISTINCT id_grano) AS granos_unicos,
    SUM(CASE WHEN id_variedad IS NULL OR id_tamano IS NULL OR id_forma IS NULL THEN 1 ELSE 0 END) AS claves_invalidas
FROM dbo.fact_bean_morphology;

DBCC CHECKCONSTRAINTS ('dbo.fact_bean_morphology') WITH ALL_CONSTRAINTS;

SELECT * FROM dbo.vw_resumen_morfologico_variedad ORDER BY Variedad;
SELECT * FROM dbo.vw_distribucion_tamano_variedad ORDER BY Variedad, Categoria_Tamano;
GO
