import os
import zipfile
import tempfile
import shutil
import pandas as pd
import geopandas as gpd
from app import db
from app.models.organisme import Organisme
from app.validators.organisme_validator import OrganismeValidator

class OrganismeService:
    @staticmethod
    def import_from_file(file_path):
        """
        Importe des organismes depuis un fichier (CSV, SHP, GeoJSON, ZIP)
        
        Args:
            file_path (str): Chemin vers le fichier à importer
            
        Returns:
            dict: Résultat de l'importation avec statut et messages
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            # Gérer les fichiers ZIP
            if file_ext == '.zip':
                # Créer un dossier temporaire pour extraire les fichiers
                temp_dir = tempfile.mkdtemp()
                try:
                    # Extraire tous les fichiers du ZIP
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    # Chercher un fichier contenant les données d'organismes
                    csv_files = [f for f in os.listdir(temp_dir) if f.lower().endswith('.csv') and 't_organisme' in f.lower()]
                    shp_files = [f for f in os.listdir(temp_dir) if f.lower().endswith('.shp') and 't_organisme' in f.lower()]
                    
                    if csv_files:
                        # Utiliser le premier fichier CSV trouvé
                        file_path = os.path.join(temp_dir, csv_files[0])
                        # Lire le fichier CSV
                        df = pd.read_csv(file_path)
                        return OrganismeService._process_dataframe(df)
                    elif shp_files:
                        # Utiliser le premier fichier SHP trouvé
                        shp_path = os.path.join(temp_dir, shp_files[0])
                        # Lire le fichier SHP
                        gdf = gpd.read_file(shp_path)
                        return OrganismeService._process_dataframe(gdf)
                    else:
                        return {
                            'success': False,
                            'message': "Aucun fichier contenant des données d'organismes n'a été trouvé dans l'archive ZIP"
                        }
                finally:
                    # Nettoyer le dossier temporaire
                    shutil.rmtree(temp_dir)
            # Traiter les autres formats
            elif file_ext == '.csv':
                df = pd.read_csv(file_path)
                return OrganismeService._process_dataframe(df)
            elif file_ext in ['.shp', '.geojson']:
                gdf = gpd.read_file(file_path)
                return OrganismeService._process_dataframe(gdf)
            else:
                return {
                    'success': False,
                    'message': f"Format de fichier non supporté: {file_ext}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Erreur lors de l'importation: {str(e)}"
            }
    
    @staticmethod
    def _process_dataframe(df):
        """
        Traite un DataFrame contenant des données d'organismes
        
        Args:
            df (DataFrame): DataFrame avec les données d'organismes
            
        Returns:
            dict: Résultat du traitement avec statut et messages
        """
        # Validation des données
        validator = OrganismeValidator()
        validation_results = validator.validate_dataframe(df)
        
        if not validation_results['valid']:
            return {
                'success': False,
                'message': "Validation échouée",
                'errors': validation_results['errors']
            }
        
        # Préparation des données pour l'insertion
        organismes = []
        for _, row in df.iterrows():
            organisme = OrganismeService._create_organisme_from_row(row)
            organismes.append(organisme)
        
        # Insertion en base de données
        try:
            db.session.bulk_save_objects(organismes)
            db.session.commit()
            
            return {
                'success': True,
                'message': f"{len(organismes)} organismes importés avec succès",
                'count': len(organismes)
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f"Erreur lors de l'insertion en base: {str(e)}"
            }
    
    @staticmethod
    def _create_organisme_from_row(row):
        """
        Crée un objet Organisme à partir d'une ligne de DataFrame
        
        Args:
            row: Ligne de DataFrame avec les données d'organisme
            
        Returns:
            Organisme: Instance du modèle Organisme
        """
        organisme = Organisme()
        
        # Mapper les colonnes du DataFrame vers les attributs du modèle
        for column in Organisme.__table__.columns.keys():
            # Vérifier si la colonne existe dans le DataFrame
            if hasattr(row, column) or column in row:
                value = row.get(column)
                setattr(organisme, column, value)
        
        return organisme

    @staticmethod
    def get_all_organismes(page=1, per_page=10):
        """
        Récupère tous les organismes avec pagination
        
        Args:
            page (int): Numéro de page
            per_page (int): Nombre d'éléments par page
            
        Returns:
            Pagination: Objet de pagination contenant les organismes
        """
        return Organisme.query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_organisme_by_code(or_code):
        """
        Récupère un organisme par son code
        
        Args:
            or_code (str): Code de l'organisme
            
        Returns:
            Organisme: Instance de l'organisme ou None si non trouvé
        """
        return Organisme.query.get(or_code)
    
    @staticmethod
    def validate_organisme(organisme):
        """
        Valide un organisme existant
        
        Args:
            organisme (Organisme): Instance de l'organisme à valider
            
        Returns:
            dict: Résultat de la validation
        """
        validator = OrganismeValidator()
        return validator.validate_organisme(organisme)
