-- Ejecutar con SQLCMD y proporcionar la ruta mediante -v DataFile="ruta.csv"
USE DryBean_DataMart;
GO

-- La carga es repetible: sustituye los hechos sin duplicarlos.
TRUNCATE TABLE dbo.fact_bean_morphology;
GO

IF OBJECT_ID('dbo.stg_dry_beans', 'U') IS NOT NULL DROP TABLE dbo.stg_dry_beans;
GO

CREATE TABLE dbo.stg_dry_beans (
    Area INT,
    Perimeter FLOAT,
    MajorAxisLength FLOAT,
    MinorAxisLength FLOAT,
    AspectRatio FLOAT,
    Eccentricity FLOAT,
    ConvexArea INT,
    EquivDiameter FLOAT,
    Extent FLOAT,
    Solidity FLOAT,
    Roundness FLOAT,
    Compactness FLOAT,
    ShapeFactor1 FLOAT,
    ShapeFactor2 FLOAT,
    ShapeFactor3 FLOAT,
    ShapeFactor4 FLOAT,
    Class VARCHAR(50)
);
GO

BULK INSERT dbo.stg_dry_beans
FROM '$(DataFile)'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDQUOTE = '"',
    ROWTERMINATOR = '0x0a',
    TABLOCK
);
GO

INSERT INTO dbo.fact_bean_morphology (
    id_variedad, id_tamano, id_forma, id_tiempo,
    area, perimeter, major_axis_length, minor_axis_length,
    convex_area, equiv_diameter, aspect_ratio, eccentricity,
    extent, solidity, roundness, compactness,
    shape_factor_1, shape_factor_2, shape_factor_3, shape_factor_4
)
SELECT
    v.id_variedad,
    t.id_tamano,
    f.id_forma,
    CONVERT(INT, CONVERT(CHAR(8), GETDATE(), 112)),
    s.Area, s.Perimeter, s.MajorAxisLength, s.MinorAxisLength,
    s.ConvexArea, s.EquivDiameter, s.AspectRatio, s.Eccentricity,
    s.Extent, s.Solidity, s.Roundness, s.Compactness,
    s.ShapeFactor1, s.ShapeFactor2, s.ShapeFactor3, s.ShapeFactor4
FROM dbo.stg_dry_beans s
INNER JOIN dbo.dim_variedad v
    ON v.nombre_variedad = REPLACE(LTRIM(RTRIM(s.Class)), CHAR(13), '')
INNER JOIN dbo.dim_tamano t
    ON s.Area >= t.rango_area_min AND s.Area < t.rango_area_max
INNER JOIN dbo.dim_forma f
    ON s.AspectRatio >= f.rango_aspect_ratio_min AND s.AspectRatio < f.rango_aspect_ratio_max;
GO

DROP TABLE dbo.stg_dry_beans;
GO
