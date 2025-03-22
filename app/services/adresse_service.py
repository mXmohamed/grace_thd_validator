import os
import zipfile
import tempfile
import shutil
import pandas as pd
import geopandas as gpd
from shapely import wkt
from app import db
from app.models.adresse import Adresse
from app.validators.adresse_validator import AdresseValidator

class AdresseService:
    @staticmethod
    def import_from_file(file_path):
        """
        Importe des adresses depuis un fichier (CSV, SHP, GeoJSON, ZIP)
        
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
                    
                    # Chercher un fichier SHP dans le dossier (ignorer les fichiers auxiliaires)
                    shp_files = [f for f in os.listdir(temp_dir) if f.lower().endswith('.shp') and 't_adresse' in f.lower()]
                    csv_files = [f for f in os.listdir(temp_dir) if f.lower().endswith('.csv') and 't_adresse' in f.lower()]
                    geojson_files = [f for f in os.listdir(temp_dir) if f.lower().endswith('.geojson') and 't_adresse' in f.lower()]
                    
                    if shp_files:
                        # Utiliser le premier fichier SHP trouvé
                        shp_path = os.path.join(temp_dir, shp_files[0])
                        
                        # Lire le fichier SHP
                        gdf = gpd.read_file(shp_path)
                        
                        # Convertir à EPSG:4326 si nécessaire
                        if gdf.crs and gdf.crs != "EPSG:4326":
                            gdf = gdf.to_crs("EPSG:4326")
                    
                    elif csv_files:
                        # Utiliser le premier fichier CSV trouvé
                        csv_path = os.path.join(temp_dir, csv_files[0])
                        
                        # Lire le fichier CSV avec une gestion d'erreurs améliorée
                        try:
                            df = pd.read_csv(csv_path, 
                                          sep=';',  # Utiliser le point-virgule comme séparateur
                                          on_bad_lines='skip',  # Ignorer les lignes problématiques
                                          dtype=str,  # Tout traiter comme des chaînes
                                          encoding='utf-8-sig')  # Gérer les BOM
                        except:
                            # Fallback au cas où on_bad_lines n'est pas disponible (versions pandas plus anciennes)
                            df = pd.read_csv(csv_path, 
                                          sep=';', 
                                          error_bad_lines=False, 
                                          warn_bad_lines=True,
                                          dtype=str,
                                          encoding='utf-8-sig')
                        
                        # Vérifier si les colonnes de géométrie existent
                        if 'longitude' in df.columns and 'latitude' in df.columns:
                            # Convertir les colonnes en numérique
                            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
                            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
                            
                            # Créer un GeoDataFrame à partir des coordonnées
                            gdf = gpd.GeoDataFrame(
                                df, 
                                geometry=gpd.points_from_xy(df.longitude, df.latitude),
                                crs="EPSG:4326"
                            )
                        elif 'geom' in df.columns:
                            # Filtrer les géométries valides
                            df = df[df['geom'].notna()]
                            try:
                                # Convertir les géométries WKT en objets shapely
                                df['geometry'] = df['geom'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)
                                # Filtrer les lignes avec des géométries valides
                                df = df[df['geometry'].notna()]
                                gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
                            except Exception as e:
                                return {
                                    'success': False,
                                    'message': f"Erreur lors de la conversion des géométries: {str(e)}"
                                }
                        else:
                            return {
                                'success': False,
                                'message': "Le fichier CSV ne contient pas de colonnes de géométrie (longitude/latitude ou geom)"
                            }
                    
                    elif geojson_files:
                        # Utiliser le premier fichier GeoJSON trouvé
                        geojson_path = os.path.join(temp_dir, geojson_files[0])
                        gdf = gpd.read_file(geojson_path)
                        
                        # Convertir à EPSG:4326 si nécessaire
                        if gdf.crs and gdf.crs != "EPSG:4326":
                            gdf = gdf.to_crs("EPSG:4326")
                    else:
                        return {
                            'success': False,
                            'message': "Aucun fichier d'adresses valide trouvé dans l'archive ZIP"
                        }
                    
                finally:
                    # Nettoyer le dossier temporaire
                    shutil.rmtree(temp_dir)
            
            # Traiter les autres formats
            elif file_ext == '.csv':
                # Code pour les CSV
                try:
                    df = pd.read_csv(file_path, 
                                  sep=';',  # Utiliser le point-virgule comme séparateur
                                  on_bad_lines='skip',  # Ignorer les lignes problématiques
                                  dtype=str,  # Tout traiter comme des chaînes
                                  encoding='utf-8-sig')  # Gérer les BOM
                except:
                    # Fallback au cas où on_bad_lines n'est pas disponible (versions pandas plus anciennes)
                    df = pd.read_csv(file_path, 
                                  sep=';', 
                                  error_bad_lines=False, 
                                  warn_bad_lines=True,
                                  dtype=str,
                                  encoding='utf-8-sig')
                
                # Vérifier si les colonnes de géométrie existent
                if 'longitude' in df.columns and 'latitude' in df.columns:
                    # Convertir les colonnes en numérique
                    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
                    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
                    
                    # Créer un GeoDataFrame à partir des coordonnées
                    gdf = gpd.GeoDataFrame(
                        df, 
                        geometry=gpd.points_from_xy(df.longitude, df.latitude),
                        crs="EPSG:4326"
                    )
                elif 'geom' in df.columns:
                    # Filtrer les géométries valides
                    df = df[df['geom'].notna()]
                    try:
                        # Convertir les géométries WKT en objets shapely
                        df['geometry'] = df['geom'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)
                        # Filtrer les lignes avec des géométries valides
                        df = df[df['geometry'].notna()]
                        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
                    except Exception as e:
                        return {
                            'success': False,
                            'message': f"Erreur lors de la conversion des géométries: {str(e)}"
                        }
                else:
                    return {
                        'success': False,
                        'message': "Le fichier CSV ne contient pas de colonnes de géométrie (longitude/latitude ou geom)"
                    }
                    
            elif file_ext in ['.shp', '.geojson']:
                gdf = gpd.read_file(file_path)
                
                # Convertir à EPSG:4326 si nécessaire
                if gdf.crs and gdf.crs != "EPSG:4326":
                    gdf = gdf.to_crs("EPSG:4326")
            else:
                return {
                    'success': False,
                    'message': f"Format de fichier non supporté: {file_ext}"
                }
            
            # Validation des données
            validator = AdresseValidator()
            validation_results = validator.validate_dataframe(gdf)
            
            if not validation_results['valid']:
                return {
                    'success': False,
                    'message': "Validation échouée",
                    'errors': validation_results['errors']
                }
            
            # Préparation des données pour l'insertion
            adresses = []
            for _, row in gdf.iterrows():
                try:
                    adresse = AdresseService._create_adresse_from_row(row)
                    adresses.append(adresse)
                except Exception as e:
                    # Ignorer les lignes qui posent problème
                    continue
            
            # Vérifier si des adresses ont été extraites
            if not adresses:
                return {
                    'success': False,
                    'message': "Aucune adresse valide n'a été extraite du fichier",
                    'errors': ["Format de données non conforme ou données invalides"]
                }
            
            # Insertion en base de données
            try:
                db.session.bulk_save_objects(adresses)
                db.session.commit()
                
                return {
                    'success': True,
                    'message': f"{len(adresses)} adresses importées avec succès",
                    'count': len(adresses)
                }
            except Exception as e:
                db.session.rollback()
                return {
                    'success': False,
                    'message': f"Erreur lors de l'insertion en base: {str(e)}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Erreur lors de l'importation: {str(e)}"
            }
    
    @staticmethod
    def _create_adresse_from_row(row):
        """
        Crée un objet Adresse à partir d'une ligne de DataFrame
        
        Args:
            row: Ligne de DataFrame avec les données d'adresse
            
        Returns:
            Adresse: Instance du modèle Adresse
        """
        adresse = Adresse()
        
        # Mapper les colonnes du DataFrame vers les attributs du modèle
        for column in Adresse.__table__.columns.keys():
            # Cas spécial pour la géométrie
            if column == 'geom':
                if hasattr(row, 'geometry') and row.geometry is not None:
                    adresse.geom = row.geometry.wkt
                continue
                
            # Pour les autres colonnes, vérifier si elles existent dans le DataFrame
            try:
                if hasattr(row, column):
                    value = getattr(row, column)
                elif column in row:
                    value = row[column]
                else:
                    continue  # Colonne non trouvée, passer à la suivante
                
                if pd.isna(value):  # Vérifier si la valeur est NaN
                    value = None
                    
                setattr(adresse, column, value)
            except:
                # En cas d'erreur, passer à la colonne suivante
                continue
        
        return adresse

    @staticmethod
    def get_all_adresses(page=1, per_page=10):
        """
        Récupère toutes les adresses avec pagination
        
        Args:
            page (int): Numéro de page
            per_page (int): Nombre d'éléments par page
            
        Returns:
            Pagination: Objet de pagination contenant les adresses
        """
        return Adresse.query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_adresse_by_code(ad_code):
        """
        Récupère une adresse par son code
        
        Args:
            ad_code (str): Code de l'adresse
            
        Returns:
            Adresse: Instance de l'adresse ou None si non trouvée
        """
        return Adresse.query.get(ad_code)
    
    @staticmethod
    def validate_adresse(adresse):
        """
        Valide une adresse existante
        
        Args:
            adresse (Adresse): Instance de l'adresse à valider
            
        Returns:
            dict: Résultat de la validation
        """
        validator = AdresseValidator()
        return validator.validate_adresse(adresse)
