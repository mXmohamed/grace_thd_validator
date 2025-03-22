from app import db
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import NUMERIC

class Adresse(db.Model):
    __tablename__ = 't_adresse'
    __table_args__ = {'schema': 'gracethd_commun'}
    
    # Colonnes de base
    ad_code = db.Column(db.String(254), primary_key=True, 
                       comment="Code unique de l'adresse")
    ad_raclong = db.Column(db.String(1),
                          comment="Défini si l'entité est raccordable en longueur (0/1)")
    ad_datmodi = db.Column(db.DateTime,
                          comment="Date de dernière mise à jour de l'adresse")
    ad_nomvoie = db.Column(db.String(254),
                          comment="Nom de la voie")
    ad_numero = db.Column(db.Integer,
                         comment="Numéro éventuel de l'adresse dans la voie")
    ad_rep = db.Column(db.String(20),
                      comment="Indice de répétition associé au numéro (Bis, A, 1...)")
    ad_insee = db.Column(db.String(6),
                        comment="Identifiant INSEE de la commune")
    ad_postal = db.Column(db.String(20),
                         comment="Code postal du bureau de distribution de la voie")
    ad_commune = db.Column(db.String(254),
                          comment="Nom officiel de la commune")
    ad_hexacle = db.Column(db.String(254),
                          comment="Code HEXACLE")
    ad_distinf = db.Column(NUMERIC(6, 2),
                          comment="Distance en mètres de raccordement")
    ad_isole = db.Column(db.String(1),
                        comment="Pour distinguer les locaux isolés (1) ou non (0)")
    ad_prio = db.Column(db.String(1),
                       comment="Le raccordement est-il prioritaire (1) ou non (0)")
    ad_racc = db.Column(db.String(2),
                       comment="Type de raccordement du site")
    ad_batcode = db.Column(db.String(100), unique=True,
                          comment="Identifiant du bâtiment dans une base externe")
    ad_codtemp = db.Column(db.String(254), unique=True,
                          comment="Code temporaire avant création de l'ad_batcode")
    ad_nombat = db.Column(db.String(254),
                         comment="Nom du batiment tel que décrit par l'opérateur")
    ad_ietat = db.Column(db.String(2),
                        comment="Avancement du déploiement")
    ad_imneuf = db.Column(db.String(1),
                         comment="S'il s'agit d'un habitat en cours de construction (1) ou non (0)")
    ad_gest = db.Column(db.String(254),
                       comment="Gestionnaire d'immeuble")
    ad_idatsgn = db.Column(db.DateTime,
                          comment="Date de signature de la convention avec le gestionnaire")
    ad_iaccgst = db.Column(db.String(1),
                          comment="Accord gestionnaire nécessaire (1) ou non (0)")
    
    # Colonnes pour nombre de locaux
    ad_nblres = db.Column(db.Integer,
                         comment="Nombre de locaux résidentiels")
    ad_nblpro = db.Column(db.Integer,
                         comment="Nombre de locaux professionnels")
    ad_nblent = db.Column(db.Integer,
                         comment="Nombre de locaux d'entreprises éligibles à une offre spécifique")
    ad_nblpub = db.Column(db.Integer,
                         comment="Nombre de locaux exploités par des services publics")
    ad_nblobj = db.Column(db.Integer,
                         comment="Nombre de locaux de type objet connectés")
    ad_nblope = db.Column(db.Integer,
                         comment="Nombre de locaux exploités par des opérateurs télécoms")
    
    # Colonnes pour nombre de fibres
    ad_nbfotte = db.Column(db.Integer,
                          comment="Nombre de fibres FTTE")
    ad_nbfogfu = db.Column(db.Integer,
                          comment="Nombre de fibres GFU")
    ad_nbfotto = db.Column(db.Integer,
                          comment="Nombre de fibres FTTO")
    ad_nbfotth = db.Column(db.Integer,
                          comment="Nombre de fibres FTTH")
    ad_nbfofon = db.Column(db.Integer,
                          comment="Nombre de fibres noires")
    
    # Autres informations
    ad_dta = db.Column(db.String(1),
                      comment="1 si Diagnostic Technique Amiante obligatoire, 0 sinon")
    geom = db.Column(Geometry(geometry_type='POINT', srid=4326),
                    comment="Point abstrait (géométrie)")
    
    # Informations complémentaires
    ad_ban_id = db.Column(db.String(24),
                         comment="Identifiant Base Adresse Nationale")
    ad_fantoir = db.Column(db.String(10),
                          comment="Identifiant FANTOIR")
    ad_alias = db.Column(db.String(254),
                        comment="Nom en langue régionale ou autre appellation différente")
    ad_nom_ld = db.Column(db.String(254),
                         comment="Nom du lieu-dit")
    ad_x_ban = db.Column(db.Numeric,
                        comment="X en lambert 93")
    ad_y_ban = db.Column(db.Numeric,
                        comment="Y en lambert 93")
    ad_section = db.Column(db.String(5),
                          comment="Section cadastrale")
    ad_idpar = db.Column(db.String(20),
                        comment="Identifiant de la parcelle de référence")
    ad_x_parc = db.Column(db.Numeric,
                         comment="X en lambert 93 de la parcelle de référence")
    ad_y_parc = db.Column(db.Numeric,
                         comment="Y en lambert 93 de la parcelle de référence")
    ad_nat = db.Column(db.String(1),
                      comment="Oui si le site n'est pas une propriété privée")
    ad_rivoli = db.Column(db.String(254),
                         comment="Code RIVOLI")
    ad_hexaclv = db.Column(db.String(254),
                          comment="Code HEXACLE Voie")
    ad_itypeim = db.Column(db.String(1),
                          comment="Type d'immeuble (IPE)")
    ad_idatimn = db.Column(db.DateTime,
                          comment="Date prévisionnelle de livraison de l'immeuble")
    ad_prop = db.Column(db.String(254),
                       comment="Propriétaire de l'immeuble")
    ad_idatcab = db.Column(db.DateTime,
                          comment="Date prévisionnelle de câblage de l'adresse")
    ad_idatcom = db.Column(db.Date,
                          comment="Date d'ouverture à la commercialisation")
    ad_typzone = db.Column(db.String(1),
                          comment="Type de zone de l'adresse desservie")
    
    # Méta-données
    ad_comment = db.Column(db.String(254),
                          comment="Commentaire")
    ad_geolqlt = db.Column(NUMERIC(6, 2),
                          comment="Précision du positionnement en mètres")
    ad_geolmod = db.Column(db.String(4),
                          comment="Mode d'implantation de l'objet")
    ad_geolsrc = db.Column(db.String(254),
                          comment="Source de la géolocalisation")
    ad_creadat = db.Column(db.DateTime,
                          comment="Date de création de l'objet en base")
    ad_majdate = db.Column(db.DateTime,
                          comment="Date de mise à jour de l'objet en base")
    ad_majsrc = db.Column(db.String(254),
                         comment="Source utilisée pour la mise à jour")
    ad_abddate = db.Column(db.DateTime,
                          comment="Date d'abandon de l'objet")
    ad_abdsrc = db.Column(db.String(254),
                         comment="Cause de l'abandon de l'objet")
    ad_sracdem = db.Column(db.String(1),
                          comment="Adresse susceptible d'être raccordable sur demande")
    
    def __repr__(self):
        return f'<Adresse {self.ad_code}: {self.ad_numero} {self.ad_rep} {self.ad_nomvoie}, {self.ad_commune}>'