// Popup functionality for the Homepage Companion extension
document.addEventListener('DOMContentLoaded', async () => {
    const toggle = document.getElementById('redirectToggle') as HTMLElement;

    if (!toggle) {
        console.error('Toggle element not found');
        return;
    }

    // Load current setting
    try {
        const result = await chrome.storage.sync.get(['newTabRedirect']);
        const config = result.newTabRedirect || { enabled: true };

        // Set initial toggle state
        if (config.enabled) {
            toggle.classList.add('active');
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }

    // Handle toggle click
    toggle.addEventListener('click', async () => {
        try {
            const isActive = toggle.classList.contains('active');
            const newState = !isActive;

            // Update storage
            await chrome.storage.sync.set({
                newTabRedirect: {
                    enabled: newState,
                    homepageUrl: 'http://localhost:3000'
                }
            });

            // Update UI
            if (newState) {
                toggle.classList.add('active');
            } else {
                toggle.classList.remove('active');
            }

            console.log('New tab redirect setting updated:', newState);
        } catch (error) {
            console.error('Error updating setting:', error);
        }
    });
});
