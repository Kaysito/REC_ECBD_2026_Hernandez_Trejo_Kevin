let
    Source = Sql.Database("(localdb)\MSSQLLocalDB", "DryBean_DataMart", [Query="SELECT f.id_grano, f.id_variedad, f.id_tamano, f.id_forma, f.area, f.perimeter, f.major_axis_length, f.minor_axis_length, f.convex_area, f.equiv_diameter, f.aspect_ratio, f.eccentricity, f.extent, f.solidity, f.roundness, f.compactness, f.shape_factor_1, f.shape_factor_2, f.shape_factor_3, f.shape_factor_4, CONVERT(varchar(19), f.fecha_carga, 120) AS fecha_carga, v.nombre_variedad AS variedad, t.categoria_tamano, fo.categoria_forma FROM dbo.fact_bean_morphology f INNER JOIN dbo.dim_variedad v ON f.id_variedad=v.id_variedad INNER JOIN dbo.dim_tamano t ON f.id_tamano=t.id_tamano INNER JOIN dbo.dim_forma fo ON f.id_forma=fo.id_forma"]),
    Typed = Table.TransformColumnTypes(Source, {
            {"id_grano", Int64.Type},
            {"id_variedad", Int64.Type},
            {"id_tamano", Int64.Type},
            {"id_forma", Int64.Type},
            {"area", Int64.Type},
            {"perimeter", type number},
            {"major_axis_length", type number},
            {"minor_axis_length", type number},
            {"convex_area", Int64.Type},
            {"equiv_diameter", type number},
            {"aspect_ratio", type number},
            {"eccentricity", type number},
            {"extent", type number},
            {"solidity", type number},
            {"roundness", type number},
            {"compactness", type number},
            {"shape_factor_1", type number},
            {"shape_factor_2", type number},
            {"shape_factor_3", type number},
            {"shape_factor_4", type number},
            {"fecha_carga", Text.Type},
            {"variedad", Text.Type},
            {"categoria_tamano", Text.Type},
            {"categoria_forma", Text.Type}
        }, "en-US")
in
    Typed
