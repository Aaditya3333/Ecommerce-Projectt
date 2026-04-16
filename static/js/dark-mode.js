// Dark Mode Functionality
class DarkModeManager {
    constructor() {
        this.isDarkMode = this.loadDarkMode();
        this.init();
    }

    init() {
        // Apply dark mode on page load
        if (this.isDarkMode) {
            this.enableDarkMode();
        }

        // Add event listeners
        this.setupEventListeners();
        
        // Update toggle button
        this.updateToggleButton();
    }

    setupEventListeners() {
        const darkModeToggle = document.getElementById('darkModeToggle');
        if (darkModeToggle) {
            darkModeToggle.addEventListener('click', () => {
                this.toggleDarkMode();
            });
        }

        // Listen for system dark mode changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (e.matches && !this.isDarkMode) {
                    this.enableDarkMode();
                } else if (!e.matches && this.isDarkMode) {
                    this.disableDarkMode();
                }
            });
        }
    }

    toggleDarkMode() {
        if (this.isDarkMode) {
            this.disableDarkMode();
        } else {
            this.enableDarkMode();
        }
        this.saveDarkModePreference();
        this.updateToggleButton();
    }

    enableDarkMode() {
        document.body.classList.add('dark-mode');
        this.isDarkMode = true;
        this.updateThemeColorMeta('#1a1a1a');
    }

    disableDarkMode() {
        document.body.classList.remove('dark-mode');
        this.isDarkMode = false;
        this.updateThemeColorMeta('#ffffff');
    }

    updateToggleButton() {
        const icon = document.getElementById('darkModeIcon');
        if (icon) {
            if (this.isDarkMode) {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
                icon.title = 'Switch to Light Mode';
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
                icon.title = 'Switch to Dark Mode';
            }
        }
    }

    updateThemeColorMeta(color) {
        // Update theme color meta tag for mobile browsers
        let themeColorMeta = document.querySelector('meta[name="theme-color"]');
        if (!themeColorMeta) {
            themeColorMeta = document.createElement('meta');
            themeColorMeta.name = 'theme-color';
            document.head.appendChild(themeColorMeta);
        }
        themeColorMeta.content = color;
    }

    saveDarkModePreference() {
        localStorage.setItem('darkMode', this.isDarkMode);
        
        // Also save as cookie for server-side detection
        document.cookie = `darkMode=${this.isDarkMode}; path=/; max-age=31536000; SameSite=Lax`;
    }

    loadDarkMode() {
        // Check localStorage first
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode !== null) {
            return savedDarkMode === 'true';
        }

        // Check cookie as fallback
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'darkMode') {
                return value === 'true';
            }
        }

        // Check system preference
        if (window.matchMedia) {
            return window.matchMedia('(prefers-color-scheme: dark)').matches;
        }

        return false;
    }

    // Auto-detect based on time of day
    autoDetectDarkMode() {
        const hour = new Date().getHours();
        const isNightTime = hour >= 18 || hour < 6; // 6 PM to 6 AM
        
        if (isNightTime && !this.isDarkMode) {
            this.enableDarkMode();
            this.saveDarkModePreference();
        } else if (!isNightTime && this.isDarkMode) {
            this.disableDarkMode();
            this.saveDarkModePreference();
        }
    }

    // Get current dark mode status
    isDarkModeEnabled() {
        return this.isDarkMode;
    }

    // Apply dark mode to specific elements
    applyDarkModeToElements() {
        // Apply dark mode to dynamically created elements
        const elements = document.querySelectorAll('.dynamic-content');
        elements.forEach(element => {
            if (this.isDarkMode) {
                element.classList.add('dark-mode-element');
            } else {
                element.classList.remove('dark-mode-element');
            }
        });
    }
}

// Initialize dark mode when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.darkModeManager = new DarkModeManager();
    
    // Optional: Auto-detect based on time (comment out if not wanted)
    // window.darkModeManager.autoDetectDarkMode();
});

// Export for global access
window.toggleDarkMode = () => {
    if (window.darkModeManager) {
        window.darkModeManager.toggleDarkMode();
    }
};

window.enableDarkMode = () => {
    if (window.darkModeManager) {
        window.darkModeManager.enableDarkMode();
    }
};

window.disableDarkMode = () => {
    if (window.darkModeManager) {
        window.darkModeManager.disableDarkMode();
    }
};
