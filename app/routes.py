import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename
from app.services.adresse_service import AdresseService

bp = Blueprint('main', __name__)

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'csv', 'shp', 'geojson', 'zip'}

@bp.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@bp.route('/adresses')
def adresses():
    """Liste des adresses avec pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    adresses = AdresseService.get_all_adresses(page, per_page)
    return render_template('adresse.html', adresses=adresses)

@bp.route('/adresses/import', methods=['GET', 'POST'])
def import_adresses():
    """Importation d'adresses depuis un fichier"""
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
            
            # Importer les adresses
            result = AdresseService.import_from_file(file_path)
            
            # Supprimer le fichier temporaire
            os.remove(file_path)
            
            # Gérer le résultat
            if result['success']:
                flash(result['message'], 'success')
                return redirect(url_for('main.adresses'))
            else:
                if 'errors' in result:
                    # Afficher la liste des erreurs
                    for error in result['errors']:
                        flash(error, 'danger')
                else:
                    flash(result['message'], 'danger')
                return redirect(request.url)
        else:
            flash('Type de fichier non autorisé. Formats acceptés : CSV, SHP, GeoJSON, ZIP', 'danger')
            return redirect(request.url)
    
    # Afficher le formulaire d'importation
    return render_template('import.html')

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

@bp.route('/api/import/adresses', methods=['POST'])
def api_import_adresses():
    """API pour importer des adresses"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nom de fichier vide'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        result = AdresseService.import_from_file(file_path)
        
        os.remove(file_path)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    else:
        return jsonify({
            'success': False,
            'message': 'Type de fichier non autorisé. Formats acceptés : CSV, SHP, GeoJSON, ZIP'
        }), 400