import pymysql  # Assurez-vous que pymysql est importé correctement
import pandas as pd
import os
import time

EXTRACT_DATE='20250620'

class Credit_outstanding_report:
def connect_to_database(host, user, password, database):
    """Connect to the database and return the connection object."""
    try:
        conn = pymysql.connect(
            host=host,       # Utilisation des paramètres fournis
            user=user,       # Nom d'utilisateur
            password=password,  # Mot de_passe
            database=database,  # Base de_données
            cursorclass=pymysql.cursors.DictCursor  # Ajoutez cette ligne pour obtenir les résultats sous forme de_dictionnaire
        )
        print("Connection to the database was successful!")
        return conn
    except pymysql.MySQLError as err:
        print(f"Error: Unable to connect to the database. details: {err}")
        return None

def fetch_data_from_table(conn, query):
    """Fetch data from the database based on the query."""
    try:
        cursor = conn.cursor()  # Pas besoin de_'dictionary=True', DictCursor est déjà configuré
        print(f"Executing query in progress...")
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Query executed successfully. Fetched {len(results)} rows.")
        return results
    except pymysql.MySQLError as err:
        print(f"Error: Unable to execute query. Query: {query} | Error: {err}")
        return None
    finally:
        cursor.close()

def split_value(value, index, default=None):
    """Helper function to split values by '|' and return the part at the given index."""
    if value:
        parts = value.split('|')
        return parts[index] if len(parts) > index else  default
    return  default 

def modify_column_data(data):
    """Modify the 'contract_balance.open_balance' column to keep only the first value before the pipe (|)."""
    new_data=[]
    for row in data:  
      
        if row['Nombre_de_jour_retard']:
            
            # pirnt(f"Nombre_de_jour_retard: {row['Date_pret']}")
            if  int(row['Nombre_de_jour_retard'])<0 :  
                row['Nombre_de_jour_retard'] = 0
            else:
                row['Nombre_de_jour_retard'] = int(row['Nombre_de_jour_retard'])
        else:
            row['Nombre_de_jour_retard'] = 0 
                
        input_string = row['type_sysdate']
        type_sysdate = row['type_sysdate']
        if input_string or type_sysdate: 
            entries = input_string.split('|')   
            
            matching_indice_montant_pret=[] 
            for index, entry in enumerate(entries):
                if entry.startswith("TOTCOMMITMENT"):  
                    matching_indice_montant_pret.append(index)  # Affiche chaque entrée
  
            if not matching_indice_montant_pret: 
                row['Montant_pret']=0
            else: 
                montant_pert_total=0
                for index in matching_indice_montant_pret: 
                    debit_mvmt=0
                    credit_mvmt=0
                    open_balance=0 
                    if split_value(row['debit_mvmt'],index):
                        debit_mvmt = split_value(row['debit_mvmt'],index) 
                        if debit_mvmt.strip() == '' or debit_mvmt is None:
                            debit_mvmt = '0.0' 
                        montant_pert_total= round(float(debit_mvmt),2)
                    if split_value(row['credit_mvmt'],index):
                        credit_mvmt = split_value(row['credit_mvmt'],index)
                        if credit_mvmt.strip() == '' or credit_mvmt is None:
                            credit_mvmt = '0.0' 
                        montant_pert_total= round(float(credit_mvmt),2)
                    if split_value(row['open_balance'],index):
                        open_balance = split_value(row['open_balance'],index)
                        if open_balance.strip() == '' or open_balance is None:
                            open_balance = '0.0' 
                        montant_pert_total= round(float(open_balance),2) 
                row['Montant_pret'] =  montant_pert_total * -1 if montant_pert_total < 0 else montant_pert_total  
            
            matching_indice_Appele_Non_verse=[]   
            for index, entry in enumerate(entries): 
                if entry.startswith("CURACCOUNT") or entry.startswith("DUEACCOUNT"):   
                    date_str = entry.split("-")[1] if "-" in entry else ""
              
                    if not date_str:
                        matching_indice_Appele_Non_verse.append(index)
                    elif int(date_str) <= int(EXTRACT_DATE): 
                        matching_indice_Appele_Non_verse.append(index) 
            if not matching_indice_Appele_Non_verse:
                row['Capital_Non_appele_ech']=0
            else:     
                montant_pert_total=0 
              
                for index in matching_indice_Appele_Non_verse: 
                    debit_mvmt=0
                    credit_mvmt=0
                    open_balance=0 
                    if split_value(row['debit_mvmt'],index):
                        debit_mvmt = split_value(row['debit_mvmt'],index)  
                        if debit_mvmt.strip() == '' or debit_mvmt is None:
                            debit_mvmt = '0.0'  
                    if split_value(row['credit_mvmt'],index):
                        credit_mvmt = split_value(row['credit_mvmt'],index) 
                        if credit_mvmt.strip() == '' or credit_mvmt is None:
                            credit_mvmt = '0.0' 
                    if split_value(row['open_balance'],index):
                        
                        open_balance = split_value(row['open_balance'],index)
                        if open_balance.strip() == '' or open_balance is None:
                            open_balance = '0.0'   
                    montant_pert_total+= round(float(credit_mvmt),2)
                    montant_pert_total+= round(float(debit_mvmt),2) 
                    montant_pert_total+= round(float(open_balance),2) 
                    
                row['Capital_Non_appele_ech'] =montant_pert_total
                if row['Capital_Non_appele_ech']==0 and   row['arr_status'] =='EXPIRED' and row['Nombre_de_jour_retard']==0: 
                    for index in matching_indice_Appele_Non_verse: 
                        debit_mvmt=0
                        credit_mvmt=0
                        open_balance=0 
                        if split_value(row['debit_mvmt'],index):
                            debit_mvmt = split_value(row['debit_mvmt'],index)  
                            if debit_mvmt.strip() == '' or debit_mvmt is None:
                                debit_mvmt = '0.0'  
                        if split_value(row['credit_mvmt'],index):
                            credit_mvmt = split_value(row['credit_mvmt'],index) 
                            if credit_mvmt.strip() == '' or credit_mvmt is None:
                                credit_mvmt = '0.0' 
                        if split_value(row['open_balance'],index):
                            
                            open_balance = split_value(row['open_balance'],index)
                            if open_balance.strip() == '' or open_balance is None:
                                open_balance = '0.0'   
                 
            indices_total_iterest_echus=[]
            for index, entry in enumerate(entries):    
               if any(f"PA{x}PRINCIPALINT" in entry for x in range(1, 5)) and "SP" not in entry: 
                    indices_total_iterest_echus.append(index) 
            if not indices_total_iterest_echus:
                row['Total_interet_echus']=0
            else:
                montant_pert_total=0
                for index in indices_total_iterest_echus:  
                    open_balance=0
                    if split_value(row['open_balance'],index):  
                        open_balance = split_value(row['open_balance'],index) 
                        if open_balance.strip() == '' or open_balance is None:
                            open_balance = '0.0'    
                    montant_pert_total= round(float(open_balance),2)    
                row['Total_interet_echus'] =montant_pert_total * -1 if montant_pert_total < 0 else montant_pert_total   
            
     
            # Initialisation de_la liste de_résultats
            matching_indice_Non_appele_verse = [] 
            
            for index, entry in enumerate(entries):  # Si l'entrée est dans la liste des entrées valides
                if entry == "CURACCOUNT" or entry.startswith("DUEACCOUNT"): # Si l'entrée est dans la liste des entrées valides
                    continue  # Passer à l'itération suivante sans rien faire
                else: 
                    base_accounts = ["PA1ACCOUNT", "PA2ACCOUNT", "PA3ACCOUNT", "PA4ACCOUNT"]
                    years = ["2024", "2025"] 
                    if any(entry == account or any(entry.startswith(f"{account}-{year}") for year in years) for account in base_accounts):
                        date_str = entry.split("-")[1] if "-" in entry else ""
                        if not date_str:
                            matching_indice_Non_appele_verse.append(index)
                        elif int(date_str) <= int(EXTRACT_DATE):
                            matching_indice_Non_appele_verse.append(index)
                        
            
            # print('matching_indice_Non_appele_verse: ',matching_indice_Non_appele_verse)                 
            if not matching_indice_Non_appele_verse: 
                row['Capital_Appele_Non_verse']=0
            # elif row['Nombre_de_jour_retard'] == 0: 
            #     row['Capital_Appele_Non_verse']=0
            else:  
                # print(matching_indice_Non_appele_verse) 
                montant_pert_total=0 
                debit_mvmt=0
                credit_mvmt=0
                open_balance=0 
                
                for index in matching_indice_Non_appele_verse: 
                    value = split_value(row['debit_mvmt'], index)
                    if value: 
                        debit_mvmt += round(float(value),2) 
                     
                    value_2 = split_value(row['credit_mvmt'], index)
                    if value_2:
                        credit_mvmt += round(float(value_2),2)  
                     
                    value_3 = split_value(row['open_balance'], index)
                    if value_3: 
                        open_balance += round(float(value_3),2) 
                  
                if (row['Produits'].startswith('AL.ESCO') and row['Nombre_de_jour_retard'] > 0):  
                    row['Capital_Appele_Non_verse'] = round(float(open_balance),2)+round(float(credit_mvmt),2)+ round(float(debit_mvmt),2)
                else:
                    row['Capital_Appele_Non_verse'] = round(float(open_balance),2)+round(float(credit_mvmt),2)+ round(float(debit_mvmt),2) 
                        
                row['Capital_Appele_Non_verse'] =row['Capital_Appele_Non_verse'] 
                
                
                if row['Capital_Appele_Non_verse']  == 0 and row['Nombre_de_jour_retard'] > 0 and row['arr_status'] =='EXPIRED' :
                    # print("IO ALOHA")
                    for index in matching_indice_Non_appele_verse: 
                        debit_mvmt=0
                        credit_mvmt=0    
                        open_balance=0   
                        if split_value(row['debit_mvmt'],index):
                            debit_mvmt = split_value(row['debit_mvmt'],index) 
                            if debit_mvmt.strip() == '' or debit_mvmt is None:
                                debit_mvmt = '0.0'  
                        if split_value(row['credit_mvmt'],index):
                            credit_mvmt = split_value(row['credit_mvmt'],index) 
                            if credit_mvmt.strip() == '' or credit_mvmt is None:
                                credit_mvmt = '0.0'  
                        if split_value(row['open_balance'],index):
                            open_balance = split_value(row['open_balance'],index)
                            if open_balance.strip() == '' or open_balance is None:
                                open_balance = '0.0'   
                    max_value = max(round(float(open_balance),2), round(float(credit_mvmt),2), round(float(debit_mvmt),2))
           
            valeur_retard = row.get('Nombre_de_jour_retard', '')

            if isinstance(valeur_retard, str):  # Si c'est une chaîne, nettoyez-la
                valeur_retard = valeur_retard.strip()

            # Vérifier si la valeur est convertible en entier
            try:
                retard = int(valeur_retard) 
                if retard:
                    row['OD & PEN']=safe_float(row['total_OD']) + safe_float(row['OD Pen'])
                else:
                    row['OD & PEN']=0# Convertit la valeur en entier
                    row['OD Pen']=0
                # Appliquez les conditions
                if 0 < retard <= 30:
                    row['Statut_du_client'] = 'PA1'
                    row['Statut_du_client'] = 'PA1'
                elif 30 < retard <= 60:
                    row['Statut_du_client'] = 'PA2'
                elif 60 < retard <= 90:
                    row['Statut_du_client'] = 'PA3'
                elif retard > 90:
                    row['Statut_du_client'] = 'PA4'
                else:
                    row['Statut_du_client'] = ''  # Optionnel pour les cas inattendus
            except (ValueError, TypeError):  # Gérer les cas où la conversion échoue
                row['Statut_du_client'] = ''
            # Gestion des cas invalides ou valides
         
            # print(f"Statut_du_client: {row['Statut_du_client']}")
            if  row['Statut_du_client']==None:
                row['Nombre_de_jour_retard'] = '' 
   
             
        capital_appele =row['Capital_Appele_Non_verse']
        capital_non_appele = row['Capital_Non_appele_ech']
    
        if capital_appele==0 and row['Statut_du_client']=='PA1':
            row['Nombre_de_jour_retard'] =''
            row['Statut_du_client'] =''
        if (row['Produits'].startswith('AL.ESCO') and safe_float(row['Nombre_de_jour_retard'])  > 0):
            row['Total_capital_echus_non_echus'] = row['Capital_Appele_Non_verse']
        else:
            row['Total_capital_echus_non_echus'] = capital_appele + capital_non_appele  
     
        #     pass
        row['Total_capital_echus_non_echus'] = safe_float(row['Total_capital_echus_non_echus'])*-1 if safe_float(row['Total_capital_echus_non_echus']) < 0 else safe_float(row['Total_capital_echus_non_echus'])
        
        row['total_OD']=safe_float(row['Total_capital_echus_non_echus']) 
        if row['total_OD']==0.0 and (row['arr_status'] =='EXPIRED' or row['arr_status'] == 'CLOSE'):  
            continue
        row['Capital_Non_appele_ech']=  row['Capital_Non_appele_ech']*-1 if row['Capital_Non_appele_ech'] < 0 else row['Capital_Non_appele_ech']
        row['Capital_Appele_Non_verse']=  row['Capital_Appele_Non_verse']*-1 if row['Capital_Appele_Non_verse'] < 0 else row['Capital_Appele_Non_verse']
        
       
        for key in ['bill_status','Numero_compte','total_OD','settle_status','credit_mvmt','debit_mvmt','type_sysdate','open_balance','Montant_pret']:
            if key in row:
                del row[key]
        new_data.append(row)
    # print(new_data)
    return new_data
def safe_float(value):
    try:
        return round(float(value),2) if value is not None else 0.0
    except (ValueError, TypeError):
        return 0.0
 
def data_base_query(offset,date_):
       return f"""
            SELECT 
                arrangement.co_code AS Agence,
                arrangement.customer AS identification_client,
                arrangement.id AS Numero_pret,
                arrangement.linked_appl_id AS linked_appl_id,
                COALESCE(arrangement.orig_contract_date, arrangement.start_date) AS Date_pret,  
                (SELECT maturity_date FROM `aa_account_details_mcbc_live_full` WHERE  id=arrangement.id) AS Date_fin_pret,  
                (SELECT CONCAT(customer.short_name, ' ', customer.name_1) 
                FROM customer_mcbc_live_full AS customer  
                WHERE FIND_IN_SET(customer.id, 
                        REPLACE(
                            IF(LOCATE('|', arrangement.customer) > 0, 
                                SUBSTRING_INDEX(arrangement.customer, '|', 1), 
                                arrangement.customer
                            ), 
                            '|', ','
                        )
                    ) LIMIT 1
                ) AS Nom_client,
                
                
                arrangement.product AS Produits,
                (SELECT amount 
                FROM AA_ARR_TERM_MCBC_LIVE_FULL 
                WHERE id_comp_1 = arrangement.id 
                AND activity IN ('LENDING-TAKEOVER-ARRANGEMENT', 'LENDING-NEW-ARRANGEMENT')) AS Amount,
                (SELECT DATEDIFF(maturity_date, base_date) 
                FROM aa_account_details_mcbc_live_full 
                WHERE id = arrangement.id LIMIT 1) AS Duree_Remboursement,
                (SELECT effective_rate  
                FROM aa_arr_interest_mcbc_live_full 
                WHERE id_comp_1 = arrangement.id  
                AND id_comp_2 = 'PRINCIPALINT' LIMIT 1) AS taux_d_interet,  
                
                -- Correction pour le calcul du nombre de jours de retard :
                (SELECT DATEDIFF({date_}, MIN(payment_date))  
                FROM aa_bill_details_mcbc_live_full 
                WHERE arrangement_id = arrangement.id 
                AND settle_status = 'UNPAID'
                GROUP BY arrangement_id) AS Nombre_de_jour_retard,
                
                (SELECT MIN(payment_date)  
                FROM aa_bill_details_mcbc_live_full 
                WHERE arrangement_id = arrangement.id 
                ORDER BY payment_date DESC LIMIT 1) AS payment_date,
                
                '' AS Statut_du_client,
                '' AS Capital_Non_appele_ech,
                '' AS Capital_Appele_Non_verse,
                '' AS Total_capital_echus_non_echus,
                '' AS Total_interet_echus,
                
                
                '' AS `OD Pen`,
                
                (SELECT SUM(os_total_amount) FROM `aa_bill_details_mcbc_live_full`
                WHERE arrangement_id=arrangement.id GROUP BY payment_date ORDER BY `payment_date` DESC LIMIT 1) as total_OD,
                
                '' AS `OD & PEN`,
                '' AS `Solde du client`,
                
                (SELECT gender 
                FROM customer_mcbc_live_full AS customer  
                WHERE FIND_IN_SET(customer.id, REPLACE(arrangement.customer, '|', ',')) LIMIT 1) AS Genre,

                (SELECT industry.description  
                FROM industry_mcbc_live_full AS industry 
                INNER JOIN customer_mcbc_live_full AS customer ON industry.id = customer.industry 
                WHERE FIND_IN_SET(customer.id, REPLACE(arrangement.customer, '|', ',')) LIMIT 1) AS Secteur_d_activité,

                (SELECT industry.id  
                FROM industry_mcbc_live_full AS industry 
                INNER JOIN customer_mcbc_live_full AS customer ON industry.id = customer.industry 
                WHERE FIND_IN_SET(customer.id, REPLACE(arrangement.customer, '|', ',')) LIMIT 1) AS Secteur_d_activité_code, 
                
                (SELECT account_officer 
                FROM customer_mcbc_live_full AS customer  
                WHERE FIND_IN_SET(customer.id, REPLACE(arrangement.customer, '|', ',')) LIMIT 1) AS Agent_de_gestion,
                
                (SELECT salary 
                FROM customer_mcbc_live_full AS customer  
                WHERE FIND_IN_SET(customer.id, REPLACE(arrangement.customer, '|', ',')) LIMIT 1) AS Chiff_affaire,

                (SELECT collateral_code 
                FROM collateral_right_mcbc_live_full 
                WHERE SUBSTRING(id, 1, LOCATE('.', id) - 1) = arrangement.customer LIMIT 1) AS Code_Garantie, 
                
                ( SELECT SUM(nominal_value)
                FROM `collateral_mcbc_live_full` 
                WHERE id LIKE CONCAT((
                    SELECT em_lo.co_coll_id
                    FROM em_lo_application_mcbc_live_full as em_lo
                    INNER JOIN collateral_right_mcbc_live_full as coll_rigth on coll_rigth.id=em_lo.co_coll_id
                    WHERE em_lo.arrangement_id = arrangement.id 
                ), '%') 
                AND collateral_type=200) as Valeur_garantie, 
                

                (SELECT bill_status 
                FROM aa_bill_details_mcbc_live_full 
                WHERE bill_status NOT REGEXP 'SETTLED' 
                AND arrangement_id = arrangement.id 
                ORDER BY payment_date ASC LIMIT 1) AS bill_status,

                (SELECT alt_acct_id 
                FROM account_mcbc_live_full 
                WHERE id = arrangement.linked_appl_id LIMIT 1) AS Numero_compte,   

                (SELECT settle_status  
                FROM aa_bill_details_mcbc_live_full 
                WHERE settle_status = 'UNPAID' LIMIT 1) AS settle_status,
            

                (SELECT credit_mvmt 
                FROM eb_cont_bal_mcbc_live_full 
                WHERE id = arrangement.linked_appl_id) AS credit_mvmt, 

                (SELECT debit_mvmt 
                FROM eb_cont_bal_mcbc_live_full 
                WHERE id = arrangement.linked_appl_id) AS debit_mvmt,  

                (SELECT type_sysdate 
                FROM eb_cont_bal_mcbc_live_full 
                WHERE id = arrangement.linked_appl_id LIMIT 1) AS type_sysdate,

                (SELECT open_balance 
                FROM eb_cont_bal_mcbc_live_full 
                WHERE id = arrangement.linked_appl_id LIMIT 1) AS open_balance, 
                arrangement.arr_status,
                '' AS Montant_pret
            FROM 
                aa_arrangement_mcbc_live_full AS arrangement  
            WHERE 
                arrangement.product_line = 'LENDING'
                AND arrangement.arr_status IN ('CURRENT', 'EXPIRED', 'AUTH','CLOSE')    
            HAVING settle_status IS NOT NULL
            LIMIT 200 OFFSET {offset}

            """      
            
def export_to_excel(data, file_name):
    """Export data to an Excel file."""
    if not data:
        print("No data to export!")
        return

    try:
        df = pd.DataFrame(data)
        df.to_excel(file_name, index=False, engine='openpyxl')
        print(f"Data has been exported to {file_name} successfully!")
    except Exception as e:
        print(f"Error while exporting to Excel: {e}")

if __name__ == "__main__":
    # Database configuration
    db_config = {
        "host": "localhost",      # Replace with your database host
        "user": "root",               # Replace with your database username
        "password": "",       # Replace with your database password
        "database": "dfe"             # Replace with your database name
    }
    
    # SQL query to execute
 
 
    # output_file_template = "output_offset_{offset}.xlsx"
    # define the path template for the output file
    output_file_template = "./out_put_etat_des_encours/etat_des_encours_offset_{offset}.xlsx"

    # Check if the directory exists, and if not, create it
    output_dir = os.path.dirname(output_file_template)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Connect to the database
    conn = connect_to_database(**db_config) 
    if conn:
        try:
            for offset in range(0, 10000, 200): 
                start_time = time.time()  # Début du chronométrage
                # structure de la date =='Année, mois, jour'
                data = fetch_data_from_table(conn,  data_base_query(offset,EXTRACT_DATE))
                if data:
                    k=offset
                    print("Data fetched successfully in page =============> ", k+200," / 10000") 
                    
                    modified_data = modify_column_data(data) 
                    output_file = output_file_template.format(offset=(k+200))
                    export_to_excel(modified_data, output_file)
                    elapsed_time = time.time() - start_time 
                    print(f"✅ Data fetched successfully for page {k+200} / 10000 in {elapsed_time:.2f} seconds")
                else:
                    print("No data was fetched from the database.") 
        finally:
            conn.close()
    else:
        print("Database connection failed!")
 
# 032 01 631 89

