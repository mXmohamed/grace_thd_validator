import os
import csv
import datetime
from app.services.adresse_service import AdresseService
from app.services.organisme_service import OrganismeService
from app.models.adresse import Adresse
from app.models.organisme import Organisme

class ExportService:
    @staticmethod
    def generate_validation_report(results, export_dir):
        """
        Génère un rapport de validation unique pour toutes les tables importées
        
        Args:
            results (dict): Résultats de validation pour chaque table
            export_dir (str): Répertoire où enregistrer le rapport
            
        Returns:
            str: Chemin vers le fichier de rapport généré
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rapport_validation_grace_{timestamp}.csv"
        file_path = os.path.join(export_dir, filename)
        
        # Création du répertoire d'export s'il n'existe pas
        os.makedirs(export_dir, exist_ok=True)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['table', 'code_objet', 'controle', 'statut', 'message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            
            # Ajout des résultats pour chaque table
            for table_result in results.get('tables', []):
                table_name = table_result.get('table')
                
                # Statut global de la table
                writer.writerow({
                    'table': table_name,
                    'code_objet': 'GLOBAL',
                    'controle': 'Validation globale',
                    'statut': 'OK' if table_result.get('success') else 'NOK',
                    'message': table_result.get('message')
                })
                
                # Erreurs détaillées
                for error in table_result.get('errors', []):
                    writer.writerow({
                        'table': table_name,
                        'code_objet': error.get('code', 'N/A'),
                        'controle': error.get('controle', 'N/A'),
                        'statut': 'NOK',
                        'message': error.get('message', '')
                    })
                
                # Si aucune erreur mais que la table a été importée, on génère un rapport détaillé
                if table_result.get('success') and 'errors' not in table_result:
                    ExportService._add_detailed_validation(writer, table_name)
        
        return file_path
    
    @staticmethod
    def _add_detailed_validation(writer, table_name):
        """
        Ajoute des validations détaillées pour chaque enregistrement d'une table
        
        Args:
            writer: Writer CSV pour écrire les résultats
            table_name (str): Nom de la table
        """
        if table_name == 't_adresse':
            # Récupérer toutes les adresses et les valider individuellement
            adresses = Adresse.query.all()
            for adresse in adresses:
                result = AdresseService.validate_adresse(adresse)
                
                # Résultat global pour cette adresse
                writer.writerow({
                    'table': 't_adresse',
                    'code_objet': adresse.ad_code,
                    'controle': 'Validation complète',
                    'statut': 'OK' if result['valid'] else 'NOK',
                    'message': 'Tous les contrôles sont valides' if result['valid'] else 'Des contrôles ont échoué'
                })
                
                # Détails des erreurs s'il y en a
                for error in result.get('errors', []):
                    writer.writerow({
                        'table': 't_adresse',
                        'code_objet': adresse.ad_code,
                        'controle': error.get('controle', 'N/A'),
                        'statut': 'NOK',
                        'message': error.get('message', '')
                    })
        
        elif table_name == 't_organisme':
            # Récupérer tous les organismes et les valider individuellement
            organismes = Organisme.query.all()
            for organisme in organismes:
                result = OrganismeService.validate_organisme(organisme)
                
                # Résultat global pour cet organisme
                writer.writerow({
                    'table': 't_organisme',
                    'code_objet': organisme.or_code,
                    'controle': 'Validation complète',
                    'statut': 'OK' if result['valid'] else 'NOK',
                    'message': 'Tous les contrôles sont valides' if result['valid'] else 'Des contrôles ont échoué'
                })
                
                # Détails des erreurs s'il y en a
                for error in result.get('errors', []):
                    writer.writerow({
                        'table': 't_organisme',
                        'code_objet': organisme.or_code,
                        'controle': error.get('controle', 'N/A'),
                        'statut': 'NOK',
                        'message': error.get('message', '')
                    })
