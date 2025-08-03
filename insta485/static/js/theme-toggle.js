// Safe-Transaction Theme Toggle Utility
// Handles light/dark theme switching with smooth transitions

class ThemeManager {
  constructor() {
    this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
    this.init();
  }

  init() {
    // Apply the theme immediately to prevent flash
    this.applyTheme(this.currentTheme);
    
    // Add smooth transition after initial load
    setTimeout(() => {
      document.documentElement.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    }, 100);

    // Listen for system theme changes
    this.listenForSystemThemeChanges();
    
    // Create theme toggle button if it doesn't exist
    this.createThemeToggle();
  }

  getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  getStoredTheme() {
    return localStorage.getItem('safe-transaction-theme');
  }

  setStoredTheme(theme) {
    if (theme === 'auto') {
      localStorage.removeItem('safe-transaction-theme');
    } else {
      localStorage.setItem('safe-transaction-theme', theme);
    }
  }

  applyTheme(theme) {
    const root = document.documentElement;
    
    // Remove existing theme attributes
    root.removeAttribute('data-theme');
    
    if (theme === 'dark') {
      root.setAttribute('data-theme', 'dark');
    } else if (theme === 'light') {
      root.setAttribute('data-theme', 'light');
    }
    // If theme is 'auto', let CSS media queries handle it
    
    this.currentTheme = theme;
    this.updateToggleButton();
    this.announceThemeChange(theme);
  }

  toggleTheme() {
    const themes = ['light', 'dark', 'auto'];
    const currentIndex = themes.indexOf(this.currentTheme);
    const nextTheme = themes[(currentIndex + 1) % themes.length];
    
    this.setTheme(nextTheme);
  }

  setTheme(theme) {
    this.setStoredTheme(theme);
    this.applyTheme(theme);
    
    // Dispatch custom event for other components to listen to
    window.dispatchEvent(new CustomEvent('themeChanged', {
      detail: { theme }
    }));
  }

  listenForSystemThemeChanges() {
    window.matchMedia('(prefers-color-scheme: dark)').addListener((e) => {
      if (this.currentTheme === 'auto') {
        this.applyTheme('auto');
      }
    });
  }

  createThemeToggle() {
    // Only create if doesn't exist
    if (document.getElementById('theme-toggle')) return;

    const toggle = document.createElement('button');
    toggle.id = 'theme-toggle';
    toggle.className = 'theme-toggle btn btn-ghost';
    toggle.setAttribute('aria-label', 'Toggle theme');
    toggle.innerHTML = this.getToggleIcon();
    
    toggle.addEventListener('click', () => this.toggleTheme());
    
    // Try to add to navbar, fallback to body
    const navbar = document.querySelector('.navbar-content, .header, nav');
    if (navbar) {
      navbar.appendChild(toggle);
    } else {
      document.body.appendChild(toggle);
    }
  }

  getToggleIcon() {
    const icons = {
      light: '<i class="fas fa-sun"></i>',
      dark: '<i class="fas fa-moon"></i>',
      auto: '<i class="fas fa-adjust"></i>'
    };
    return icons[this.currentTheme] || icons.auto;
  }

  updateToggleButton() {
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
      toggle.innerHTML = this.getToggleIcon();
      toggle.setAttribute('title', `Current theme: ${this.currentTheme}`);
    }
  }

  announceThemeChange(theme) {
    // Screen reader announcement
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = `Theme changed to ${theme}`;
    
    document.body.appendChild(announcement);
    setTimeout(() => document.body.removeChild(announcement), 1000);
  }

  // Public API methods
  getCurrentTheme() {
    return this.currentTheme;
  }

  getEffectiveTheme() {
    if (this.currentTheme === 'auto') {
      return this.getSystemTheme();
    }
    return this.currentTheme;
  }
}

// Theme Toggle Button Styles
const themeToggleStyles = `
.theme-toggle {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: all var(--transition-normal);
  background: var(--bg-tertiary);
  border: 2px solid var(--border-light);
  color: var(--text-secondary);
}

.theme-toggle:hover {
  background: var(--brand-primary-50);
  border-color: var(--brand-primary-500);
  color: var(--brand-primary-600);
  transform: var(--hover-scale);
}

.theme-toggle:active {
  transform: var(--active-scale);
}

.theme-toggle i {
  transition: transform var(--transition-normal);
}

.theme-toggle:hover i {
  transform: rotate(180deg);
}

/* Screen reader only class */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Animation for theme transitions */
* {
  transition: background-color var(--transition-normal), 
              color var(--transition-normal), 
              border-color var(--transition-normal),
              box-shadow var(--transition-normal);
}
`;

// Trust-focused animations for important actions
const trustAnimations = `
/* Trust-building micro-interactions */
.btn-primary {
  position: relative;
  overflow: hidden;
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.btn-primary:hover::before {
  left: 100%;
}

/* Security badge pulse */
.security-badge,
.verified-badge {
  animation: security-pulse 2s ease-in-out infinite;
}

@keyframes security-pulse {
  0%, 100% { 
    box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.4);
  }
  50% { 
    box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
  }
}

/* Success celebration */
.success-celebration {
  animation: success-celebrate 0.6s ease-out;
}

@keyframes success-celebrate {
  0% { transform: scale(1); }
  25% { transform: scale(1.1) rotate(5deg); }
  50% { transform: scale(1.1) rotate(-5deg); }
  75% { transform: scale(1.05) rotate(2deg); }
  100% { transform: scale(1) rotate(0deg); }
}

/* Warning shake */
.warning-shake {
  animation: warning-shake 0.5s ease-in-out;
}

@keyframes warning-shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
`;

// Initialize theme manager when DOM is ready
function initializeTheme() {
  // Add styles to head
  const styleSheet = document.createElement('style');
  styleSheet.textContent = themeToggleStyles + trustAnimations;
  document.head.appendChild(styleSheet);
  
  // Initialize theme manager
  window.themeManager = new ThemeManager();
  
  // Add utility functions to window for easy access
  window.setTheme = (theme) => window.themeManager.setTheme(theme);
  window.toggleTheme = () => window.themeManager.toggleTheme();
  window.getCurrentTheme = () => window.themeManager.getCurrentTheme();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeTheme);
} else {
  initializeTheme();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ThemeManager, initializeTheme };
} 