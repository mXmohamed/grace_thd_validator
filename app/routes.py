import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from app.services.adresse_service import AdresseService
from app.services.organisme_service import OrganismeService
from app.services.import_service import ImportService
from app.services.export_service import ExportService

bp = Blueprint('main', __name__)

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'csv', 'shp', 'geojson', 'zip'}

@bp.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

# Route d'importation unifiée avec génération de rapport
@bp.route('/import', methods=['GET', 'POST'])
def import_data():
    """Importation et validation de données depuis un fichier ZIP avec génération de rapport"""
    if request.method == 'POST':
        # Vérifier si un fichier a été soumis
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Si l'utilisateur ne sélectionne pas de fichier
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'danger')
            return redirect(request.url)
        
        # Vérifier si le fichier est autorisé
        if file and allowed_file(file.filename):
            # Sauvegarder le fichier
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Importer les données
            result = ImportService.import_from_file(file_path)
            
            # Générer le rapport de validation
            export_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reports')
            report_path = ExportService.generate_validation_report(result, export_dir)
            report_filename = os.path.basename(report_path)
            
            # Supprimer le fichier d'import temporaire
            os.remove(file_path)
            
            # Gérer le résultat
            if result['success']:
                flash(result['message'], 'success')
                
                # Ajouter des messages pour chaque table
                for table_result in result.get('tables', []):
                    status_class = 'success' if table_result.get('success') else 'warning'
                    flash(f"Table {table_result.get('table')}: {table_result.get('message')}", status_class)
                
                # Rediriger vers la page d'importation avec le nom du fichier de rapport
                return render_template('import_data.html', report_file=report_filename)
            else:
                flash(result['message'], 'danger')
                
                # Ajouter des messages pour chaque table
                for table_result in result.get('tables', []):
                    if not table_result.get('success'):
                        flash(f"Table {table_result.get('table')}: {table_result.get('message')}", 'warning')
                        
                        # Afficher les erreurs détaillées
                        for error in table_result.get('errors', []):
                            flash(error, 'danger')
                
                # Même en cas d'erreur, on propose le téléchargement du rapport
                return render_template('import_data.html', report_file=report_filename)
        else:
            flash('Type de fichier non autorisé. Formats acceptés : ZIP', 'danger')
            return redirect(request.url)
    
    # Afficher le formulaire d'importation
    return render_template('import_data.html')

# Route pour télécharger le rapport de validation
@bp.route('/download-report/<filename>')
def download_report(filename):
    """Téléchargement du rapport de validation"""
    reports_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reports')
    return send_from_directory(reports_dir, filename, as_attachment=True)

# Routes pour la visualisation des adresses
@bp.route('/adresses')
def adresses():
    """Liste des adresses avec pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    adresses = AdresseService.get_all_adresses(page, per_page)
    return render_template('adresse.html', adresses=adresses)

@bp.route('/adresses/<string:ad_code>')
def view_adresse(ad_code):
    """Affiche les détails d'une adresse"""
    adresse = AdresseService.get_adresse_by_code(ad_code)
    if adresse is None:
        flash('Adresse non trouvée', 'danger')
        return redirect(url_for('main.adresses'))
    return render_template('view_adresse.html', adresse=adresse)

@bp.route('/adresses/<string:ad_code>/validate')
def validate_adresse(ad_code):
    """Valide une adresse spécifique"""
    adresse = AdresseService.get_adresse_by_code(ad_code)
    if adresse is None:
        return jsonify({'success': False, 'message': 'Adresse non trouvée'})
    
    result = AdresseService.validate_adresse(adresse)
    return jsonify({
        'success': result['valid'],
        'message': 'Validation réussie' if result['valid'] else 'Validation échouée',
        'errors': result.get('errors', [])
    })

# Routes pour la visualisation des organismes
@bp.route('/organismes')
def organismes():
    """Liste des organismes avec pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    organismes = OrganismeService.get_all_organismes(page, per_page)
    return render_template('organisme.html', organismes=organismes)

@bp.route('/organismes/<string:or_code>')
def view_organisme(or_code):
    """Affiche les détails d'un organisme"""
    organisme = OrganismeService.get_organisme_by_code(or_code)
    if organisme is None:
        flash('Organisme non trouvé', 'danger')
        return redirect(url_for('main.organismes'))
    return render_template('view_organisme.html', organisme=organisme)

@bp.route('/organismes/<string:or_code>/validate')
def validate_organisme(or_code):
    """Valide un organisme spécifique"""
    organisme = OrganismeService.get_organisme_by_code(or_code)
    if organisme is None:
        return jsonify({'success': False, 'message': 'Organisme non trouvé'})
    
    result = OrganismeService.validate_organisme(organisme)
    return jsonify({
        'success': result['valid'],
        'message': 'Validation réussie' if result['valid'] else 'Validation échouée',
        'errors': result.get('errors', [])
    })

# API Routes
@bp.route('/api/adresses', methods=['GET'])
def api_adresses():
    """API pour récupérer la liste des adresses"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = AdresseService.get_all_adresses(page, per_page)
    adresses = pagination.items
    
    # Convertir les adresses en dictionnaire
    adresses_dict = []
    for adresse in adresses:
        adresse_dict = {
            'ad_code': adresse.ad_code,
            'ad_nomvoie': adresse.ad_nomvoie,
            'ad_numero': adresse.ad_numero,
            'ad_rep': adresse.ad_rep,
            'ad_commune': adresse.ad_commune,
            'ad_postal': adresse.ad_postal,
            'ad_insee': adresse.ad_insee
        }
        adresses_dict.append(adresse_dict)
    
    return jsonify({
        'adresses': adresses_dict,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })

@bp.route('/api/adresses/<string:ad_code>', methods=['GET'])
def api_adresse(ad_code):
    """API pour récupérer les détails d'une adresse"""
    adresse = AdresseService.get_adresse_by_code(ad_code)
    if adresse is None:
        return jsonify({'success': False, 'message': 'Adresse non trouvée'}), 404
    
    # Convertir l'adresse en dictionnaire (sans la géométrie)
    adresse_dict = {}
    for column in adresse.__table__.columns.keys():
        if column != 'geom':
            adresse_dict[column] = getattr(adresse, column)
    
    return jsonify({
        'success': True,
        'adresse': adresse_dict
    })

@bp.route('/api/organismes', methods=['GET'])
def api_organismes():
    """API pour récupérer la liste des organismes"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = OrganismeService.get_all_organismes(page, per_page)
    organismes = pagination.items
    
    # Convertir les organismes en dictionnaire
    organismes_dict = []
    for organisme in organismes:
        organisme_dict = {
            'or_code': organisme.or_code,
            'or_nom': organisme.or_nom,
            'or_type': organisme.or_type,
            'or_siret': organisme.or_siret,
            'or_commune': organisme.or_commune,
            'or_postal': organisme.or_postal
        }
        organismes_dict.append(organisme_dict)
    
    return jsonify({
        'organismes': organismes_dict,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })

@bp.route('/api/organismes/<string:or_code>', methods=['GET'])
def api_organisme(or_code):
    """API pour récupérer les détails d'un organisme"""
    organisme = OrganismeService.get_organisme_by_code(or_code)
    if organisme is None:
        return jsonify({'success': False, 'message': 'Organisme non trouvé'}), 404
    
    # Convertir l'organisme en dictionnaire
    organisme_dict = {}
    for column in organisme.__table__.columns.keys():
        organisme_dict[column] = getattr(organisme, column)
    
    return jsonify({
        'success': True,
        'organisme': organisme_dict
    })

@bp.route('/api/import', methods=['POST'])
def api_import_data():
    """API pour importer des données et générer un rapport"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nom de fichier vide'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Importer les données
        result = ImportService.import_from_file(file_path)
        
        # Générer le rapport de validation
        export_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reports')
        report_path = ExportService.generate_validation_report(result, export_dir)
        report_filename = os.path.basename(report_path)
        
        # Supprimer le fichier d'import temporaire
        os.remove(file_path)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'tables': result.get('tables', []),
                'report_url': url_for('main.download_report', filename=report_filename, _external=True)
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message'],
                'tables': result.get('tables', []),
                'report_url': url_for('main.download_report', filename=report_filename, _external=True)
            }), 400
    else:
        return jsonify({
            'success': False,
            'message': 'Type de fichier non autorisé. Formats acceptés : ZIP'
        }), 400
