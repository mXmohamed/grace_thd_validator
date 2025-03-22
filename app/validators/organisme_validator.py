import re
import pandas as pd

class OrganismeValidator:
    """
    Classe pour valider les données d'organismes selon les règles GRACE THD
    """
    
    def __init__(self):
        # Définir les règles de validation
        self.rules = {
            # Champs obligatoires
            'required_fields': ['or_code', 'or_nom', 'or_type'],
            
            # Formats attendus pour certains champs
            'formats': {
                'or_code': {'regex': r'^[A-Za-z0-9_-]{1,20}$', 'message': "Le code de l'organisme doit contenir uniquement des lettres, chiffres, tirets et underscores (max 20 caractères)"},
                'or_siret': {'regex': r'^\d{14}$', 'message': "Le numéro SIRET doit être composé de 14 chiffres"},
                'or_siren': {'regex': r'^\d{9}$', 'message': "Le numéro SIREN doit être composé de 9 chiffres"},
                'or_postal': {'regex': r'^\d{5}$', 'message': "Le code postal doit être composé de 5 chiffres"},
                'or_telfixe': {'regex': r'^[0-9]{10,20}$', 'message': "Le numéro de téléphone fixe doit être composé de 10 à 20 chiffres"},
                'or_mail': {'regex': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', 'message': "Le format de l'adresse email est invalide"},
            }
        }
    
    def validate_dataframe(self, df):
        """
        Valide un DataFrame contenant des organismes
        
        Args:
            df (DataFrame): DataFrame avec les données d'organismes
            
        Returns:
            dict: Résultat de la validation avec statut et erreurs
        """
        errors = []
        
        # Vérifier les champs obligatoires
        for field in self.rules['required_fields']:
            if field not in df.columns:
                errors.append(f"Champ obligatoire manquant: {field}")
            elif df[field].isnull().any():
                missing_count = df[field].isnull().sum()
                errors.append(f"{missing_count} organismes ont une valeur manquante pour le champ: {field}")
        
        # Vérifier les formats
        for field, rule in self.rules['formats'].items():
            if field not in df.columns:
                continue
                
            # Filtrer les lignes non nulles
            non_null_rows = df[~df[field].isnull()]
            
            if 'regex' in rule:
                # Convertir en string pour le regex
                non_null_rows = non_null_rows.copy()
                non_null_rows[field] = non_null_rows[field].astype(str)
                invalid_mask = ~non_null_rows[field].str.match(rule['regex'])
                if invalid_mask.any():
                    invalid_count = invalid_mask.sum()
                    errors.append(f"{invalid_count} organismes ont un format invalide pour {field}: {rule['message']}")
        
        # Vérifier les doublons sur les champs uniques
        for field in ['or_code']:
            if field in df.columns:
                duplicates = df[field].dropna().duplicated()
                if duplicates.any():
                    duplicate_count = duplicates.sum()
                    errors.append(f"{duplicate_count} valeurs en doublon pour le champ unique {field}")
        
        # Résultat de la validation
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_organisme(self, organisme):
        """
        Valide une instance d'organisme
        
        Args:
            organisme: Instance de l'organisme à valider
            
        Returns:
            dict: Résultat de la validation avec statut et erreurs
        """
        errors = []
        
        # Vérifier les champs obligatoires
        for field in self.rules['required_fields']:
            if not hasattr(organisme, field) or getattr(organisme, field) is None:
                errors.append(f"Champ obligatoire manquant: {field}")
        
        # Vérifier les formats
        for field, rule in self.rules['formats'].items():
            if not hasattr(organisme, field) or getattr(organisme, field) is None:
                continue
                
            value = str(getattr(organisme, field))
            
            if 'regex' in rule and not re.match(rule['regex'], value):
                errors.append(f"Format invalide pour {field}: {rule['message']}")
        
        # Résultat de la validation
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
