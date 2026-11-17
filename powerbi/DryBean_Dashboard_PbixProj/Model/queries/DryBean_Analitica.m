let
    Source = Csv.Document(File.Contents("C:\\Users\\crepe\\Documents\\Proyectos\\REC_ECBD_2026_Hernandez_Trejo_Kevin\\data\\bi\\drybean_powerbi.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
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
