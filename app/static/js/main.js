// Script principal pour l'application GRACE THD Validator

// Fermer automatiquement les alertes après 5 secondes
document.addEventListener('DOMContentLoaded', function() {
    // Récupérer toutes les alertes avec classe .alert
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    // Fermer automatiquement après 5 secondes
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Utiliser Bootstrap pour fermer l'alerte
            $(alert).fadeOut('slow', function() {
                $(this).remove();
            });
        }, 5000);
    });
});

// Confirmer les actions de suppression
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.btn-delete');
    
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
                e.preventDefault();
            }
        });
    });
});

// Fonction utilitaire pour formater les dates
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    
    return date.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// Fonction utilitaire pour tronquer un texte
function truncateText(text, maxLength = 100) {
    if (!text || text.length <= maxLength) return text;
    
    return text.substring(0, maxLength) + '...';
}