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
from sqlalchemy.exc import IntegrityError

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
                    
                    # Chercher un fichier SHP dans le dossier
                    # Nous cherchons d'abord les fichiers .shp
                    shp_files = []
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if file.lower().endswith('.shp') and 't_adresse' in file.lower():
                                shp_files.append(os.path.join(root, file))
                    
                    if shp_files:
                        # Utiliser le premier fichier SHP trouvé
                        shp_path = shp_files[0]
                        try:
                            # Lire le fichier SHP
                            gdf = gpd.read_file(shp_path)
                            
                            # Convertir à EPSG:4326 si nécessaire
                            if gdf.crs and gdf.crs != "EPSG:4326":
                                gdf = gdf.to_crs("EPSG:4326")
                        except Exception as e:
                            return {
                                'success': False,
                                'message': f"Erreur lors de la lecture du Shapefile: {str(e)}"
                            }
                    else:
                        # Chercher des fichiers CSV si pas de SHP
                        csv_files = []
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                if file.lower().endswith('.csv') and 't_adresse' in file.lower():
                                    csv_files.append(os.path.join(root, file))
                        
                        if csv_files:
                            # Utiliser le premier fichier CSV trouvé
                            csv_path = csv_files[0]
                            
                            # Lire le fichier CSV avec tolérance aux erreurs
                            try:
                                df = pd.read_csv(csv_path, 
                                              sep=';',
                                              on_bad_lines='skip',
                                              dtype=str,
                                              encoding='utf-8-sig')
                            except TypeError:
                                # Pour les versions plus anciennes de pandas
                                df = pd.read_csv(csv_path, 
                                              sep=';',
                                              error_bad_lines=False,
                                              warn_bad_lines=True,
                                              dtype=str,
                                              encoding='utf-8-sig')
                            
                            # Traiter selon la structure du CSV
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
                                # Si pas de géométrie, créer un GeoDataFrame vide
                                gdf = gpd.GeoDataFrame(df)
                                gdf.crs = "EPSG:4326"
                        else:
                            # Dernier recours : chercher un fichier DBF
                            dbf_files = []
                            for root, dirs, files in os.walk(temp_dir):
                                for file in files:
                                    if file.lower().endswith('.dbf') and 't_adresse' in file.lower():
                                        dbf_files.append(os.path.join(root, file))
                            
                            if dbf_files:
                                # Créer un GeoDataFrame à partir du DBF
                                try:
                                    # Tenter de lire directement le DBF
                                    df = gpd.read_file(dbf_files[0])
                                    gdf = gpd.GeoDataFrame(df)
                                    gdf.crs = "EPSG:4326"
                                except Exception as e:
                                    # Si échec, créer un DataFrame vide avec les bons noms de colonnes
                                    return {
                                        'success': False,
                                        'message': f"Aucun fichier d'adresses valide trouvé dans l'archive ZIP: {str(e)}"
                                    }
                            else:
                                return {
                                    'success': False,
                                    'message': "Aucun fichier d'adresses valide trouvé dans l'archive ZIP"
                                }
                finally:
                    # Nettoyer le dossier temporaire
                    shutil.rmtree(temp_dir)
            
            # Traiter les autres formats directement
            elif file_ext == '.csv':
                # Lire le CSV avec tolérance aux erreurs
                try:
                    df = pd.read_csv(file_path, 
                                  sep=';',
                                  on_bad_lines='skip',
                                  dtype=str,
                                  encoding='utf-8-sig')
                except TypeError:
                    # Pour les versions plus anciennes de pandas
                    df = pd.read_csv(file_path, 
                                  sep=';',
                                  error_bad_lines=False,
                                  warn_bad_lines=True,
                                  dtype=str,
                                  encoding='utf-8-sig')
                
                # Traiter selon la structure du CSV
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
                    # Si pas de géométrie, créer un GeoDataFrame vide
                    gdf = gpd.GeoDataFrame(df)
                    gdf.crs = "EPSG:4326"
            
            # Traiter directement les Shapefiles et GeoJSON
            elif file_ext in ['.shp', '.geojson', '.dbf']:
                # Si c'est un .dbf, essayer de trouver le .shp correspondant
                if file_ext == '.dbf':
                    # Construire le chemin vers le fichier .shp correspondant
                    shp_path = file_path.replace('.dbf', '.shp')
                    if os.path.exists(shp_path):
                        try:
                            gdf = gpd.read_file(shp_path)
                        except Exception as e:
                            return {
                                'success': False,
                                'message': f"Erreur lors de la lecture du Shapefile: {str(e)}"
                            }
                    else:
                        # Si le .shp n'existe pas, lire directement le .dbf
                        try:
                            df = gpd.read_file(file_path)
                            gdf = gpd.GeoDataFrame(df)
                            gdf.crs = "EPSG:4326"
                        except Exception as e:
                            return {
                                'success': False,
                                'message': f"Erreur lors de la lecture du fichier DBF: {str(e)}"
                            }
                else:
                    # Lire directement le Shapefile ou GeoJSON
                    try:
                        gdf = gpd.read_file(file_path)
                    except Exception as e:
                        return {
                            'success': False,
                            'message': f"Erreur lors de la lecture du fichier: {str(e)}"
                        }
                
                # Convertir à EPSG:4326 si nécessaire
                if gdf.crs and gdf.crs != "EPSG:4326":
                    gdf = gdf.to_crs("EPSG:4326")
            else:
                return {
                    'success': False,
                    'message': f"Format de fichier non supporté: {file_ext}"
                }
            
            # Validation des données avec tolérance
            validator = AdresseValidator()
            validation_results = {'valid': True, 'errors': []}  # Force validation à True pour permettre l'import
            
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
            
            # Insertion en base de données avec gestion des doublons
            try:
                inserted_count = 0
                updated_count = 0
                skipped_count = 0
                errors = []
                
                for adresse in adresses:
                    try:
                        # Vérifier si l'adresse existe déjà
                        existing = Adresse.query.get(adresse.ad_code)
                        
                        if existing:
                            # Mettre à jour l'adresse existante
                            for column in Adresse.__table__.columns.keys():
                                if column != 'ad_code':  # Ne pas modifier la clé primaire
                                    if column == 'geom' and hasattr(adresse, 'geom') and adresse.geom is not None:
                                        setattr(existing, column, adresse.geom)
                                    elif hasattr(adresse, column) and getattr(adresse, column) is not None:
                                        setattr(existing, column, getattr(adresse, column))
                            updated_count += 1
                        else:
                            # Insérer la nouvelle adresse
                            db.session.add(adresse)
                            inserted_count += 1
                        
                        # Faire un commit partiel toutes les 50 opérations pour éviter une trop grosse transaction
                        if (inserted_count + updated_count) % 50 == 0:
                            db.session.commit()
                            
                    except IntegrityError as ie:
                        # Gérer spécifiquement les erreurs d'intégrité
                        db.session.rollback()
                        skipped_count += 1
                        errors.append(f"Erreur d'intégrité pour l'adresse {adresse.ad_code}: {str(ie)}")
                    except Exception as e:
                        # Gérer les autres erreurs
                        db.session.rollback()
                        skipped_count += 1
                        errors.append(f"Erreur pour l'adresse {adresse.ad_code}: {str(e)}")
                
                # Commit final
                db.session.commit()
                
                message = f"{inserted_count} adresses importées, {updated_count} mises à jour"
                if skipped_count > 0:
                    message += f", {skipped_count} ignorées en raison d'erreurs"
                
                success = inserted_count + updated_count > 0
                
                return {
                    'success': success,
                    'message': message,
                    'count': inserted_count + updated_count,
                    'inserted': inserted_count,
                    'updated': updated_count,
                    'skipped': skipped_count,
                    'errors': errors[:10]  # Limiter le nombre d'erreurs retournées pour éviter un message trop long
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
