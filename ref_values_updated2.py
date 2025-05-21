# ref_values_updated.py

# Structure for REF_VALUES:
# Each entry is a tuple: (test_name, test_info_dict)
# test_info_dict:
#   "unit": str (e.g., "mg/dL") or None for unit-less values
#   "references": list of dicts, each representing a specific reference condition
#     - "condition": str (textual description of the condition, e.g., "Homens", "Crianças: 0 a 2 anos")
#     - "type": "range", "min_inclusive", "max_inclusive", "qualitative", "textual_range_inclusive_lower_bound" (default is "range")
#     - "min": float/int (for quantitative)
#     - "max": float/int (for quantitative)
#     - "expected": list of str (for qualitative)
#     - "age_min": int (optional, for age-based conditions in years, inclusive)
#     - "age_max": int (optional, for age-based conditions in years, inclusive)
#     - "gender": "M" or "F" (optional, for gender-based conditions)
#     - "priority": int (optional, higher value means higher priority, default 0. Specific conditions should have higher priority)

REF_VALUES = [
    ("HEMACIAS (Hemograma)", {
        "unit": "milhões/mm3",
        "references": [
            {"condition": "Homens", "gender": "M", "min": 4.50, "max": 6.10, "priority": 2},
            {"condition": "Mulheres", "gender": "F", "min": 4.00, "max": 5.40, "priority": 2},
            {"condition": "Crianças", "age_min": 0, "age_max": 18, "min": 4.07, "max": 5.37, "priority": 1},
            {"condition": "Acima de 70 anos", "age_min": 70, "min": 3.90, "max": 5.36, "priority": 1},
            {"condition": "Geral", "min": 3.9, "max": 6.1, "priority": 0} # Fallback
        ]
    }),
    ("HEMOGLOBINA (Hemograma)", {
        "unit": "g/dL",
        "references": [
            {"condition": "Homens", "gender": "M", "min": 13.0, "max": 16.5, "priority": 2},
            {"condition": "Mulheres", "gender": "F", "min": 12.0, "max": 15.8, "priority": 2},
            {"condition": "Crianças", "age_min": 0, "age_max": 18, "min": 10.5, "max": 14.0, "priority": 1},
            {"condition": "Acima de 70 anos", "age_min": 70, "min": 11.5, "max": 15.1, "priority": 1},
            {"condition": "Geral", "min": 12.0, "max": 17.5, "priority": 0} # Fallback
        ]
    }),
    ("HEMATOCRITO (Hemograma)", {
        "unit": "%",
        "references": [
            {"condition": "Homens", "gender": "M", "min": 36.0, "max": 54.0, "priority": 2},
            {"condition": "Mulheres", "gender": "F", "min": 33.0, "max": 47.8, "priority": 2},
            {"condition": "Crianças", "age_min": 0, "age_max": 18, "min": 30.0, "max": 44.5, "priority": 1},
            {"condition": "Acima de 70 anos", "age_min": 70, "min": 33.0, "max": 46.0, "priority": 1},
            {"condition": "Geral", "min": 34.9, "max": 52.0, "priority": 0} # Fallback
        ]
    }),
    ("VCM (Hemograma)", {
        "unit": "fl",
        "references": [
            {"condition": "Geral", "min": 80.0, "max": 98.0, "priority": 0},
            {"condition": "Crianças", "age_min": 0, "age_max": 18, "min": 70.0, "max": 86.0, "priority": 1}
        ]
    }),
    ("HCM (Hemograma)", {
        "unit": "pg",
        "references": [
            {"condition": "Geral", "min": 26.8, "max": 32.9, "priority": 0}, # Homens range, closest general
            {"condition": "Mulheres", "gender": "F", "min": 26.2, "max": 32.6, "priority": 1},
            {"condition": "Crianças", "age_min": 0, "age_max": 18, "min": 23.2, "max": 31.7, "priority": 1}
        ]
    }),
    ("CHCM (Hemograma)", {
        "unit": "g/dl",
        "references": [
            {"condition": "Geral", "min": 30.0, "max": 36.5, "priority": 0}
        ]
    }),
    ("RDW (Hemograma)", {
        "unit": "%",
        "references": [
            {"condition": "Geral", "min": 11.0, "max": 16.0, "priority": 0}
        ]
    }),

    ("GLICOSE", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Normal", "min": 70, "max": 99, "type": "range", "priority": 1},
            {"condition": "Intolerância glicose Jejum", "min": 100, "max": 125, "type": "range", "priority": 1},
            {"condition": "Diabetes mellitus", "min": 126, "type": "min_inclusive", "priority": 1},
            {"condition": "Geral", "min": 70, "max": 99, "type": "range", "priority": 0} # Fallback
        ]
    }),
    ("COLESTEROL TOTAL", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Geral", "max": 190, "type": "max_inclusive", "priority": 0} # Example, based on common lab values
        ]
    }),
    ("TRIGLICERÍDEOS", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Geral", "max": 150, "type": "max_inclusive", "priority": 0} # Example
        ]
    }),
    ("COLESTEROL HDL", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Geral", "min": 40, "type": "min_inclusive", "priority": 0} # Example
        ]
    }),
    ("COLESTEROL LDL", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Geral", "max": 130, "type": "max_inclusive", "priority": 0} # Example
        ]
    }),
    ("COLESTEROL NÃO HDL", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Geral", "max": 160, "type": "max_inclusive", "priority": 0} # Example
        ]
    }),
    ("CREATININA", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Adultos: Homens", "gender": "M", "age_min": 18, "min": 0.7, "max": 1.2, "priority": 2},
            {"condition": "Adultos: Mulheres", "gender": "F", "age_min": 18, "min": 0.5, "max": 0.9, "priority": 2},
            {"condition": "Recém Nascido (prematuros)", "age_min": 0, "age_max": 0, "min": 0.29, "max": 1.04, "priority": 3}, # assuming age 0 covers prematures
            {"condition": "Recém Nascido (de termo)", "age_min": 0, "age_max": 0, "min": 0.24, "max": 0.85, "priority": 3}, # assuming age 0 covers term babies
            {"condition": "Crianças: 0 a 2 anos", "age_min": 0, "age_max": 2, "min": 0.17, "max": 0.42, "priority": 1},
            {"condition": "Crianças: 3 a 4 anos", "age_min": 3, "age_max": 4, "min": 0.31, "max": 0.47, "priority": 1},
            {"condition": "Crianças: 5 a 8 anos", "age_min": 5, "age_max": 8, "min": 0.32, "max": 0.60, "priority": 1},
            {"condition": "Crianças: 9 a 10 anos", "age_min": 9, "age_max": 10, "min": 0.39, "max": 0.73, "priority": 1},
            {"condition": "Crianças: 11 a 15 anos", "age_min": 11, "age_max": 15, "min": 0.53, "max": 0.87, "priority": 1},
            {"condition": "Geral Adultos", "age_min": 18, "min": 0.5, "max": 1.2, "priority": 0}, # Fallback for adults
            {"condition": "Geral", "min": 0.1, "max": 1.5, "priority": 0} # Generic fallback
        ]
    }),
    ("eTFG (ESTIMATIVA DA TAXA DE FILTRAÇÃO GLOMERULAR)", { # New
        "unit": "mL/min/1.73m2",
        "references": [
            {"condition": "Normal", "expected": [">90", "maior que 90"], "type": "qualitative", "priority": 1},
            {"condition": "Redução Discreta", "min": 60, "max": 89, "type": "range", "priority": 1},
            {"condition": "Redução Discreta - Moderada", "min": 45, "max": 59, "type": "range", "priority": 1},
            {"condition": "Redução Moderada - Severa", "min": 30, "max": 44, "type": "range", "priority": 1},
            {"condition": "Redução Severa", "min": 15, "max": 29, "type": "range", "priority": 1},
            {"condition": "Falência Renal", "expected": ["<15", "menor que 15"], "type": "qualitative", "priority": 1},
            {"condition": "Não Calculada (Menores que 18 anos)", "age_max": 17, "expected": ["*"], "type": "qualitative", "priority": 2}, # Specific for children's "*"
            {"condition": "Geral", "expected": [">90", "maior que 90", "*"], "type": "qualitative", "priority": 0} # Fallback for other texts like "*"
        ]
    }),
    ("TSH", {
        "unit": "µUI/mL",
        "references": [
            {"condition": "Geral", "min": 0.27, "max": 4.20, "priority": 3},
            {"condition": "Gestantes: 1o trimestre", "min": 0.10, "max": 2.50, "priority": 2, "gender": "F"}, # Pregnancy is a specific condition
            {"condition": "Gestantes: 2o trimestre", "min": 0.20, "max": 3.00, "priority": 2, "gender": "F"},
            {"condition": "Gestantes: 3o trimestre", "min": 0.30, "max": 3.00, "priority": 2, "gender": "F"},
            {"condition": "Criança: 0 a 6 dias", "age_min": 0, "age_max": 0, "min": 0.70, "max": 15.20, "priority": 1},
            {"condition": "Criança: 7 dias a 3 meses", "age_min": 0, "age_max": 0, "min": 0.72, "max": 11.00, "priority": 1}, # Approx age 0
            {"condition": "Criança: 4 meses a 1 ano", "age_min": 0, "age_max": 1, "min": 0.73, "max": 8.35, "priority": 1}, # Approx age 0-1
            {"condition": "Criança: 2 anos a 6 anos", "age_min": 2, "age_max": 6, "min": 0.70, "max": 5.97, "priority": 1},
            {"condition": "Criança: 7 anos a 11 anos", "age_min": 7, "age_max": 11, "min": 0.60, "max": 4.84, "priority": 1},
            {"condition": "Criança: 12 anos a 20 anos", "age_min": 12, "age_max": 20, "min": 0.51, "max": 4.30, "priority": 1},
        ]
    }),
    ("LH - HORMONIO LUTEINIZANTE", {
        "unit": "mUI/mL",
        "references": [
            {"condition": "Homens", "gender": "M", "min": 1.70, "max": 8.60, "priority": 2},
            {"condition": "Mulheres: Fase folicular", "gender": "F", "min": 2.40, "max": 12.60, "priority": 2},
            {"condition": "Mulheres: Fase ovulatória", "gender": "F", "min": 14.00, "max": 95.60, "priority": 2},
            {"condition": "Mulheres: Fase lutea", "gender": "F", "min": 1.00, "max": 11.40, "priority": 2},
            {"condition": "Mulheres: Pos menopausa", "gender": "F", "min": 7.70, "max": 58.50, "priority": 2},
            {"condition": "Criança Masculino: 1 a 12 meses", "age_min": 0, "age_max": 1, "gender": "M", "min": 0.10, "max": 0.40, "type": "range_inclusive_lower_bound", "priority": 1}, # < 0,10 to 0.40
            {"condition": "Criança Feminino: 1 a 12 meses", "age_min": 0, "age_max": 1, "gender": "F", "min": 0.10, "max": 0.40, "type": "range_inclusive_lower_bound", "priority": 1},
            {"condition": "Criança Masculino: 1 a 5 anos", "age_min": 1, "age_max": 5, "gender": "M", "min": 0.10, "max": 1.30, "type": "range_inclusive_lower_bound", "priority": 1},
            {"condition": "Criança Feminino: 1 a 5 anos", "age_min": 1, "age_max": 5, "gender": "F", "min": 0.10, "max": 0.50, "type": "range_inclusive_lower_bound", "priority": 1},
            {"condition": "Geral", "min": 0.1, "max": 100, "priority": 0} # Fallback
        ]
    }),
    ("FSH - HORMÔNIO FOLÍCULO ESTIMULANTE", {
        "unit": "mUI/mL",
        "references": [
            {"condition": "Mulheres: Fase folicular", "gender": "F", "min": 3.5, "max": 12.5, "priority": 2},
            {"condition": "Mulheres: Fase ovulatória", "gender": "F", "min": 4.7, "max": 21.5, "priority": 2},
            {"condition": "Mulheres: Fase lutea", "gender": "F", "min": 1.7, "max": 7.7, "priority": 2},
            {"condition": "Mulheres: Pos menopausa", "gender": "F", "min": 25.8, "max": 134.8, "priority": 2},
            {"condition": "Homens", "gender": "M", "min": 1.5, "max": 12.4, "priority": 2},
            {"condition": "Criança Feminino: 1 a 5 anos", "age_min": 1, "age_max": 5, "gender": "F", "min": 0.2, "max": 2.8, "priority": 1},
            {"condition": "Criança Masculino: 1 a 5 anos", "age_min": 1, "age_max": 5, "gender": "M", "min": 0.2, "max": 11.1, "priority": 1},
            {"condition": "Criança Feminino: 6 a 11 anos", "age_min": 6, "age_max": 11, "gender": "F", "min": 0.4, "max": 3.8, "priority": 1},
            {"condition": "Criança Masculino: 6 a 11 anos", "age_min": 6, "age_max": 11, "gender": "M", "min": 0.3, "max": 11.1, "priority": 1},
            {"condition": "Criança Feminino: 11 a 13 anos", "age_min": 11, "age_max": 13, "gender": "F", "min": 0.4, "max": 4.6, "priority": 1},
            {"condition": "Criança Masculino: 11 a 13 anos", "age_min": 11, "age_max": 13, "gender": "M", "min": 2.1, "max": 11.1, "priority": 1},
            {"condition": "Criança Feminino: 14 a 17 anos", "age_min": 14, "age_max": 17, "gender": "F", "min": 1.5, "max": 12.9, "priority": 1},
            {"condition": "Criança Masculino: 14 a 17 anos", "age_min": 14, "age_max": 17, "gender": "M", "min": 1.6, "max": 17.0, "priority": 1},
            {"condition": "Geral", "min": 0.1, "max": 150, "priority": 0} # Fallback
        ]
    }),
    ("VITAMINA D3 25-HIDROXI", {
        "unit": "ng/mL",
        "references": [
            {"condition": "Desejável (População sem comorbidades)", "min": 20.0, "type": "min_inclusive", "priority": 1},
            {"condition": "Grupos de risco", "min": 30, "max": 60, "priority": 1},
            {"condition": "Geral", "min": 20.0, "type": "min_inclusive", "priority": 0} # Fallback
        ]
    }),
    ("1,25-DIHIDROXIVITAMINA D", { # New
        "unit": "pg/mL",
        "references": [
            {"condition": "Geral", "min": 19.9, "max": 79.3, "priority": 0}
        ]
    }),
    ("UREIA", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Geral", "min": 15, "max": 50, "priority": 0}
        ]
    }),
    ("MAGNÉSIO", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Adultos", "age_min": 18, "min": 1.6, "max": 2.6, "priority": 1},
            {"condition": "60 a 90 anos", "age_min": 60, "age_max": 90, "min": 1.6, "max": 2.4, "priority": 2},
            {"condition": "Maior que 90 anos", "age_min": 90, "min": 1.7, "max": 2.3, "priority": 2},
            {"condition": "Recém Nascido", "age_min": 0, "age_max": 0, "min": 1.5, "max": 2.2, "priority": 2},
            {"condition": "5 meses a 6 anos", "age_min": 0, "age_max": 6, "min": 1.7, "max": 2.3, "priority": 1},
            {"condition": "7 a 12 anos", "age_min": 7, "age_max": 12, "min": 1.7, "max": 2.1, "priority": 1},
            {"condition": "13 a 20 anos", "age_min": 13, "age_max": 20, "min": 1.7, "max": 2.2, "priority": 1},
            {"condition": "Geral", "min": 1.5, "max": 2.6, "priority": 0} # Fallback
        ]
    }),
    ("FÓSFORO", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Adultos", "age_min": 18, "min": 2.5, "max": 4.5, "priority": 1},
            {"condition": "Masculina: 1 a 30 dias", "gender": "M", "age_min": 0, "age_max": 0, "min": 3.9, "max": 6.9, "priority": 2},
            {"condition": "Masculina: 1 a 12 meses", "gender": "M", "age_min": 0, "age_max": 1, "min": 3.5, "max": 6.6, "priority": 2},
            {"condition": "Masculina: 1 a 15 anos", "gender": "M", "age_min": 1, "age_max": 15, "min": 3.0, "max": 6.0, "priority": 2},
            {"condition": "Masculina: 16 a 18 anos", "gender": "M", "age_min": 16, "age_max": 18, "min": 2.7, "max": 4.9, "priority": 2},
            {"condition": "Feminina: 1 a 30 dias", "gender": "F", "age_min": 0, "age_max": 0, "min": 4.3, "max": 7.7, "priority": 2},
            {"condition": "Feminina: 1 a 12 meses", "gender": "F", "age_min": 0, "age_max": 1, "min": 3.7, "max": 6.5, "priority": 2},
            {"condition": "Feminina: 1 a 15 anos", "gender": "F", "age_min": 1, "age_max": 15, "min": 3.2, "max": 6.0, "priority": 2},
            {"condition": "Feminina: 16 a 18 anos", "gender": "F", "age_min": 16, "age_max": 18, "min": 2.5, "max": 4.8, "priority": 2},
            {"condition": "Geral", "min": 2.5, "max": 7.7, "priority": 0} # Fallback
        ]
    }),
    ("CÁLCIO", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Adultos: 18 a 60 anos", "age_min": 18, "age_max": 60, "min": 8.6, "max": 10.0, "priority": 2},
            {"condition": "Adultos: 60 a 90 anos", "age_min": 60, "age_max": 90, "min": 8.8, "max": 10.2, "priority": 2},
            {"condition": "Adultos: Superior a 90 anos", "age_min": 90, "min": 8.2, "max": 9.6, "priority": 2},
            {"condition": "Criancas: 0 a 10 dias", "age_min": 0, "age_max": 0, "min": 7.6, "max": 10.4, "priority": 1},
            {"condition": "Criancas: 10 dias a 02 anos", "age_min": 0, "age_max": 2, "min": 9.0, "max": 11.0, "priority": 1},
            {"condition": "Criancas: 02 a 12 anos", "age_min": 2, "age_max": 12, "min": 8.8, "max": 10.8, "priority": 1},
            {"condition": "Criancas: 12 a 18 anos", "age_min": 12, "age_max": 18, "min": 8.4, "max": 10.2, "priority": 1},
            {"condition": "Geral", "min": 7.6, "max": 11.0, "priority": 0} # Fallback
        ]
    }),
    ("TRANSAMINASE OXALACÉTICA TGO (AST)", {
        "unit": "U/L",
        "references": [
            {"condition": "HOMENS", "gender": "M", "max": 40, "type": "max_inclusive", "priority": 1},
            {"condition": "MULHERES", "gender": "F", "max": 32, "type": "max_inclusive", "priority": 1},
            {"condition": "Geral", "max": 40, "type": "max_inclusive", "priority": 0} # Fallback
        ]
    }),
    ("TRANSAMINASE PIRÚVICA TGP (ALT)", {
        "unit": "U/L",
        "references": [
            {"condition": "HOMENS", "gender": "M", "max": 41, "type": "max_inclusive", "priority": 1},
            {"condition": "MULHERES", "gender": "F", "max": 33, "type": "max_inclusive", "priority": 1},
            {"condition": "Geral", "max": 41, "type": "max_inclusive", "priority": 0} # Fallback
        ]
    }),
    ("FOSFATASE ALCALINA", {
        "unit": "U/L",
        "references": [
            {"condition": "Adultos: Homens", "gender": "M", "age_min": 18, "min": 40, "max": 129, "priority": 1},
            {"condition": "Adultos: Mulheres", "gender": "F", "age_min": 18, "min": 35, "max": 104, "priority": 1},
            {"condition": "Crianças: 0 a 1 ano", "age_min": 0, "age_max": 1, "min": 83, "max": 469, "priority": 1},
            {"condition": "Crianças: 2 a 9 anos", "age_min": 2, "age_max": 9, "min": 142, "max": 335, "priority": 1},
            {"condition": "Geral Adultos", "age_min": 18, "min": 35, "max": 129, "priority": 0}
        ]
    }),
    ("GAMA GLUTAMIL TRANSFERASE", {
        "unit": "U/L",
        "references": [
            {"condition": "Homem", "gender": "M", "max": 60, "type": "max_inclusive", "priority": 1},
            {"condition": "Mulher", "gender": "F", "max": 40, "type": "max_inclusive", "priority": 1},
            {"condition": "Geral", "max": 60, "type": "max_inclusive", "priority": 0} # Fallback
        ]
    }),
    ("BILIRRUBINA TOTAL...", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Adultos", "age_min": 18, "max": 1.2, "type": "max_inclusive", "priority": 1},
            {"condition": "Crianças", "age_max": 18, "max": 1.0, "type": "max_inclusive", "priority": 1},
            {"condition": "Recém Nascido Prematuro (1º dia)", "age_min": 0, "age_max": 0, "min": 1.0, "max": 8.0, "priority": 2},
            {"condition": "Recém Nascido a termo (1º dia)", "age_min": 0, "age_max": 0, "min": 2.0, "max": 6.0, "priority": 2},
            {"condition": "Geral", "max": 1.2, "type": "max_inclusive", "priority": 0} # Fallback
        ]
    }),
    ("BILIRRUBINA DIRETA..", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Geral", "max": 0.20, "type": "max_inclusive", "priority": 0}
        ]
    }),
    ("BILIRRUBINA INDIRETA", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Geral", "max": 0.75, "type": "max_inclusive", "priority": 0}
        ]
    }),
    ("CULTURA DE URINA", {
        "references": [
            {"condition": "Geral", "expected": ["NEGATIVA"], "type": "qualitative"}
        ]
    }),
    ("SANGUE OCULTO - PESQUISA", {
        "references": [
            {"condition": "Geral", "expected": ["NEGATIVA"], "type": "qualitative"}
        ]
    }),
    ("CARIÓTIPO EM SANGUE PERIFÉRICO", {
        "references": [
            {"condition": "Cariótipo Masculino", "gender": "M", "expected": ["46,XY", "46,X,Yqh+"], "type": "qualitative", "priority": 1}, # Added Yqh+
            {"condition": "Cariótipo Feminino", "gender": "F", "expected": ["46,XX"], "type": "qualitative", "priority": 1},
            {"condition": "Geral", "expected": ["46,XY", "46,XX", "46,X,Yqh+"], "type": "qualitative", "priority": 0} # Fallback for expected variations
        ]
    }),
    ("CARIÓTIPO COM BANDA G PARA 50 CÉLULAS", {
        "references": [
            {"condition": "Cariótipo Masculino", "gender": "M", "expected": ["46,XY", "46,X,Yqh+"], "type": "qualitative", "priority": 1}, # Added Yqh+
            {"condition": "Cariótipo Feminino", "gender": "F", "expected": ["46,XX"], "type": "qualitative", "priority": 1},
            {"condition": "Geral", "expected": ["46,XY", "46,XX", "46,X,Yqh+"], "type": "qualitative", "priority": 0} # Fallback for expected variations
        ]
    }),
    ("CEA/ANTIGENO CARCINOEMBRIOGENICO", {
        "unit": "ng/mL",
        "references": [
            {"condition": "Não Fumantes", "max": 3.80, "type": "max_inclusive", "priority": 1},
            {"condition": "Fumantes", "max": 5.50, "type": "max_inclusive", "priority": 1},
            {"condition": "Geral", "max": 5.50, "type": "max_inclusive", "priority": 0} # Fallback
        ]
    }),
    ("PSA LIVRE", {
        "unit": "ng/mL",
        "references": [
            {"condition": "Geral", "min": 0, "max": 10, "priority": 0} # Need to find specific ranges if any
        ]
    }),
    ("PSA TOTAL", {
        "unit": "ng/mL",
        "references": [
            {"condition": "< 40 anos", "age_max": 40, "max": 1.4, "type": "max_inclusive", "priority": 1},
            {"condition": "40 a 49 anos", "age_min": 40, "age_max": 49, "max": 2.0, "type": "max_inclusive", "priority": 1},
            {"condition": "50 a 59 anos", "age_min": 50, "age_max": 59, "max": 3.1, "type": "max_inclusive", "priority": 1},
            {"condition": "60 a 69 anos", "age_min": 60, "age_max": 69, "max": 4.1, "type": "max_inclusive", "priority": 1},
            {"condition": "> ou = 70 anos", "age_min": 70, "max": 4.4, "type": "max_inclusive", "priority": 1},
            {"condition": "Geral", "max": 4.4, "type": "max_inclusive", "priority": 0} # Fallback
        ]
    }),
    ("RELAÇÃO PSA LIVRE/PSA TOTAL", {
        "unit": "%",
        "references": [
            {"condition": "Geral", "min": 25, "type": "min_inclusive", "priority": 0} # Example, considering common interpretation
        ]
    }),
    ("PARATORMÔNIO", {
        "unit": "pg/mL",
        "references": [
            {"condition": "Geral", "min": 15, "max": 65, "priority": 0}
        ]
    }),
    ("HOMOCISTEÍNA", {
        "unit": "µmol/L",
        "references": [
            {"condition": "Geral", "min": 5.0, "max": 12.0, "priority": 0}
        ]
    }),
    ("ZINCO SERICO", {
        "unit": "ug/dL",
        "references": [
            {"condition": "Normal", "min": 80, "max": 120, "priority": 1},
            {"condition": "Deficiência", "max": 30, "type": "max_inclusive", "priority": 1},
            {"condition": "Geral", "min": 80, "max": 120, "priority": 0} # Fallback
        ]
    }),
    ("CAXUMBA IgG", {
        "unit": "UA/mL",
        "references": [
            {"condition": "Não reagente", "max": 9.00, "type": "max_inclusive", "priority": 1},
            {"condition": "Indeterminado", "min": 9.00, "max": 11.00, "priority": 1},
            {"condition": "Reagente", "min": 11.00, "type": "min_inclusive", "priority": 1},
            {"condition": "Geral", "max": 9.00, "type": "max_inclusive", "priority": 0} # Fallback
        ]
    }),
    ("TESTOSTERONA TOTAL", {
        "unit": "ng/dL",
        "references": [
            {"condition": "Pré-púberes", "max": 40.00, "type": "max_inclusive", "priority": 1},
            {"condition": "Feminino: 11 a 49 anos", "gender": "F", "age_min": 11, "age_max": 49, "min": 8.40, "max": 48.00, "priority": 2},
            {"condition": "Feminino: Maior ou igual a 50 anos", "gender": "F", "age_min": 50, "min": 2.90, "max": 40.80, "priority": 2},
            {"condition": "Masculino: 11 a 49 anos", "gender": "M", "age_min": 11, "age_max": 49, "min": 249.00, "max": 836.00, "priority": 2},
            {"condition": "Masculino: Maior ou igual a 50 anos", "gender": "M", "age_min": 50, "min": 193.00, "max": 740.00, "priority": 2},
            {"condition": "Geral", "min": 0, "max": 1000, "priority": 0} # Fallback
        ]
    }),
    ("ANDROSTANEDIOL GLUCURONIDE [3 ALFA DIOL]", {
        "unit": "ng/mL",
        "references": [
            {"condition": "HOMENS", "gender": "M", "min": 1.53, "max": 14.82, "priority": 1},
            {"condition": "MULHERES: Pré-menopausa", "gender": "F", "min": 0.22, "max": 4.64, "priority": 1},
            {"condition": "MULHERES: Pós-menopausa", "gender": "F", "min": 0.61, "max": 3.71, "priority": 1},
            {"condition": "MULHERES: Puberdade", "gender": "F", "min": 0.51, "max": 4.03, "priority": 1},
            {"condition": "Geral", "min": 0.1, "max": 15, "priority": 0} # Fallback
        ]
    }),
    ("SÓDIO", {
        "unit": "mmol/L",
        "references": [
            {"condition": "Geral", "min": 136, "max": 145, "priority": 0}
        ]
    }),
    ("POTÁSSIO", {
        "unit": "mmol/L",
        "references": [
            {"condition": "Geral", "min": 3.5, "max": 5.5, "priority": 0}
        ]
    }),
    ("INSULINA BASAL", {
        "unit": "mU/mL",
        "references": [
            {"condition": "Insulina basal", "min": 2.60, "max": 24.90, "priority": 1},
            {"condition": "Geral", "min": 2.60, "max": 24.90, "priority": 0} # Fallback
        ]
    }),
    ("HOMA IR", { # No unit specified in text
        "unit": None,
        "references": [
            {"condition": "Geral", "max": 2.7, "type": "max_inclusive", "priority": 0}
        ]
    }),
    ("HOMA BETA", { # No unit specified in text
        "unit": None,
        "references": [
            {"condition": "Geral", "min": 0, "max": 300, "priority": 0} # Placeholder range, needs actual reference
        ]
    }),
    ("FERRO SÉRICO", {
        "unit": "mcg/dL",
        "references": [
            {"condition": "Adultos: Masculino", "gender": "M", "age_min": 18, "min": 59, "max": 158, "priority": 1},
            {"condition": "Adultos: Feminino", "gender": "F", "age_min": 18, "min": 37, "max": 145, "priority": 1},
            {"condition": "Geral", "min": 25, "max": 160, "priority": 0} # Fallback
        ]
    }),
    ("FERRITINA", {
        "unit": "nanog/mL",
        "references": [
            {"condition": "Homens", "gender": "M", "min": 30, "max": 400, "priority": 1},
            {"condition": "Mulheres", "gender": "F", "min": 13, "max": 150, "priority": 1},
            {"condition": "Geral", "min": 13, "max": 400, "priority": 0} # Fallback
        ]
    }),
    ("T4 LIVRE", {
        "unit": "ng/dL",
        "references": [
            {"condition": "Geral", "min": 0.93, "max": 1.70, "priority": 0},
            {"condition": "Gestante: 1º trimestre", "gender": "F", "min": 0.9, "max": 1.5, "priority": 1},
            {"condition": "Gestante: 2º trimestre", "gender": "F", "min": 0.7, "max": 1.3, "priority": 1},
            {"condition": "Gestante: 3º trimestre", "gender": "F", "min": 0.6, "max": 1.2, "priority": 1},
        ]
    }),
    ("ÁCIDO ÚRICO", {
        "unit": "mg/dL",
        "references": [
            {"condition": "Homem", "gender": "M", "min": 3.4, "max": 7.0, "priority": 1},
            {"condition": "Mulher", "gender": "F", "min": 2.4, "max": 5.7, "priority": 1},
            {"condition": "Geral", "min": 2.4, "max": 7.0, "priority": 0} # Fallback
        ]
    }),
    ("VITAMINA B12", {
        "unit": "pg/mL",
        "references": [
            {"condition": "Geral", "min": 197, "max": 771, "priority": 0}
        ]
    }),
    ("ÁCIDO FÓLICO", {
        "unit": "ng/mL",
        "references": [
            {"condition": "Normal", "min": 5.38, "type": "min_inclusive", "priority": 1},
            {"condition": "Indeterminado", "min": 3.38, "max": 5.38, "priority": 1},
            {"condition": "Deficiente", "min": 0.35, "max": 3.37, "priority": 1},
            {"condition": "Geral", "min": 5.38, "type": "min_inclusive", "priority": 0} # Fallback
        ]
    }),
    ("N-TELOPEPTÍDEO (CROSS-LINKS) - NTX", { # New
        "unit": "nmol ECO/mM creatinina",
        "references": [
            {"condition": "Mulheres", "gender": "F", "min": 5, "max": 65, "priority": 1},
            {"condition": "Homens", "gender": "M", "min": 3, "max": 63, "priority": 1},
            {"condition": "Geral", "min": 3, "max": 65, "priority": 0} # Fallback
        ]
    }),
    ("N-TELOPEPTÍDEO CONCENTRAÇÃO", { # New
        "unit": "nmol ECO/L",
        "references": [
            {"condition": "Geral", "min": 0, "max": 200, "priority": 0} # Placeholder range, needs actual reference
        ]
    }),

    # Leucograma Tests (assuming Adultos for now, as no specific children/gender ranges provided in text)
    ("LEUCOCITOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Adultos", "age_min": 18, "min": 3.6, "max": 11., "priority": 1},
            {"condition": "Crianças (Menores de 8 anos)", "age_max": 8, "min": 4.0, "max": 14.0, "priority": 1},
            {"condition": "Geral", "min": 3.5, "max": 10.5, "priority": 0} # Fallback from test_patterns original ref
        ]
    }),
    ("BASTONETES (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Adultos", "age_min": 18, "min": 0, "max": 550, "priority": 1},
            {"condition": "Crianças (Menores de 8 anos)", "age_max": 8, "min": 0, "max": 450, "priority": 1},
            {"condition": "Geral", "min": 0, "max": 840, "priority": 0} # Fallback from test_patterns original ref
        ]
    }),
    ("SEGMENTADOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Adultos", "age_min": 18, "min": 1.480, "max": 7.700, "priority": 1},
            {"condition": "Crianças (Menores de 8 anos)", "age_max": 8, "min": 1.200, "max": 9.600, "priority": 1},
            {"condition": "Geral", "min": 1.700, "max": 8.000, "priority": 0} # Fallback from test_patterns original ref
        ]
    }),
    ("EOSINOFILOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Adultos", "age_min": 18, "min": 0, "max": 550, "priority": 1},
            {"condition": "Crianças (Menores de 8 anos)", "age_max": 8, "min": 0, "max": 550, "priority": 1},
            {"condition": "Geral", "min": 50, "max": 500, "priority": 0} # Fallback from test_patterns original ref
        ]
    }),
    ("BASOFILOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Adultos", "age_min": 18, "min": 0, "max": 220, "priority": 1},
            {"condition": "Crianças (Menores de 8 anos)", "age_max": 8, "min": 0, "max": 300, "priority": 1},
            {"condition": "Geral", "min": 0, "max": 100, "priority": 0} # Fallback from test_patterns original ref
        ]
    }),
    ("LINFOCITOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Adultos", "age_min": 18, "min": 0.740, "max": 5.500, "priority": 1},
            {"condition": "Crianças (Menores de 8 anos)", "age_max": 8, "min": 1.520, "max": 10.500, "priority": 1},
            {"condition": "Geral", "min": 0.900, "max": 2.900, "priority": 0} # Fallback from test_patterns original ref
        ]
    }),
    ("MONOCITOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Adultos", "age_min": 18, "min": 37, "max": 1500, "priority": 1},
            {"condition": "Crianças (Menores de 8 anos)", "age_max": 8, "min": 40, "max": 1700, "priority": 1},
            {"condition": "Geral", "min": 300, "max": 900, "priority": 0} # Fallback from test_patterns original ref
        ]
    }),
    ("NEUTRÓFILOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Geral", "min": 1.700, "max": 8.000, "priority": 0}
        ]
    }),
    ("PROMIELÓCITOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Geral", "min": 0, "max": 0, "priority": 0} # Implicitly 0
        ]
    }),
    ("MIELÓCITOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Geral", "min": 0, "max": 0, "priority": 0} # Implicitly 0
        ]
    }),
    ("METAMIELÓCITOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Geral", "min": 0, "max": 0, "priority": 0} # Implicitly 0
        ]
    }),
    ("LINFÓCITOS TÍPICOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Geral", "min": 0.900, "max": 29.00, "priority": 0}
        ]
    }),
    ("LINFÓCITOS ATÍPICOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Geral", "min": 0, "max": 0, "priority": 0} # Implicitly 0
        ]
    }),
    ("BLASTOS (Leucograma)", {
        "unit": "/mm3",
        "references": [
            {"condition": "Geral", "min": 0, "max": 0, "priority": 0} # Implicitly 0
        ]
    }),
    ("PLAQUETAS", {
        "unit": "mil/mm3",
        "references": [
            {"condition": "Adultos", "age_min": 18, "min": 150, "max": 450, "priority": 1},
            {"condition": "Crianças", "age_max": 18, "min": 140, "max": 500, "priority": 1},
            {"condition": "Geral", "min": 150, "max": 450, "priority": 0} # Fallback
        ]
    }),
    ("VMP (Volume Plaquetário Médio)", {
        "unit": "fl",
        "references": [
            {"condition": "Geral", "min": 6.8, "max": 12.6, "priority": 0}
        ]
    }),

    # Coagulogram Tests (specific items)
    ("PROTROMBINA (PADRÃO)", { # New. Placeholder reference as this is a control value.
        "unit": "segundos",
        "references": [
            {"condition": "Geral", "min": 9.0, "max": 12.0, "priority": 0} # Example control range
        ]
    }),
    ("PROTROMBINA (PACIENTE)", {
        "unit": "segundos",
        "references": [
            {"condition": "Geral", "min": 9.0, "max": 13.0, "priority": 0} # Example range
        ]
    }),
    ("ATIVIDADE DE PROTROMBINA", {
        "unit": "%",
        "references": [
            {"condition": "Geral", "min": 70, "max": 110, "priority": 0}
        ]
    }),
    ("PROTROMBINA (RELAÇÃO PACIENTE/PADRÃO)", {
        "unit": None,
        "references": [
            {"condition": "Geral", "min": 0.85, "max": 1.20, "priority": 0}
        ]
    }),
    ("RELAÇÃO PADRÃO INTERNACIONAL (INR)", {
        "unit": None,
        "references": [
            {"condition": "Geral", "min": 0.89, "max": 1.28, "priority": 0}
        ]
    }),
    ("SENSIBILIDADE INTERNACIONAL (ISI)", { # New. Placeholder reference.
        "unit": None,
        "references": [
            {"condition": "Geral", "min": 0.8, "max": 1.3, "priority": 0} # ISI is a calculation factor, general range for validity
        ]
    }),
    ("PLASMA CONTROLE", { # New. Placeholder reference as this is a control value.
        "unit": "segundos",
        "references": [
            {"condition": "Geral", "min": 20.0, "max": 35.0, "priority": 0} # Example control range
        ]
    }),
    ("PLASMA PACIENTE", {
        "unit": "segundos",
        "references": [
            {"condition": "Geral", "min": 20.0, "max": 35.0, "priority": 0} # Example range
        ]
    }),
    ("RELAÇÃO PACIENTE/CONTROLE", {
        "unit": None,
        "references": [
            {"condition": "Geral", "min": 0.82, "max": 1.18, "priority": 0}
        ]
    }),

    # Blood Group (Qualitative)
    ("SISTEMA ABO", { # New
        "unit": None,
        "references": [
            {"condition": "Geral", "expected": ["A", "B", "AB", "O"], "type": "qualitative"}
        ]
    }),
    ("FATOR RH", { # New
        "unit": None,
        "references": [
            {"condition": "Geral", "expected": ["POSITIVO", "NEGATIVO"], "type": "qualitative"}
        ]
    }),

    # Gasometria Venosa
    ("pH (Gasometria)", {
        "unit": None, # Unit is "pH" itself or implied
        "references": [
            {"condition": "Geral", "min": 7.32, "max": 7.42, "priority": 0}
        ]
    }),
    ("PCO2", {
        "unit": "mmHg",
        "references": [
            {"condition": "Geral", "min": 41, "max": 51, "priority": 0}
        ]
    }),
    ("PO2", {
        "unit": "mmHg",
        "references": [
            {"condition": "Geral", "min": 30, "max": 40, "priority": 0}
        ]
    }),
    ("HCO3", {
        "unit": "mmol/L",
        "references": [
            {"condition": "Geral", "min": 22, "max": 26, "priority": 0}
        ]
    }),
    ("O2 SATURAÇÃO", {
        "unit": "%",
        "references": [
            {"condition": "Geral", "min": 60, "max": 75, "priority": 0}
        ]
    }),
    ("B.E", {
        "unit": "mmol/L",
        "references": [
            {"condition": "Geral", "min": -3.0, "max": 3.0, "priority": 0}
        ]
    }),

    # Urinalysis (EAS / Rotina de Urina) - Differentiated by "Urina" in name
    ("DENSIDADE (Urina)", {
        "unit": None, # Unit is "1.XXX"
        "references": [
            {"condition": "Geral", "min": 1.005, "max": 1.030, "priority": 0} # Using the broader range found
        ]
    }),
    ("PH (Urina)", {
        "unit": None,
        "references": [
            {"condition": "Geral", "min": 4.8, "max": 8.0, "priority": 0} # Using the broader range found
        ]
    }),
    ("PROTEÍNAS (Urina)", {
        "references": [
            {"condition": "Geral", "expected": ["Negativo", "Ausentes", "Negativo (<=10 mg/dL)"], "type": "qualitative"}
        ]
    }),
    ("GLICOSE (Urina)", {
        "references": [
            {"condition": "Geral", "expected": ["Negativo", "Negativo (<=20 mg/dL)"], "type": "qualitative"}
        ]
    }),
    ("CORPOS CETÔNICOS (Urina)", {
        "references": [
            {"condition": "Geral", "expected": ["Negativo"], "type": "qualitative"}
        ]
    }),
    ("BILIRRUBINAS (Urina)", {
        "references": [
            {"condition": "Geral", "expected": ["Negativo"], "type": "qualitative"}
        ]
    }),
    ("HEMOGLOBINA (Urina)", { # Note: Added "Positivo +" as seen in one sample, but still "off-range" for "Negativo"
        "references": [
            {"condition": "Geral", "expected": ["Negativo", "Negativo (+)"], "type": "qualitative"} # "Negativo (+)" is just the text as it appears
        ]
    }),
    ("NITRITOS (Urina)", {
        "references": [
            {"condition": "Geral", "expected": ["Negativo"], "type": "qualitative"}
        ]
    }),
    ("UROBILINOGÊNIO (Urina)", {
        "references": [
            {"condition": "Geral", "expected": ["Negativo", "Normal", "Normal (<=1,0 mg/dL)"], "type": "qualitative"}
        ]
    }),
    ("LEUCÓCITOS (Urina)", {
        "unit": "/mL",
        "references": [
            {"condition": "Geral", "max": 20.000, "type": "max_inclusive", "priority": 0}
        ]
    }),
    ("HEMÁCIAS (Urina)", {
        "unit": "/mL",
        "references": [
            {"condition": "Geral", "max": 10.000, "type": "max_inclusive", "priority": 0}
        ]
    }),
    ("CILINDROS (Urina)", {
        "references": [
            {"condition": "Geral", "expected": ["Ausentes"], "type": "qualitative"}
        ]
    }),
    ("BACTÉRIAS (Urina)", {
        "references": [
            {"condition": "Geral", "expected": ["Não Vizualizada", "Escassa"], "type": "qualitative"} # "Presente (+)" means off-range
        ]
    }),
    ("CÉLULAS EPITELIAIS (Urina)", {
        "references": [
            {"condition": "Geral", "expected": ["Ausente"], "type": "qualitative"} # "Presente (+)" or "Raras" means off-range
        ]
    }),
    ("CRISTAIS (Urina)", {
        "references": [
            {"condition": "Geral", "expected": ["Ausentes"], "type": "qualitative"}
        ]
    }),

    # Eletroforese de Proteínas (assuming Adultos for now, as no specific children/gender ranges provided in text)
    ("ALBUMINA (g/dL)", {
        "unit": "g/dL",
        "references": [
            {"condition": "Geral", "min": 3.52, "max": 4.81, "priority": 0}
        ]
    }),
    ("ALBUMINA (%)", {
        "unit": "%",
        "references": [
            {"condition": "Geral", "min": 55.80, "max": 66.10, "priority": 0}
        ]
    }),
    ("ALFA 1 (g/dL)", {
        "unit": "g/dL",
        "references": [
            {"condition": "Geral", "min": 0.18, "max": 0.32, "priority": 0}
        ]
    }),
    ("ALFA 1 (%)", {
        "unit": "%",
        "references": [
            {"condition": "Geral", "min": 2.60, "max": 4.70, "priority": 0}
        ]
    }),
    ("ALFA 2 (g/dL)", {
        "unit": "g/dL",
        "references": [
            {"condition": "Geral", "min": 0.46, "max": 0.80, "priority": 0}
        ]
    }),
    ("ALFA 2 (%)", {
        "unit": "%",
        "references": [
            {"condition": "Geral", "min": 6.60, "max": 11.60, "priority": 0}
        ]
    }),
    ("BETA 1 (g/dL)", {
        "unit": "g/dL",
        "references": [
            {"condition": "Geral", "min": 0.30, "max": 0.52, "priority": 0}
        ]
    }),
    ("BETA 1 (%)", {
        "unit": "%",
        "references": [
            {"condition": "Geral", "min": 4.20, "max": 7.40, "priority": 0}
        ]
    }),
    ("BETA 2 (g/dL)", {
        "unit": "g/dL",
        "references": [
            {"condition": "Geral", "min": 0.23, "max": 0.46, "priority": 0}
        ]
    }),
    ("BETA 2 (%)", {
        "unit": "%",
        "references": [
            {"condition": "Geral", "min": 3.60, "max": 6.70, "priority": 0}
        ]
    }),
    ("GAMA (g/dL)", {
        "unit": "g/dL",
        "references": [
            {"condition": "Geral", "min": 0.63, "max": 1.51, "priority": 0}
        ]
    }),
    ("GAMA (%)", {
        "unit": "%",
        "references": [
            {"condition": "Geral", "min": 10.10, "max": 20.40, "priority": 0}
        ]
    }),
    ("RELAÇÃO A/G", {
        "unit": None,
        "references": [
            {"condition": "Geral", "min": 1.10, "max": 2.00, "priority": 0}
        ]
    }),
    ("PROTEÍNAS TOTAIS", {
        "unit": "g/dL",
        "references": [
            {"condition": "Geral", "min": 5.7, "max": 8.2, "priority": 0}
        ]
    }),
]