import re
import pandas as pd

class AdresseValidator:
    """
    Classe pour valider les données d'adresse selon les règles GRACE THD
    """
    
    def __init__(self):
        # Définir les règles de validation
        self.rules = {
            # Champs obligatoires
            'required_fields': ['ad_code', 'ad_nomvoie', 'ad_commune', 'ad_insee'],
            
            # Formats attendus pour certains champs
            'formats': {
                'ad_code': {'regex': r'^[A-Za-z0-9_-]{1,254}$', 'message': "Le code d'adresse doit contenir uniquement des lettres, chiffres, tirets et underscores"},
                'ad_insee': {'regex': r'^\d{5}$', 'message': "Le code INSEE doit être composé de 5 chiffres"},
                'ad_postal': {'regex': r'^\d{5}$', 'message': "Le code postal doit être composé de 5 chiffres"},
                'ad_hexacle': {'regex': r'^[A-Za-z0-9]{10}$', 'message': "Le code HEXACLE doit être composé de 10 caractères alphanumériques"},
                'ad_distinf': {'min': 0, 'max': 9999.99, 'message': "La distance doit être comprise entre 0 et 9999.99 mètres"},
            },
            
            # Valeurs permises pour certains champs
            'allowed_values': {
                'ad_raclong': ['0', '1', None],
                'ad_isole': ['0', '1', None],
                'ad_prio': ['0', '1', None],
                'ad_imneuf': ['0', '1', None],
                'ad_iaccgst': ['0', '1', None],
                'ad_dta': ['0', '1', None],
            }
        }
    
    def validate_dataframe(self, gdf):
        """
        Valide un GeoDataFrame contenant des adresses
        
        Args:
            gdf (GeoDataFrame): GeoDataFrame avec les données d'adresse
            
        Returns:
            dict: Résultat de la validation avec statut et erreurs
        """
        errors = []
        
        # Vérifier les champs obligatoires
        for field in self.rules['required_fields']:
            if field not in gdf.columns:
                errors.append(f"Champ obligatoire manquant: {field}")
            elif gdf[field].isnull().any():
                missing_count = gdf[field].isnull().sum()
                errors.append(f"{missing_count} adresses ont une valeur manquante pour le champ: {field}")
        
        # Vérifier les formats
        for field, rule in self.rules['formats'].items():
            if field not in gdf.columns:
                continue
                
            # Filtrer les lignes non nulles
            non_null_rows = gdf[~gdf[field].isnull()]
            
            if 'regex' in rule:
                # Convertir en string pour le regex
                non_null_rows = non_null_rows.copy()
                non_null_rows[field] = non_null_rows[field].astype(str)
                invalid_mask = ~non_null_rows[field].str.match(rule['regex'])
                if invalid_mask.any():
                    invalid_count = invalid_mask.sum()
                    errors.append(f"{invalid_count} adresses ont un format invalide pour {field}: {rule['message']}")
            
            if 'min' in rule and 'max' in rule:
                # Vérifier les valeurs numériques
                try:
                    numeric_vals = pd.to_numeric(non_null_rows[field])
                    invalid_mask = (numeric_vals < rule['min']) | (numeric_vals > rule['max'])
                    if invalid_mask.any():
                        invalid_count = invalid_mask.sum()
                        errors.append(f"{invalid_count} adresses ont une valeur hors limites pour {field}: {rule['message']}")
                except Exception:
                    errors.append(f"Le champ {field} contient des valeurs non numériques")
        
        # Vérifier les valeurs permises
        for field, allowed in self.rules['allowed_values'].items():
            if field in gdf.columns:
                # Convertir en string pour la comparaison
                field_values = gdf[field].astype(str) if not gdf[field].isnull().all() else gdf[field]
                invalid_mask = ~field_values.isin(allowed) & ~gdf[field].isnull()
                if invalid_mask.any():
                    invalid_count = invalid_mask.sum()
                    errors.append(f"{invalid_count} adresses ont des valeurs non autorisées pour {field}. Valeurs autorisées: {', '.join(str(v) for v in allowed if v is not None)}")
        
        # Vérifier les doublons sur les champs uniques
        for field in ['ad_code', 'ad_batcode', 'ad_codtemp']:
            if field in gdf.columns:
                duplicates = gdf[field].dropna().duplicated()
                if duplicates.any():
                    duplicate_count = duplicates.sum()
                    errors.append(f"{duplicate_count} valeurs en doublon pour le champ unique {field}")
        
        # Vérifier les géométries
        if not all(gdf.geometry.is_valid):
            invalid_count = (~gdf.geometry.is_valid).sum()
            errors.append(f"{invalid_count} géométries invalides détectées")
        
        # Résultat de la validation
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_adresse(self, adresse):
        """
        Valide une instance d'adresse
        
        Args:
            adresse: Instance de l'adresse à valider
            
        Returns:
            dict: Résultat de la validation avec statut et erreurs
        """
        errors = []
        
        # Vérifier les champs obligatoires
        for field in self.rules['required_fields']:
            if not hasattr(adresse, field) or getattr(adresse, field) is None:
                errors.append(f"Champ obligatoire manquant: {field}")
        
        # Vérifier les formats
        for field, rule in self.rules['formats'].items():
            if not hasattr(adresse, field) or getattr(adresse, field) is None:
                continue
                
            value = str(getattr(adresse, field))
            
            if 'regex' in rule and not re.match(rule['regex'], value):
                errors.append(f"Format invalide pour {field}: {rule['message']}")
            
            if 'min' in rule and 'max' in rule:
                try:
                    numeric_val = float(value)
                    if numeric_val < rule['min'] or numeric_val > rule['max']:
                        errors.append(f"Valeur hors limites pour {field}: {rule['message']}")
                except ValueError:
                    errors.append(f"Le champ {field} contient une valeur non numérique")
        
        # Vérifier les valeurs permises
        for field, allowed in self.rules['allowed_values'].items():
            if hasattr(adresse, field) and getattr(adresse, field) is not None:
                value = getattr(adresse, field)
                if value not in allowed:
                    errors.append(f"Valeur non autorisée pour {field}: {value}. Valeurs autorisées: {', '.join(str(v) for v in allowed if v is not None)}")
        
        # Résultat de la validation
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }