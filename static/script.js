// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {

    // ====================
    // Rating Modal Logic
    // ====================
    const modal = document.getElementById('ratingModalWrapper');
    const openBtn = document.getElementById('openRatingBtn');

    // Only proceed if both elements exist (important for pages without the modal)
    if (modal && openBtn) {
        // Open modal
        openBtn.addEventListener('click', function () {
            modal.style.display = 'flex';
        });

        // Close modal when clicking Cancel button
        const cancelBtn = modal.querySelector('.btn-secondary');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', function () {
                modal.style.display = 'none';
            });
        }

        // Close modal when clicking outside the content
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }


    // ====================
    // Hamburger Menu Logic (Improved)
    // ====================
    const menuToggle = document.getElementById('menuToggle');
    const dropdownMenu = document.getElementById('dropdownMenu');

    if (menuToggle && dropdownMenu) {
        menuToggle.addEventListener('click', function (e) {
            e.stopPropagation(); // Prevent the document click handler from closing it immediately

            // Toggle visibility
            const isOpen = dropdownMenu.style.display === 'block';
            dropdownMenu.style.display = isOpen ? 'none' : 'block';

            // Add/remove 'active' class for smooth "X" animation
            if (isOpen) {
                menuToggle.classList.remove('active');
            } else {
                menuToggle.classList.add('active');
            }
        });

        // Close menu when clicking anywhere outside
        document.addEventListener('click', function (e) {
            if (!menuToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownMenu.style.display = 'none';
                menuToggle.classList.remove('active');
            }
        });

        // Optional: Close menu on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && dropdownMenu.style.display === 'block') {
                dropdownMenu.style.display = 'none';
                menuToggle.classList.remove('active');
            }
        });
    }
});