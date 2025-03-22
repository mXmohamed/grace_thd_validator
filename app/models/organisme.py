from app import db

class Organisme(db.Model):
    __tablename__ = 't_organisme'
    __table_args__ = {'schema': 'gracethd_commun'}
    
    # Colonnes principales
    or_code = db.Column(db.String(20), primary_key=True, 
                       comment="Code de l'organisme")
    or_nom = db.Column(db.String(254),
                       comment="Nom de l'opérateur, de la collectivité, de l'entreprise, etc.")
    or_type = db.Column(db.String(254),
                       comment="Classification juridique. Littéral ou nomenclature INSEE")
    or_siret = db.Column(db.String(14),
                       comment="Numéro SIRET dans le cas d'un établissement (sens INSEE, base SIRENE)")
    or_nomvoie = db.Column(db.String(254),
                         comment="Nom de la voie")
    or_numero = db.Column(db.Integer,
                        comment="Numéro éventuel de l'adresse dans la voie")
    or_rep = db.Column(db.String(20),
                      comment="Indice de répétition associé au numéro (par exemple Bis, A, 1…)")
    or_local = db.Column(db.String(254),
                        comment="Complément d'adresse pour identifier le local")
    or_postal = db.Column(db.String(20),
                        comment="Code postal du bureau de distribution de la voie")
    or_commune = db.Column(db.String(254),
                          comment="Nom officiel de la commune")
    or_siren = db.Column(db.String(9),
                        comment="Numéro SIREN de l'opérateur, de la collectivité, …")
    or_activ = db.Column(db.String(254),
                        comment="Activité principale exercée. Littéral ou Code NAF")
    or_l331 = db.Column(db.String(254),
                      comment="Code court selon liste opérateurs L33-1 (téléchargeable sur le site de l'ARCEP)")
    or_nometab = db.Column(db.String(254),
                          comment="Nom de l'établissement, de l'agence (sens INSEE, base SIRENE)")
    or_ad_code = db.Column(db.String(254),
                          comment="Identifiant de l'adresse dans la table t_adresse")
    or_telfixe = db.Column(db.String(20),
                          comment="Téléphone fixe")
    or_mail = db.Column(db.String(254),
                       comment="Mail de contact générique")
    or_comment = db.Column(db.String(254),
                          comment="Commentaire")
    
    # Méta-données
    or_creadat = db.Column(db.DateTime,
                          comment="Date de création de l'objet en base")
    or_majdate = db.Column(db.DateTime,
                          comment="Date de la mise à jour de l'objet en base")
    or_majsrc = db.Column(db.String(254),
                         comment="Source utilisée pour la mise à jour")
    or_abddate = db.Column(db.DateTime,
                          comment="Date d'abandon de l'objet")
    or_abdsrc = db.Column(db.String(254),
                         comment="Cause de l'abandon de l'objet")
    
    def __repr__(self):
        return f'<Organisme {self.or_code}: {self.or_nom}>'
