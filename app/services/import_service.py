import os
import zipfile
import tempfile
import shutil
import pandas as pd
import geopandas as gpd
from app import db
from app.services.adresse_service import AdresseService
from app.services.organisme_service import OrganismeService

class ImportService:
    @staticmethod
    def import_from_file(file_path):
        """
        Importe les données depuis un fichier (ZIP) et analyse les différentes tables GRACE THD
        
        Args:
            file_path (str): Chemin vers le fichier à importer
            
        Returns:
            dict: Résultat de l'importation avec statut et messages pour chaque table
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        results = {
            'success': True,
            'message': 'Importation réussie',
            'tables': []
        }
        
        try:
            # Vérifier si c'est un fichier ZIP
            if file_ext != '.zip':
                return {
                    'success': False,
                    'message': 'Seuls les fichiers ZIP sont acceptés pour l\'importation multi-tables'
                }
            
            # Créer un dossier temporaire pour extraire les fichiers
            temp_dir = tempfile.mkdtemp()
            try:
                # Extraire tous les fichiers du ZIP
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Vérifier les fichiers disponibles
                all_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        all_files.append(file_path)
                
                # Rechercher les fichiers pour chaque table en filtrant les extensions
                adresse_files = [f for f in all_files if 't_adresse' in f.lower() and (
                    f.lower().endswith('.shp') or 
                    f.lower().endswith('.csv') or 
                    f.lower().endswith('.geojson')
                )]
                
                organisme_files = [f for f in all_files if 't_organisme' in f.lower() and (
                    f.lower().endswith('.shp') or 
                    f.lower().endswith('.csv') or 
                    f.lower().endswith('.geojson')
                )]
                
                # Traiter t_adresse
                if adresse_files:
                    # Sélectionner le premier fichier trouvé pour t_adresse
                    adresse_file = adresse_files[0]
                    adresse_result = AdresseService.import_from_file(adresse_file)
                    results['tables'].append({
                        'table': 't_adresse',
                        'success': adresse_result['success'],
                        'message': adresse_result['message'],
                        'errors': adresse_result.get('errors', [])
                    })
                    if not adresse_result['success']:
                        results['success'] = False
                else:
                    results['tables'].append({
                        'table': 't_adresse',
                        'success': False,
                        'message': 'Aucun fichier trouvé pour la table t_adresse'
                    })
                
                # Traiter t_organisme
                if organisme_files:
                    # Sélectionner le premier fichier trouvé pour t_organisme
                    organisme_file = organisme_files[0]
                    organisme_result = OrganismeService.import_from_file(organisme_file)
                    results['tables'].append({
                        'table': 't_organisme',
                        'success': organisme_result['success'],
                        'message': organisme_result['message'],
                        'errors': organisme_result.get('errors', [])
                    })
                    if not organisme_result['success']:
                        results['success'] = False
                else:
                    results['tables'].append({
                        'table': 't_organisme',
                        'success': False,
                        'message': 'Aucun fichier trouvé pour la table t_organisme'
                    })
                
                # Mettre à jour le message global
                if not results['success']:
                    results['message'] = 'Certaines tables n\'ont pas pu être importées. Consultez les détails ci-dessous.'
            finally:
                # Nettoyer le dossier temporaire
                shutil.rmtree(temp_dir)
                
            return results
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Erreur lors de l'importation: {str(e)}"
            }
