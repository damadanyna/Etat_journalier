import pandas as pd
import re
from db.db import DB
from sqlalchemy import text
from controller.DbGet import DbGet
import pymysql
dbGet = DbGet()

class OperationEsri:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
        
        self.teller = [
            '151', '152', '171', '172', 'SIGNATORY', 'USREGS.TP.LEGAL.ID', 'EM.DRAW.CHQ.NO', 'EM.DRAW.CHQ.AMT',
            'EM.DRAW.ACCT.NO', 'EM.DRAW.BANK', 'EM.DRAW.BRANCH', 'EM.DRAW.BRCH.CODE', 'EM.DRAW.CUST.NAME',
            'EM.CLEARED.BAL', 'EM.MEMBER.NAME', 'EM.ACCT.WORK.BAL', 'EM.PAY.TO', 'EM.AMT.ARREARS', 'EM.ACCT.NUM',
            'EM.SAVGS.AMOUNT', 'EM.REPAYMENT', 'EM.INT.REPAYMENT', 'EM.INTEREST.DUE', 'EM.CONS.DISCLOSE',
            'EM.SAVING.TMP.BAL', 'EM.LOAN.TMP.BAL', 'EM.INT.TMP.BAL', 'EM.ACCT.TYPE', 'L.REFERENCE', 'L.ORD.CUST',
            'L.ORD.CUST.CTRY', 'L.ORD.CUST.RES', 'L.BEN.NAME', 'L.BEN.ADD', 'L.BEN.RES', 'L.PAY.DETAILS', 'L.INI.CTRY',
            'L.ECO.CODE', 'L.CCY.REC', 'L.MODE.TXN', 'L.MAT.AGEN', 'L.NOM.PRES', 'L.NIF.PRES', 'L.NUM.STATS', 'L.TYP.IDEN',
            'L.NUM.IDEN', 'L.NUM.BEN', 'L.NOM.TIER', 'L.ORD.ADD', 'L.NAME.REC', 'L.ADDR', 'L.CIN', 'L.VERSION.NAME'
        ]

        self.columns_mapping = {
            'Type': 'EM.ACCT.TYPE',
            'Référence': 'L.REFERENCE',
            'Donneur d\'ordre': 'L.ORD.CUST',
            'Adresse donneur d\'ordre': 'L.ORD.ADD',
            'Code pays donneur d\'ordre': 'L.ORD.CUST.CTRY',
            'Bénéficiaire': 'L.BEN.NAME',
            'Bénéficiaire résident': 'L.BEN.RES',
            'Adresse Bénéficiaire': 'L.BEN.ADD',
            'Nature': 'L.PAY.DETAILS',
            'Code économique': 'L.ECO.CODE',
            'Sens': 'L.MODE.TXN',
        }

        self.country_addresses = {
           'AD': 'Andorre', 'AE': 'Émirats Arabes Unis', 'AF': 'Afghanistan', 'AG': 'Antigua et Barbuda', 'AI': 'Anguilla',
            'AL': 'Albanie', 'AM': 'Arménie', 'AN': 'Antilles néerlandaises', 'AO': 'Angola', 'AQ': 'Antarctique',
            'AR': 'Argentine', 'AS': 'Îles Samoa', 'AT': 'Autriche', 'AU': 'Australie', 'AW': 'Aruba', 'AZ': 'Azerbaïdjan',
            'BA': 'Bosnie-Herzégovine', 'BB': 'La Barbade', 'BD': 'Bangladesh', 'BE': 'Belgique', 'BF': 'Burkina Faso',
            'BG': 'Bulgarie', 'BH': 'Bahreïn', 'BI': 'Burundi', 'BJ': 'Benin', 'BM': 'Bermudas', 'BN': 'Brunéï', 'BO': 'Bolivie',
            'BR': 'Brésil', 'BS': 'Bahamas', 'BT': 'Bhoutan', 'BV': 'Îles Bouvet', 'BW': 'Botswana', 'BY': 'Biélorussie',
            'BZ': 'Bélize', 'CA': 'Canada', 'CC': 'Îles Coco', 'CF': 'République centrafricaine', 'CG': 'Congo', 'CH': 'Suisse',
            'CI': 'Côte d\'Ivoire', 'CK': 'Îles Cook', 'CL': 'Chili', 'CM': 'Cameroun', 'CN': 'Chine', 'CO': 'Colombie', 'CR': 'Costa Rica',
            'CS': 'Tchécoslovaquie (obsolète)', 'CU': 'Cuba', 'CV': 'Cap Vert', 'CX': 'Christmas Island', 'CY': 'Chypre', 'CZ': 'Tchèque (République)',
            'DE': 'Allemagne', 'DJ': 'Djibouti', 'DK': 'Danemark', 'DM': 'Dominique', 'DO': 'République Dominicaine', 'DZ': 'Algérie',
            'EC': 'Équateur', 'EE': 'Estonie', 'EG': 'Égypte', 'EH': 'Sahara Occidental', 'ER': 'Érythrée', 'ES': 'Espagne', 'ET': 'Éthiopie',
            'FI': 'Finlande', 'FJ': 'Îles Fidji', 'FK': 'Îles Falkland', 'FM': 'Micronésie', 'FO': 'Îles Féroé', 'FR': 'France', 'FX': 'France (métropolitaine)',
            'GA': 'Gabon', 'GB': 'Royaume-Uni (UK)', 'GD': 'Grenade', 'GE': 'Géorgie', 'GF': 'Guyane Française', 'GH': 'Ghana', 'GI': 'Gibraltar',
            'GL': 'Groenland', 'GM': 'Gambie', 'GN': 'Guinée', 'GP': 'Guadeloupe', 'GQ': 'Guinée équatoriale', 'GR': 'Grèce',
            'GS': 'Géorgie du Sud et îles Sandwich du Sud', 'GT': 'Guatemala', 'GU': 'Guam', 'GW': 'Guinée-Bissau', 'GY': 'Guyane', 'HK': 'Hong Kong',
            'HM': 'Îles Heard et MacDonald', 'HN': 'Honduras', 'HR': 'Croatie', 'HT': 'Haïti', 'HU': 'Hongrie', 'ID': 'Indonésie', 'IE': 'Irlande',
            'IL': 'Israël', 'IN': 'Inde', 'IO': 'Océan Indien Anglais', 'IQ': 'Irak', 'IR': 'République islamique d\'Iran', 'IS': 'Islande',
            'IT': 'Italie', 'JM': 'Jamaïque', 'JO': 'Jordanie', 'JP': 'Japon', 'KE': 'Kenya', 'KG': 'Kirghizistan', 'KH': 'Cambodge', 'KI': 'Kiribati',
            'KM': 'Comores', 'KN': 'Saint-Kitts-et-Nevis', 'KP': 'Corée du Nord', 'KR': 'Corée du Sud', 'KW': 'Koweït', 'KY': 'Îles Caïmans',
            'KZ': 'Kazakhstan', 'LA': 'Laos', 'LB': 'Liban', 'LC': 'Sainte-Lucie', 'LI': 'Liechtenstein', 'LK': 'Sri Lanka', 'LR': 'Libéria',
            'LS': 'Lesotho', 'LT': 'Lituanie', 'LU': 'Luxembourg', 'LV': 'Lettonie', 'LY': 'Libye', 'MA': 'Maroc', 'MC': 'Monaco', 'MD': 'Moldavie',
            'MG': 'Madagascar', 'MH': 'Îles Marshall', 'MK': 'Macédoine', 'ML': 'Mali', 'MM': 'Birmanie (Myanmar)', 'MN': 'Mongolie', 'MO': 'Macao',
            'MP': 'Îles Mariannes', 'MQ': 'Martinique', 'MR': 'Mauritanie', 'MS': 'Montserrat', 'MT': 'Malte', 'MU': 'Île Maurice', 'MV': 'Maldives',
            'MW': 'Malawi', 'MX': 'Mexique', 'MY': 'Malaisie', 'MZ': 'Mozambique', 'NA': 'Namibie', 'NC': 'Nouvelle-Calédonie', 'NE': 'Niger',
            'NF': 'Île Norfolk', 'NG': 'Nigeria', 'NI': 'Nicaragua', 'NL': 'Pays-Bas', 'NO': 'Norvège', 'NP': 'Népal', 'NR': 'Nauru', 'NU': 'Niue',
            'NZ': 'Nouvelle-Zélande', 'OM': 'Oman', 'PA': 'Panama', 'PE': 'Pérou', 'PF': 'Polynésie Française', 'PG': 'Papouasie-Nouvelle-Guinée',
            'PH': 'Philippines', 'PK': 'Pakistan', 'PL': 'Pologne', 'PM': 'Saint-Pierre-et-Miquelon', 'PN': 'Pitcairn', 'PR': 'Porto Rico',
            'PT': 'Portugal', 'PW': 'Palau', 'PY': 'Paraguay', 'QA': 'Qatar', 'RE': 'Réunion', 'RO': 'Roumanie', 'RU': 'Fédération de Russie',
            'RW': 'Rwanda', 'SA': 'Arabie Saoudite', 'SB': 'Îles Salomon', 'SC': 'Seychelles', 'SD': 'Soudan', 'SE': 'Suède', 'SG': 'Singapour',
            'SH': 'Sainte-Hélène', 'SI': 'Slovénie', 'SJ': 'Île Jan Mayen', 'SK': 'Slovaquie (République slovaque)', 'SL': 'Sierra Leone',
            'SM': 'Saint-Marin', 'SN': 'Sénégal', 'SO': 'Somalie', 'SR': 'Surinam', 'ST': 'Sao Tomé-et-Principe', 'SU': 'Union soviétique (obsolète)',
            'SV': 'Salvador', 'SY': 'Syrie', 'SZ': 'Swaziland', 'TC': 'Îles Turks-et-Caïques', 'TD': 'Tchad', 'TF': 'Territoires Antarctiques Français',
            'TG': 'Togo', 'TH': 'Thaïlande', 'TJ': 'Tadjikistan', 'TK': 'Tokelau', 'TM': 'Turkménistan', 'TN': 'Tunisie', 'TO': 'Tonga', 'TP': 'Timor',
            'TR': 'Turquie', 'TT': 'Trinité-et-Tobago', 'TV': 'Tuvalu', 'TW': 'Taïwan', 'TZ': 'Tanzanie', 'UA': 'Ukraine', 'UG': 'Ouganda', 'UK': 'Royaume-Uni',
            'UM': 'Petites îles extérieures des États-Unis', 'US': 'États-Unis', 'UY': 'Uruguay', 'UZ': 'Ouzbékistan', 'VA': 'Vatican',
            'VC': 'Saint-Vincent-et-les-Grenadines', 'VE': 'Vénézuela', 'VG': 'Îles Vierges britanniques', 'VI': 'Îles Vierges des États-Unis', 'VN': 'Vietnam',
            'VU': 'Vanuatu', 'WF': 'Îles Wallis-et-Futuna', 'WS': 'Samoa', 'YE': 'Yémen', 'YT': 'Mayotte', 'YU': 'Yougoslavie (obsolète)', 'ZA': 'Afrique du Sud',
            'ZM': 'Zambie', 'ZR': 'Zaïre', 'ZW': 'Zimbabwe'
        }

        self.countries_codes = [
            ("AF", "004"), ("ZA", "710"), ("AL", "008"), ("DZ", "12"), ("DE", "276"),
            ("AD", "020"), ("AO", "024"), ("AI", "660"), ("AQ", "010"), ("AG", "028"),
            ("AN", "530"), ("SA", "682"), ("AR", "032"), ("AM", "051"), ("AW", "533"),
            ("AU", "036"), ("AT", "040"), ("AZ", "031"), ("BS", "044"), ("BH", "048"),
            ("BD", "050"), ("BE", "056"), ("BZ", "084"), ("BJ", "204"), ("BM", "060"),
            ("BT", ""), ("BY", "064"), ("MM", "068"), ("BO", "070"), ("BA", "072"),
            ("BW", "074"), ("BR", "076"), ("BN", "096"), ("BG", "100"), ("BF", "854"),
            ("BI", "108"), ("KH", "116"), ("CM", "120"), ("CA", "124"), ("CV", "132"),
            ("CL", "152"), ("CN", "156"), ("CX", "162"), ("CY", "196"), ("CO", "170"),
            ("KM", "174"), ("CG", "178"), ("KP", "410"), ("KR", "408"), ("CR", "188"),
            ("CI", "384"), ("HR", "191"), ("CU", "192"), ("DK", "208"), ("DJ", "262"),
            ("DO", "214"), ("DM", "212"), ("EG", "818"), ("AE", "784"), ("EC", "218"),
            ("ER", "232"), ("ES", "724"), ("EE", "233"), ("US", "840"), ("ET", "231"),
            ("RU", "643"), ("FI", "246"), ("FR", "250"), ("FX", ""), ("GA", "266"),
            ("GM", "270"), ("GE", "268"), ("GS", "239"), ("GH", "288"), ("GI", "292"),
            ("UK", ""), ("GR", "300"), ("GD", "308"), ("GL", "304"), ("GP", "312"),
            ("GU", "316"), ("GT", "320"), ("GN", "324"), ("GW", "624"), ("GQ", "226"),
            ("GY", "328"), ("GF", "254"), ("HT", "332"), ("HN", "340"), ("HK", "344"),
            ("HU", "348"), ("SJ", ""), ("MU", "480"), ("NF", ""), ("BV", ""),
            ("KY", ""), ("CC", ""), ("CK", ""), ("FK", ""), ("FO", ""), ("FJ", ""),
            ("HM", ""), ("MP", ""), ("MH", ""), ("SB", ""), ("AS", ""), ("TC", ""),
            ("VG", "092"), ("VI", "850"), ("WF", ""), ("IN", "356"), ("ID", "360"),
            ("IQ", "368"), ("IE", "372"), ("IS", "352"), ("IL", "376"), ("IT", "380"),
            ("JM", "388"), ("JP", "392"), ("JO", "400"), ("KZ", "398"), ("KE", "404"),
            ("KG", "417"), ("KI", "296"), ("KW", "414"), ("BB", ""), ("LA", "418"),
            ("LS", "426"), ("LV", "428"), ("LB", "422"), ("LR", "430"), ("LY", "434"),
            ("LI", "438"), ("LT", "440"), ("LU", "442"), ("MO", "446"), ("MK", "807"),
            ("MG", "450"), ("MY", "458"), ("MW", "454"), ("MV", "462"), ("ML", "466"),
            ("MT", "470"), ("MA", "504"), ("MQ", "474"), ("MR", "478"), ("YT", "175"),
            ("MX", "484"), ("FM", "583"), ("MD", "498"), ("MC", "492"), ("MN", "496"),
            ("MS", "500"), ("MZ", "508"), ("NA", "516"), ("NR", "520"), ("NP", "524"),
            ("NI", "558"), ("NE", "562"), ("NG", "566"), ("NU", "570"), ("NO", "578"),
            ("NC", "540"), ("NZ", "554"), ("IO", "086"), ("OM", "512"), ("UG", "800"),
            ("UZ", "860"), ("PK", "586"), ("PW", "585"), ("PA", "591"), ("PG", "598"),
            ("PY", "600"), ("NL", "528"), ("PE", "604"), ("UM", "581"), ("PH", "608"),
            ("PN", "612"), ("PL", "616"), ("PF", "258"), ("PR", "630"), ("PT", "620"),
            ("QA", "634"), ("CF", ""), ("RE", "638"), ("RO", "642"), ("GB", "826"),
            ("RW", "646"), ("EH", "732"), ("KN", "659"), ("SH", "654"), ("LC", "662"),
            ("VC", "670"), ("SV", ""), ("WS", "882"), ("SM", ""), ("ST", "678"),
            ("SN", "686"), ("SC", "690"), ("SL", "694"), ("SG", "702"), ("SK", "703"),
            ("SI", "705"), ("SO", "706"), ("SD", "736"), ("LK", "144"), ("PM", ""),
            ("SE", "752"), ("CH", "756"), ("SR", "740"), ("SZ", "748"), ("SY", "760"),
            ("TJ", "762"), ("TW", "158"), ("TZ", "834"), ("TD", "148"), ("CS", ""),
            ("CZ", "203"), ("TF", "260"), ("TH", "764"), ("TP", "626"), ("TG", "768"),
            ("TK", "772"), ("TO", "776"), ("TT", ""), ("TN", "788"), ("TM", "795"),
            ("TR", "792"), ("TV", "798"), ("UA", "804"), ("SU", ""), ("UY", "858"),
            ("VU", "548"), ("VA", ""), ("VE", "862"), ("VN", "704"), ("YE", "887"),
            ("YU", ""), ("ZR", ""), ("ZM", "894"), ("ZW", "716")
        ]

    def extract_between_teller_and_mcbc(self, local_ref):
        """Extrait la valeur entre TELLER, et .MCBC"""
        match = re.search(r'TELLER,([^,]+)\.MCBC', local_ref)
        return match.group(1) if match else None

    def extract_value_from_local_ref(self, local_ref, field):
        """Extrait la valeur d'un champ donné depuis local_ref"""
        values = local_ref.split('|')
        if field in self.teller:
            index = self.teller.index(field)
            if index < len(values):
                return values[index]
        return None

    def update_address_based_on_country(self, country_code):
        """Met à jour l'adresse basée sur le code pays"""
        return self.country_addresses.get(country_code, 'Adresse inconnue')

    def update_country_code(self, country_code):
        """Convertit le code pays en code numérique"""
        codes_dict = {code: number for code, number in self.countries_codes if number != ""}
        if country_code is None:
            return None
        return codes_dict.get(str(country_code).strip().upper())

    def process_esri_data_fast(self, date_debut: str, date_fin:str):
        conn = None
        try:
            conn = self.db.connect()
            
            query = text("""
                SELECT 
                    co_code AS Agence,
                    'EUR' AS Devise,
                    'SIPEM' AS Banque,
                    '0' AS `Donneur resident`,
                    '' AS `Code pays donneur d'ordre`,
                    DATE_FORMAT(value_date_1, '%Y/%m/%d') AS Date,
                    amount_local_1 AS Montant,
                    local_ref
                FROM teller_mcbc_his_full
                WHERE transaction_code IN (40, 53)
                AND value_date_1 BETWEEN :date_debut AND :date_fin ;
            """)
            df = pd.read_sql(query, conn, params={"date_debut": date_debut, "date_fin": date_fin})

            
            if df.empty:
                print(f"[INFO] Aucune donnée ESRI trouvée entre {date_debut} et {date_fin}.")
                return pd.DataFrame()


            extracted_data = []
            
            for index, row in df.iterrows():
                local_ref = row['local_ref']
                row_data = {}
                
                for col, field in self.columns_mapping.items():
                    if col == "Type":
                        row_data[col] = self.extract_between_teller_and_mcbc(local_ref)
                    else:
                        row_data[col] = self.extract_value_from_local_ref(local_ref, field)
                
                row_data["Agence"] = row["Agence"]
                row_data["Montant"] = row["Montant"]
                row_data["Devise"] = row["Devise"]
                row_data["Banque"] = row["Banque"]
                row_data["Donneur resident"] = row["Donneur resident"]
                row_data["Date"] = row["Date"]
                
                country_code = row_data.get('Code pays donneur d\'ordre')
                row_data["Adresse donneur d'ordre"] = self.update_address_based_on_country(country_code)
                
                row_data["Code pays"] = self.update_country_code(country_code)
                
                extracted_data.append(row_data)

            extracted_df = pd.DataFrame(extracted_data)

            extracted_df['Code pays donneur d\'ordre'] = extracted_df['Code pays donneur d\'ordre'].str.strip().str.upper()

            desired_order = [
                'Agence', 'Type', 'Référence', 'Banque', 'Donneur d\'ordre', 'Donneur resident', 
                'Adresse donneur d\'ordre', 'Bénéficiaire', 'Bénéficiaire résident', 'Adresse Bénéficiaire',
                'Montant', 'Nature', 'Code économique', 'Devise', 'Code pays', 'Sens', 'Date'
            ]
            
            final_columns = [col for col in desired_order if col in extracted_df.columns]
            result_df = extracted_df[final_columns]

            
            print(f"[INFO] Données ESRI traitées avec succès entre {date_debut} et {date_fin} ({len(result_df)} lignes) ✅")
            return result_df,final_columns

        except Exception as e:
            print(f"[ERREUR] process_esri_data_fast : {e}")
            import traceback 
            print(f"[DEBUG] {traceback.format_exc()}")
            return pd.DataFrame()
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")