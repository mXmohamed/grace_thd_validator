from app import create_app, db
from app.models.adresse import Adresse

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Configure les objets disponibles dans le shell Flask"""
    return {'db': db, 'Adresse': Adresse}

if __name__ == '__main__':
    app.run(debug=True)
