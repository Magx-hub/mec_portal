        // Mobile-optimized JavaScript
        let touchStartY = 0;
        let touchEndY = 0;
        
        // Auto-hide toast messages
        document.addEventListener('DOMContentLoaded', function() {
            const toasts = document.querySelectorAll('.toast-message');
            toasts.forEach(toast => {
                setTimeout(() => {
                    toast.classList.add('toast-exit');
                    setTimeout(() => toast.remove(), 300);
                }, 5000);
            });
        });
        
        // Toggle functions
        function toggleQuickActions() {
            const overlay = document.getElementById('quick-actions-overlay');
            overlay.classList.toggle('hidden');
        }
        
        function toggleUserMenu() {
            const overlay = document.getElementById('user-menu-overlay');
            overlay.classList.toggle('hidden');
        }
        
        function toggleNotifications() {
            // Implement notification functionality
            console.log('Toggle notifications');
        }
        
        // Show/hide loading indicator
        function showLoading() {
            document.getElementById('loading-indicator').classList.remove('hidden');
        }
        
        function hideLoading() {
            document.getElementById('loading-indicator').classList.add('hidden');
        }
        
        // Add loading to form submissions and navigation
        document.addEventListener('click', function(e) {
            if (e.target.tagName === 'A' && e.target.href && !e.target.href.includes('#')) {
                showLoading();
            }
        });
        
        // Handle back button
        window.addEventListener('popstate', function(e) {
            hideLoading();
        });
        
        // Pull to refresh simulation
        let isRefreshing = false;
        
        document.addEventListener('touchstart', function(e) {
            touchStartY = e.changedTouches[0].screenY;
        });
        
        document.addEventListener('touchend', function(e) {
            touchEndY = e.changedTouches[0].screenY;
            handleSwipe();
        });
        
        function handleSwipe() {
            if (touchEndY - touchStartY > 100 && window.scrollY === 0 && !isRefreshing) {
                isRefreshing = true;
                // Simulate refresh
                showToast('Refreshing...', 'info');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            }
        }
        
        // Toast function
        function showToast(message, type = 'info') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `toast-message p-4 rounded-lg shadow-lg flex items-center space-x-3 toast-enter ${
                type === 'success' ? 'bg-green-500 text-white' :
                type === 'error' ? 'bg-red-500 text-white' :
                type === 'warning' ? 'bg-yellow-500 text-white' :
                'bg-blue-500 text-white'
            }`;
            
            toast.innerHTML = `
                <i class="fas ${
                    type === 'success' ? 'fa-check-circle' :
                    type === 'error' ? 'fa-exclamation-circle' :
                    type === 'warning' ? 'fa-exclamation-triangle' :
                    'fa-info-circle'
                }"></i>
                <span class="flex-1 text-sm">${message}</span>
                <i class="fas fa-times text-sm opacity-70"></i>
            `;
            
            toast.onclick = () => toast.remove();
            container.appendChild(toast);
            
            // Trigger animation
            setTimeout(() => toast.classList.add('toast-enter-active'), 10);
            
            // Auto remove
            setTimeout(() => {
                toast.classList.add('toast-exit');
                setTimeout(() => toast.remove(), 300);
            }, 5000);
        }
        
        // Close overlays when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('#quick-actions-overlay') && !e.target.closest('[onclick*="toggleQuickActions"]')) {
                document.getElementById('quick-actions-overlay').classList.add('hidden');
            }
            if (!e.target.closest('#user-menu-overlay') && !e.target.closest('[onclick*="toggleUserMenu"]')) {
                document.getElementById('user-menu-overlay').classList.add('hidden');
            }
        });
        
        // PWA Installation
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            showInstallButton();
        });
        
        function showInstallButton() {
            // Show install button in UI
            const installBtn = document.createElement('button');
            installBtn.textContent = 'Install App';
            installBtn.className = 'fixed bottom-24 right-4 bg-blue-600 text-white px-4 py-2 rounded-full shadow-lg text-sm z-40';
            installBtn.onclick = installApp;
            document.body.appendChild(installBtn);
            
            setTimeout(() => installBtn.remove(), 10000); // Auto-hide after 10s
        }
        
        function installApp() {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((result) => {
                    if (result.outcome === 'accepted') {
                        console.log('PWA installed');
                    }
                    deferredPrompt = null;
                });
            }
        }
        
        // Register service worker
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/static/js/sw.js')
                    .then(registration => console.log('SW registered'))
                    .catch(error => console.log('SW registration failed'));
            });
        }
