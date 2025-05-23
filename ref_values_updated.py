REF_VALUES = [
    ('1,25-DIHIDROXIVITAMINA D', {'ref_max': 79.3, 'ref_min': 19.9, 'unit': 'pg/mL'}),
    ('10 DIAS', {'ref_max': 11.0, 'ref_min': 9.0, 'unit': 'mg/dL'}),
    ('ADULTO', {'ref_max': 2.0, 'ref_min': 0.5, 'unit': '%'}),
    ('ADULTOS', {'ref_max': 80.0, 'ref_min': 30.0, 'unit': 'mcg/dL'}),
    ('ALBUMINA', {'ref_max': 5.4, 'ref_min': 3.4, 'unit': 'g/dL'}),
    ('ALFA 1', {'ref_max': 0.4, 'ref_min': 0.1, 'unit': 'g/dL'}),
    ('ALFA 2', {'ref_max': 1.0, 'ref_min': 0.4, 'unit': 'g/dL'}),
    ('ALUMÍNIO', {'ref_max': 10.0, 'ref_min': 0.0, 'unit': 'mcg/L'}),
    ('ANTICORPOS ANTI CITOMEGALOVÍRUS - IGG', {'expected': ['Reagente', 'Não Reagente']}),
    ('ANTICORPOS ANTI-HBS', {'expected': ['Reagente', 'Não Reagente', 'Indeterminado']}),
    ('ANTICORPOS ANTI-HCV', {'expected': ['Reagente', 'Não Reagente', 'Indeterminado']}),
    ('ANTICORPOS ANTI-TRANSGLUTAMINASE TECIDUAL - IGA', {'ref_max': 20.0, 'ref_min': 0.0, 'unit': 'U/mL'}),
    ('ANTICORPOS ANTI-TREPONEMA PALLIDUM', {'expected': ['Reagente', 'Não Reagente', 'Indeterminado']}),
    ('ANTICORPOS IGG ANTI BORRELIA BURGDORFERI', {'expected': ['Reagente', 'Não Reagente', 'Indeterminado']}),
    ('ANTICORPOS TOTAIS ANTI-HBV CORE (HBC)', {'expected': ['Reagente', 'Não Reagente', 'Indeterminado']}),
    ('ANTÍGENO DE SUPERFÍCIE DO HBV (HBSAG)', {'expected': ['Reagente', 'Não Reagente', 'Indeterminado']}),
    ('APTT / TTPA', {'ref_max': 37.0, 'ref_min': 25.0, 'unit': 'seg'}),
    ('ARSÊNICO', {'ref_max': 10.0, 'ref_min': 0.0, 'unit': 'mcg/L'}),
    ('ATIVIDADE DE PROTROMBINA', {'ref_max': 100.0, 'ref_min': 70.0, 'unit': '%'}),
    ('B.E. (GASOMETRIA VENOSA)', {'ref_max': 2.0, 'ref_min': -2.0, 'unit': 'mmol/L'}),
    ('BACTÉRIAS (URINA)', {'expected': 'Ausente'}),
    ('BASOFILOS', {'ref_max': 220.0, 'ref_min': 0.0, 'unit': ''}),
    ('BASTONETES', {'ref_max': 840.0, 'ref_min': 0.0, 'unit': ''}),
    ('BASÓFILOS', {'ref_max': 100.0, 'ref_min': 0.0, 'unit': ''}),
    ('BETA 1', {'ref_max': 0.9, 'ref_min': 0.5, 'unit': 'g/dL'}),
    ('BETA 2', {'ref_max': 0.5, 'ref_min': 0.2, 'unit': 'g/dL'}),
    ('BILIRRUBINA DIRETA', {'ref_max': 0.3, 'ref_min': 0.0, 'unit': 'mg/dL'}),
    ('BILIRRUBINA INDIRETA', {'ref_max': 1.0, 'ref_min': 0.2, 'unit': 'mg/dL'}),
    ('BILIRRUBINA TOTAL', {'ref_max': 1.2, 'ref_min': 0.2, 'unit': 'mg/dL'}),
    ('BILIRRUBINAS ROTINA DE URINA', {'expected': 'Negativo'}),
    ('BLASTOS', {'expected': '0'}),
    ('CARIÓTIPO EM SANGUE PERIFÉRICO', {'expected': ['46,XX', '46,XY']}),
    ('CAXUMBA IGG', {'expected': ['Reagente', 'Não Reagente']}),
    ('CEA/ANTIGENO CARCINOEMBRIOGENICO', {'ref_max': 5.0, 'ref_min': 0.0, 'unit': 'ng/mL'}),
    ('CHCM', {'ref_max': 36.0, 'ref_min': 31.0, 'unit': 'g/dL'}),
    ('CILINDROS (URINA)', {'expected': 'Ausentes'}),
    ('CITOMEGALOVÍRUS IGM', {'expected': ['Reagente', 'Não Reagente', 'Indeterminado']}),
    ('COBALTO', {'ref_max': 1.0, 'ref_min': 0.0, 'unit': 'µg/L'}),
    ('COLESTEROL HDL', {'ref_max': 60.0, 'ref_min': 40.0, 'unit': 'mg/dL'}),
    ('COLESTEROL LDL', {'ref_max': 130.0, 'ref_min': 0.0, 'unit': 'mg/dL'}),
    ('COLESTEROL NÃO HDL', {'ref_max': 160.0, 'ref_min': 0.0, 'unit': 'mg/dL'}),
    ('COLESTEROL TOTAL', {'ref_max': 200.0, 'ref_min': 0.0, 'unit': 'mg/dL'}),
    ('CONTRACEPTIVOS ORAIS', {'ref_max': 231.4, 'ref_min': 48.1, 'unit': 'pg/mL'}),
    ('CORPOS CETÔNICOS ROTINA DE URINA', {'expected': 'Negativo'}),
    ('CPK - CREATINA FOSFOQUINASE', {'ref_max': 190.0, 'ref_min': 10.0, 'unit': 'U/L'}),
    ('CREATININA', {'ref_max': 1.3, 'ref_min': 0.7, 'unit': 'mg/dL'}),
    ('CRISTAIS (URINA)', {'expected': 'Ausentes'}),
    ('CROMO', {'ref_max': 5.0, 'ref_min': 0.0, 'unit': 'µg/L'}),
    ('CULTURA DE URINA', {'expected': ['Sem crescimento', 'Negativo']}),
    ('CÁDMIO', {'ref_max': 0.5, 'ref_min': 0.0, 'unit': 'mcg/L'}),
    ('CÁLCIO', {'ref_max': 10.5, 'ref_min': 8.5, 'unit': 'mg/dL'}),
    ('CÉLULAS EPITELIAIS (URINA)', {'expected': ['Ausente', 'Raras']}),
    ('DE', {'ref_max': 7.5, 'ref_min': 0.6, 'unit': 'mcg/L'}),
    ('DENSIDADE', {'ref_max': 1.03, 'ref_min': 1.0, 'unit': ''}),
    ('DHT - DIHIDROTESTOSTERONA', {'ref_max': 790.0, 'ref_min': 160.0, 'unit': 'pg/mL'}),
    ('EOSINOFILOS', {'ref_max': 500.0, 'ref_min': 50.0, 'unit': ''}),
    ('EOSINÓFILOS', {'ref_max': 500.0, 'ref_min': 50.0, 'unit': ''}),
    ('ESTRADIOL', {'ref_max': 350.0, 'ref_min': 15.0, 'unit': 'pg/mL'}),
    ('FASE FOLICULAR', {'ref_max': 166.0, 'ref_min': 12.5, 'unit': 'pg/mL'}),
    ('FASE LUTEA', {'ref_max': 11.4, 'ref_min': 1.0, 'unit': 'mUI/mL'}),
    ('FASE LÚTEA', {'ref_max': 179.3, 'ref_min': 54.1, 'unit': 'pg/mL'}),
    ('FATOR RH', {'expected': ['POSITIVO', 'NEGATIVO']}),
    ('FERRITINA', {'ref_max': 150.0, 'ref_min': 15.0, 'unit': 'ng/mL'}),
    ('FERRO SÉRICO', {'ref_max': 158.0, 'ref_min': 59.0, 'unit': 'mcg/dL'}),
    ('FOSFATASE ALCALINA', {'ref_max': 147.0, 'ref_min': 44.0, 'unit': 'U/L'}),
    ('FSH', {'ref_max': 12.4, 'ref_min': 1.5, 'unit': 'mUI/mL'}),
    ('FÓSFORO', {'ref_max': 4.5, 'ref_min': 2.5, 'unit': 'mg/dL'}),
    ('GAMA', {'ref_max': 1.5, 'ref_min': 0.6, 'unit': 'g/dL'}),
    ('GAMA GLUTAMIL TRANSFERASE', {'ref_max': 61.0, 'ref_min': 8.0, 'unit': 'U/L'}),
    ('GLICEMIA MÉDIA ESTIMADA', {'ref_max': 117.0, 'ref_min': 70.0, 'unit': 'mg/dL'}),
    ('GLICOSE', {'ref_max': 99.0, 'ref_min': 70.0, 'unit': 'mg/dL'}),
    ('GLICOSE ROTINA DE URINA', {'expected': 'Negativo'}),
    ('HCG - GONADOTROFINA CORIONICA', {'ref_max': 5.0, 'ref_min': 0.0, 'unit': 'mUI/mL'}),
    ('HCM', {'ref_max': 34.0, 'ref_min': 26.0, 'unit': 'pg'}),
    ('HCO3 (GASOMETRIA VENOSA)', {'ref_max': 29.0, 'ref_min': 22.0, 'unit': 'mmol/L'}),
    ('HEMACIAS', {'ref_max': 5.7, 'ref_min': 4.3, 'unit': ''}),
    ('HEMATOCRITO', {'ref_max': 54.0, 'ref_min': 36.0, 'unit': ''}),
    ('HEMATÓCRITO', {'ref_max': 46.0, 'ref_min': 34.9, 'unit': '%'}),
    ('HEMOGLOBINA', {'ref_max': 17.5, 'ref_min': 13.0, 'unit': 'g/dL'}),
    ('HEMOGLOBINA GLICADA - HBA1C', {'ref_max': 5.6, 'ref_min': 4.0, 'unit': '%'}),
    ('HEMOGLOBINA ROTINA DE URINA', {'expected': 'Negativo'}),
    ('HEMÁCIAS', {'ref_max': 5.7, 'ref_min': 4.3, 'unit': 'milhões/mm3'}),
    ('HEMÁCIAS (URINA)', {'ref_max': 5000, 'ref_min': 0.0, 'unit': 'células/µL'}),
    ('HOMA BETA', {'ref_max': 167.0, 'ref_min': 167.0, 'unit': ''}),
    ('HOMA IR', {'ref_max': 2.0, 'ref_min': 0.0, 'unit': ''}),
    ('HOMENS', {'ref_max': 400.0, 'ref_min': 30.0, 'unit': 'nanog/mL'}),
    ('IGE MÚLTIPLO PARA ALIMENTOS', {'expected': 'Não reagente'}),
    ('IGE MÚLTIPLO PARA EPITÉLIOS E PROTEÍNAS ANIMAIS', {'expected': 'Não reagente'}),
    ('IGE MÚLTIPLO PARA PÓ DE CASA', {'expected': 'Não reagente'}),
    ('IMUNOGLOBULINAS IGA', {'ref_max': 400.0, 'ref_min': 70.0, 'unit': 'mg/dL'}),
    ('IMUNOGLOBULINAS IGE TOTAL', {'ref_max': 100.0, 'ref_min': 0.0, 'unit': 'UI/mL'}),
    ('LEUCOCITOS', {'ref_max': 10500, 'ref_min': 3500, 'unit': ''}),
    ('LEUCÓCITOS', {'ref_max': 10500, 'ref_min': 3500, 'unit': ''}),
    ('AMILASE', {'ref_max': 100, 'ref_min': 28, 'unit': 'U/L'}),
    ('LEUCÓCITOS (URINA)', {'ref_max': 20000, 'ref_min': 0.0, 'unit': 'células/µL'}),
    ('LH', {'ref_max': 8.6, 'ref_min': 1.7, 'unit': 'mUI/mL'}),
    ('LINFOCITOS', {'ref_max': 5.5, 'ref_min': 740.0, 'unit': ''}),
    ('LINFÓCITOS', {'ref_max': 2900, 'ref_min': 900, 'unit': '10³/mm³'}),
    ('LINFÓCITOS ATÍPICOS', {'expected': '0%'}),
    ('LINFÓCITOS TÍPICOS', {'ref_max': 2900, 'ref_min': 900, 'unit': ''}),
    ('MAGNÉSIO', {'ref_max': 2.2, 'ref_min': 1.7, 'unit': 'mg/dL'}),
    ('MANGANÊS', {'ref_max': 1.0, 'ref_min': 0.2, 'unit': 'µg/L'}),
    ('MERCÚRIO', {'ref_max': 10.0, 'ref_min': 0.0, 'unit': 'mcg/dL'}),
    ('METAMIELÓCITOS', {'expected': '0'}),
    ('MICROALBUMINÚRIA', {'ref_max': 29.9, 'ref_min': 0.0, 'unit': 'mg/g creatinina'}),
    ('MIELÓCITOS', {'expected': '0'}),
    ('MONOCITOS', {'ref_max': 1.5, 'ref_min': 37.0, 'unit': ''}),
    ('MONÓCITOS', {'ref_max': 900.0, 'ref_min': 300.0, 'unit': ''}),
    ('N-TELOPEPTÍDEO NTX CONCENTRAÇÃO', {'ref_max': 25.0, 'ref_min': 6.0, 'unit': 'nmol BCE/L'}),
    ('N-TELOPEPTÍDEO NTX RESULTADO', {'ref_max': 60.0, 'ref_min': 10.0, 'unit': 'nmol BCE/mM creatinina'}),
    ('NEUTRÓFILOS', {'ref_max': 8000, 'ref_min': 1700, 'unit': ''}),
    ('NITRITOS ROTINA DE URINA', {'expected': 'Negativo'}),
    ('NORMAL', {'ref_max': 99.0, 'ref_min': 70.0, 'unit': 'mg/dL'}),
    ('NÍQUEL', {'ref_max': 5.0, 'ref_min': 0.0, 'unit': 'mcg/L'}),
    ('O2 SATURAÇÃO (GASOMETRIA VENOSA)', {'ref_max': 85.0, 'ref_min': 60.0, 'unit': '%'}),
    ('OUTROS ELEMENTOS (URINA)', {'expected': 'Nenhum significativo'}),
    ('PARATORMÔNIO', {'ref_max': 65.0, 'ref_min': 15.0, 'unit': 'pg/mL'}),
    ('PCO2 (GASOMETRIA VENOSA)', {'ref_max': 50.0, 'ref_min': 38.0, 'unit': 'mmHg'}),
    ('PH', {'ref_max': 8.0, 'ref_min': 5.0, 'unit': ''}),
    ('PH (GASOMETRIA VENOSA)', {'ref_max': 7.43, 'ref_min': 7.32, 'unit': ''}),
    ('PH ROTINA DE URINA', {'ref_max': 8.0, 'ref_min': 5.0, 'unit': ''}),
    ('PLAQUETAS', {'ref_max': 450.0, 'ref_min': 150.0, 'unit': 'mil/mm3'}),
    ('PO2 (GASOMETRIA VENOSA)', {'ref_max': 50.0, 'ref_min': 30.0, 'unit': 'mmHg'}),
    ('POS MENOPAUSA', {'ref_max': 58.5, 'ref_min': 7.7, 'unit': 'mUI/mL'}),
    ('POTÁSSIO', {'ref_max': 5.1, 'ref_min': 3.5, 'unit': 'mmol/L'}),
    ('PPD (PURIFIED PROTEIN DERIVATIVE)', {'ref_max': 4.0, 'ref_min': 0.0, 'unit': 'mm'}),
    ('PRIMEIRO TRIMESTRE DE GRAVIDEZ: DE', {'ref_max': 2774.0, 'ref_min': 246.0, 'unit': 'pg/mL'}),
    ('PROMIELÓCITOS', {'expected': '0'}),
    ('PROTEÍNA ROTINA DE URINA', {'expected': 'Negativo'}),
    ('PROTEÍNAS TOTAIS', {'ref_max': 8.3, 'ref_min': 6.0, 'unit': 'g/dL'}),
    ('PROTEÍNAS TOTAIS.....: 6,3', {'ref_max': 8.2, 'ref_min': 5.7, 'unit': 'g/dL'}),
    ('PROTEÍNAS TOTAIS.....: 6,4', {'ref_max': 8.2, 'ref_min': 5.7, 'unit': 'g/dL'}),
    ('PROTEÍNAS TOTAIS.....: 6,5', {'ref_max': 8.2, 'ref_min': 5.7, 'unit': 'g/dL'}),
    ('PROTEÍNAS TOTAIS.....: 6,7', {'ref_max': 8.2, 'ref_min': 5.7, 'unit': 'g/dL'}),
    ('PROTEÍNAS TOTAIS.....: 6,8', {'ref_max': 8.2, 'ref_min': 5.7, 'unit': 'g/dL'}),
    ('PROTEÍNAS TOTAIS.....: 6,9', {'ref_max': 8.2, 'ref_min': 5.7, 'unit': 'g/dL'}),
    ('PROTEÍNAS TOTAIS.....: 7,1', {'ref_max': 8.2, 'ref_min': 5.7, 'unit': 'g/dL'}),
    ('PROTEÍNAS TOTAIS.....: 7,4', {'ref_max': 8.2, 'ref_min': 5.7, 'unit': 'g/dL'}),
    ('PROTROMBINA (PACIENTE)', {'ref_max': 13.0, 'ref_min': 10.0, 'unit': 'seg'}),
    ('PROTROMBINA (RELAÇÃO PACIENTE/PADRÃO)', {'ref_max': 1.2, 'ref_min': 0.8, 'unit': ''}),
    ('PRÉ OVULAÇÃO', {'ref_max': 246.8, 'ref_min': 70.3, 'unit': 'pg/mL'}),
    ('PSA LIVRE', {'ref_max': 0.9, 'ref_min': 0.0, 'unit': 'ng/mL'}),
    ('PSA TOTAL', {'ref_max': 4.0, 'ref_min': 0.0, 'unit': 'ng/mL'}),
    ('PSA TOTAL ESTIVER ENTRE', {'ref_max': 10.0, 'ref_min': 4.0, 'unit': 'ng/mL.'}),
    ('PÓS-MENOPAUSA COM TES', {'ref_max': 455.0, 'ref_min': 51.3, 'unit': 'pg/mL'}),
    ('PÓS-MENOPAUSA SEM TES', {'ref_max': 96.6, 'ref_min': 35.6, 'unit': 'pg/mL'}),
    ('RDW', {'ref_max': 16.0, 'ref_min': 11.0, 'unit': ''}),
    ('RECÉM NASCIDO (DE TERMO)', {'ref_max': 0.85, 'ref_min': 0.24, 'unit': 'mg/dL'}),
    ('REDUÇÃO DISCRETA', {'ref_max': 60.0, 'ref_min': 89.0, 'unit': 'mL/min/1,73m2'}),
    ('REDUÇÃO MODERADA - SEVERA', {'ref_max': 30.0, 'ref_min': 44.0, 'unit': 'mL/min/1,73m2'}),
    ('REDUÇÃO SEVERA', {'ref_max': 15.0, 'ref_min': 29.0, 'unit': 'mL/min/1,73m2'}),
    ('RELAÇÃO A/G', {'ref_max': 2.5, 'ref_min': 1.0, 'unit': ''}),
    ('RELAÇÃO PACIENTE/CONTROLE', {'ref_max': 1.2, 'ref_min': 0.8, 'unit': ''}),
    ('RELAÇÃO PSA LIVRE/PSA TOTAL', {'ref_max': 1.0, 'ref_min': 0.15, 'unit': ''}),
    ('SEGMENTADOS', {'ref_max': 8000, 'ref_min': 1700, 'unit': ''}),
    ('SEGUNDO TRIMESTRE DE GRAVIDEZ : DE', {'ref_max': 5781.0, 'ref_min': 569.0, 'unit': 'pg/mL'}),
    ('SISTEMA ABO', {'expected': ['A', 'B', 'AB', 'O']}),
    ('SOROTIPO 14', {'expected': 'Inferior a 0,35 µg/mL'}),
    ('SOROTIPO 18C', {'expected': 'Inferior a 0,35 µg/mL'}),
    ('SOROTIPO 19F', {'expected': 'Inferior a 0,35 µg/mL'}),
    ('SOROTIPO 23F', {'expected': 'Inferior a 0,35 µg/mL'}),
    ('SOROTIPO 4', {'expected': 'Inferior a 0,35 µg/mL'}),
    ('SOROTIPO 6B', {'expected': 'Inferior a 0,35 µg/mL'}),
    ('SOROTIPO 9V', {'expected': 'Inferior a 0,35 µg/mL'}),
    ('SUPERIOR A 90 ANOS', {'ref_max': 9.6, 'ref_min': 8.2, 'unit': 'mg/dl'}),
    ('SÍFILIS - FTA-ABS IGG', {'expected': ['Reagente', 'Não Reagente', 'Indeterminado']}),
    ('SÓDIO', {'ref_max': 145.0, 'ref_min': 135.0, 'unit': 'mmol/L'}),
    ('T4 LIVRE', {'ref_max': 1.8, 'ref_min': 0.8, 'unit': 'ng/dL'}),
    ('TESTOSTERONA LIVRE', {'ref_max': 30.0, 'ref_min': 5.0, 'unit': 'pg/mL'}),
    ('TESTOSTERONA TOTAL', {'ref_max': 800.0, 'ref_min': 280.0, 'unit': 'ng/dL'}),
    ('TRANSAMINASE OXALACÉTICA TGO', {'ref_max': 34.0, 'ref_min': 5.0, 'unit': 'U/L'}),
    ('TRANSAMINASE PIRÚVICA TGP', {'ref_max': 40.0, 'ref_min': 5.0, 'unit': 'U/L'}),
    ('TRIGLICERÍDEOS', {'ref_max': 150.0, 'ref_min': 0.0, 'unit': 'mg/dL'}),
    ('TSH', {'ref_max': 4.2, 'ref_min': 0.27, 'unit': 'µUI/mL'}),
    ('UREIA', {'ref_max': 50.0, 'ref_min': 15.0, 'unit': 'mg/dL'}),
    ('UROBILINOGÊNIO ROTINA DE URINA', {'expected': 'Normal'}),
    ('VCM', {'ref_max': 98.3, 'ref_min': 81.6, 'unit': 'fl'}),
    ('VHS 1ª HORA', {'ref_max': 20.0, 'ref_min': 0.0, 'unit': 'mm/1h'}),
    ('VITAMINA B12', {'ref_max': 900.0, 'ref_min': 200.0, 'unit': 'pg/mL'}),
    ('VITAMINA D3 25-HIDROXI', {'ref_max': 60.0, 'ref_min': 30.0, 'unit': 'ng/mL'}),
    ('VMP', {'ref_max': 12.6, 'ref_min': 6.8, 'unit': ''}),
    ('VPM (VOLUME PLAQUETÁRIO MÉDIO)', {'ref_max': 12.6, 'ref_min': 9.2, 'unit': 'fl'}),
    ('ZINCO SÉRICO', {'ref_max': 120.0, 'ref_min': 60.0, 'unit': 'µg/dL'}),
    ('ÁCIDO FÓLICO', {'ref_max': 17.0, 'ref_min': 3.0, 'unit': 'ng/mL'}),
    ('ÁCIDO ÚRICO', {'ref_max': 7.0, 'ref_min': 3.4, 'unit': 'mg/dL'}),
]
