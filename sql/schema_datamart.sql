-- ============================================================================
-- PROYECTO: Clasificacion automatica y analisis morfologico de variedades de frijol
-- ASIGNATURA: Extraccion de Conocimiento en Bases de Datos (ECBD)
-- ESTUDIANTE: Kevin Hernandez Trejo (Matricula: 23300950)
-- UNIDAD II: Preparacion de datos y Diseno de Data Mart Analitico
-- GESTOR OBJETIVO: Microsoft SQL Server / Compatible ANSI SQL
-- ============================================================================

-- 1. CREACION DE LA BASE DE DATOS / ESQUEMA
-- IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'DryBean_DataMart')
--     CREATE DATABASE DryBean_DataMart;
-- GO
-- USE DryBean_DataMart;
-- GO

-- 2. ELIMINACION PREVIA DE TABLAS (ORDEN POR CLAVES FORANEAS)
IF OBJECT_ID('dbo.fact_bean_morphology', 'U') IS NOT NULL DROP TABLE dbo.fact_bean_morphology;
IF OBJECT_ID('dbo.dim_forma', 'U') IS NOT NULL DROP TABLE dbo.dim_forma;
IF OBJECT_ID('dbo.dim_tamano', 'U') IS NOT NULL DROP TABLE dbo.dim_tamano;
IF OBJECT_ID('dbo.dim_variedad', 'U') IS NOT NULL DROP TABLE dbo.dim_variedad;
GO

-- 3. TABLA DIMENSIONAL: dim_variedad
-- Almacena las 7 clases registradas de semillas de frijol con metadata descriptiva
CREATE TABLE dbo.dim_variedad (
    id_variedad INT IDENTITY(1,1) PRIMARY KEY,
    nombre_variedad VARCHAR(50) NOT NULL UNIQUE,
    codigo_variedad CHAR(3) NOT NULL,
    descripcion_agronomica VARCHAR(255) NULL
);
GO

-- 4. TABLA DIMENSIONAL: dim_tamano
-- Segmentacion analitica segun la superficie proyectada en pixeles (Area)
CREATE TABLE dbo.dim_tamano (
    id_tamano INT IDENTITY(1,1) PRIMARY KEY,
    categoria_tamano VARCHAR(50) NOT NULL,
    rango_area_min FLOAT NOT NULL,
    rango_area_max FLOAT NOT NULL,
    descripcion VARCHAR(150) NULL
);
GO

-- 5. TABLA DIMENSIONAL: dim_forma
-- Segmentacion analitica segun la relacion de aspecto y redondez
CREATE TABLE dbo.dim_forma (
    id_forma INT IDENTITY(1,1) PRIMARY KEY,
    categoria_forma VARCHAR(50) NOT NULL,
    rango_aspect_ratio_min FLOAT NOT NULL,
    rango_aspect_ratio_max FLOAT NOT NULL,
    descripcion VARCHAR(150) NULL
);
GO

-- 6. TABLA DE HECHOS: fact_bean_morphology
-- Cada registro representa la medicion individual de un grano fotogrametrico limpio
CREATE TABLE dbo.fact_bean_morphology (
    id_grano INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Claves foraneas a dimensiones
    id_variedad INT NOT NULL,
    id_tamano INT NOT NULL,
    id_forma INT NOT NULL,
    
    -- Medidas de tamano (continuas y enteras originales)
    area INT NOT NULL,
    perimeter FLOAT NOT NULL,
    major_axis_length FLOAT NOT NULL,
    minor_axis_length FLOAT NOT NULL,
    convex_area INT NOT NULL,
    equiv_diameter FLOAT NOT NULL,
    
    -- Medidas de proporcion y elongacion
    aspect_ratio FLOAT NOT NULL,
    eccentricity FLOAT NOT NULL,
    extent FLOAT NOT NULL,
    solidity FLOAT NOT NULL,
    
    -- Descriptores de forma y redondez
    roundness FLOAT NOT NULL,
    compactness FLOAT NOT NULL,
    shape_factor_1 FLOAT NOT NULL,
    shape_factor_2 FLOAT NOT NULL,
    shape_factor_3 FLOAT NOT NULL,
    shape_factor_4 FLOAT NOT NULL,
    
    -- Metadatos de auditoria
    fecha_carga DATETIME DEFAULT GETDATE(),
    
    -- Restricciones de integridad referencial
    CONSTRAINT FK_fact_variedad FOREIGN KEY (id_variedad) REFERENCES dbo.dim_variedad(id_variedad),
    CONSTRAINT FK_fact_tamano FOREIGN KEY (id_tamano) REFERENCES dbo.dim_tamano(id_tamano),
    CONSTRAINT FK_fact_forma FOREIGN KEY (id_forma) REFERENCES dbo.dim_forma(id_forma)
);
GO

-- 7. CREACION DE INDICES PARA OPTIMIZACION DE CONSULTAS BI
CREATE NONCLUSTERED INDEX IX_fact_variedad ON dbo.fact_bean_morphology(id_variedad);
CREATE NONCLUSTERED INDEX IX_fact_tamano ON dbo.fact_bean_morphology(id_tamano);
CREATE NONCLUSTERED INDEX IX_fact_forma ON dbo.fact_bean_morphology(id_forma);
CREATE NONCLUSTERED INDEX IX_fact_area ON dbo.fact_bean_morphology(area);
GO

-- 8. POBLADO DE CATALOGOS DIMENSIONALES (DML)
INSERT INTO dbo.dim_variedad (nombre_variedad, codigo_variedad, descripcion_agronomica)
VALUES 
('BARBUNYA', 'BAR', 'Grano pinto con patron moteado, tamano mediano a grande'),
('BOMBAY',   'BOM', 'Grano blanco de tamano muy grande, el de mayor area promedio'),
('CALI',     'CAL', 'Grano alargado con coloracion rojiza/pardo'),
('DERMASON', 'DER', 'Grano blanco y plano, tamano medio-pequeno, clase mayoritaria'),
('HOROZ',    'HOR', 'Grano cilindrico y alargado, baja relacion de aspecto'),
('SEKER',    'SEK', 'Grano esferico y compacto, mayor redondez promedio'),
('SIRA',     'SIR', 'Grano pequeno similar a Dermason pero con mayor excentricidad');
GO

INSERT INTO dbo.dim_tamano (categoria_tamano, rango_area_min, rango_area_max, descripcion)
VALUES
('Pequeno',        0,      45000,   'Granos compactos con area menor a 45,000 pixeles'),
('Mediano',        45001,  70000,   'Granos estandar con area entre 45,001 y 70,000 pixeles'),
('Grande',         70001,  110000,  'Granos grandes con area entre 70,001 y 110,000 pixeles'),
('Muy Grande',     110001, 300000,  'Granos gigantes (ej. Bombay) superiores a 110,000 pixeles');
GO

INSERT INTO dbo.dim_forma (categoria_forma, rango_aspect_ratio_min, rango_aspect_ratio_max, descripcion)
VALUES
('Casi Esferica',  1.00, 1.30, 'Granos altamente redondeados con poca elongacion'),
('Semi-Ovalada',   1.31, 1.65, 'Granos ovalados con elongacion moderada'),
('Elongada',       1.66, 2.05, 'Granos alargados con alta razon eje mayor/menor'),
('Muy Elongada',   2.06, 3.50, 'Granos extremadamente cilindricos o alargados');
GO

-- 9. VISTAS ANALITICAS PARA CONECTIVIDAD CON POWER BI
CREATE OR ALTER VIEW dbo.vw_resumen_morfologico_variedad AS
SELECT 
    v.nombre_variedad AS Variedad,
    COUNT(f.id_grano) AS Total_Granos,
    ROUND(AVG(CAST(f.area AS FLOAT)), 2) AS Area_Promedio,
    ROUND(AVG(f.perimeter), 2) AS Perimetro_Promedio,
    ROUND(AVG(f.aspect_ratio), 4) AS AspectRatio_Promedio,
    ROUND(AVG(f.roundness), 4) AS Redondez_Promedio,
    ROUND(AVG(f.compactness), 4) AS Compacidad_Promedio,
    ROUND(MIN(f.area), 0) AS Area_Minima,
    ROUND(MAX(f.area), 0) AS Area_Maxima
FROM dbo.fact_bean_morphology f
INNER JOIN dbo.dim_variedad v ON f.id_variedad = v.id_variedad
GROUP BY v.nombre_variedad;
GO

CREATE OR ALTER VIEW dbo.vw_distribucion_tamano_variedad AS
SELECT 
    v.nombre_variedad AS Variedad,
    t.categoria_tamano AS Categoria_Tamano,
    COUNT(f.id_grano) AS Cantidad_Granos,
    ROUND(AVG(f.solidity), 4) AS Solidez_Promedio
FROM dbo.fact_bean_morphology f
INNER JOIN dbo.dim_variedad v ON f.id_variedad = v.id_variedad
INNER JOIN dbo.dim_tamano t ON f.id_tamano = t.id_tamano
GROUP BY v.nombre_variedad, t.categoria_tamano;
GO
