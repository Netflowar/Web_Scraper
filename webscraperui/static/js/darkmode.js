// Dark Mode functionality for Web Scraper Pro
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved dark mode preference
    const darkModeEnabled = localStorage.getItem('darkMode') === 'true';
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    // Initialize dark mode if previously enabled
    if (darkModeEnabled) {
        document.body.classList.add('dark-mode');
    }
    
    // Handle dark mode toggle click
    if (darkModeToggle) {
        // Update toggle appearance based on current state
        updateToggleAppearance(darkModeEnabled);
        
        darkModeToggle.addEventListener('click', function() {
            // Toggle dark mode class on body
            document.body.classList.toggle('dark-mode');
            
            // Get the current state after toggling
            const isDarkMode = document.body.classList.contains('dark-mode');
            
            // Save preference to localStorage
            localStorage.setItem('darkMode', isDarkMode);
            
            // Update toggle appearance
            updateToggleAppearance(isDarkMode);
        });
    }
    
    // Helper function to update toggle appearance
    function updateToggleAppearance(isDarkMode) {
        if (!darkModeToggle) return;
        
        const sunIcon = darkModeToggle.querySelector('.fa-sun');
        const moonIcon = darkModeToggle.querySelector('.fa-moon');
        
        if (isDarkMode) {
            if (sunIcon) sunIcon.style.opacity = '1';
            if (moonIcon) moonIcon.style.opacity = '0.5';
        } else {
            if (sunIcon) sunIcon.style.opacity = '0.5';
            if (moonIcon) moonIcon.style.opacity = '1';
        }
    }
});
