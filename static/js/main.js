// Main JavaScript file for Aurora Motors

document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Mobile Navigation Toggle
    const navbarToggle = document.getElementById('navbarToggle');
    const navbarMenu = document.getElementById('navbarMenu');
    
    if (navbarToggle) {
        navbarToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('active');
            // Animate hamburger menu
            this.classList.toggle('active');
        });
    }
    
    // Handle dropdown menus on mobile
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        if (toggle) {
            toggle.addEventListener('click', function(e) {
                if (window.innerWidth <= 768) {
                    e.preventDefault();
                    dropdown.classList.toggle('active');
                }
            });
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });
    
    // Alert Dismissal
    const closeButtons = document.querySelectorAll('.alert .close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            alert.style.display = 'none';
        });
    });
    
    // Form Validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    
                    // Show error message
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('span');
                        errorMsg.classList.add('error-message');
                        errorMsg.style.color = 'red';
                        errorMsg.style.fontSize = '0.875rem';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                    errorMsg.textContent = 'This field is required';
                } else {
                    field.classList.remove('error');
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
    
    // Date Picker Enhancement
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Set min date to today
        if (input.dataset.minToday === 'true') {
            const today = new Date().toISOString().split('T')[0];
            input.min = today;
        }
    });
    
    // Price Calculator for Bookings
    const pickupDate = document.getElementById('pickup_date');
    const returnDate = document.getElementById('return_date');
    const priceDisplay = document.getElementById('price_display');
    const dailyRate = document.getElementById('daily_rate');
    
    if (pickupDate && returnDate && priceDisplay && dailyRate) {
        function calculatePrice() {
            if (pickupDate.value && returnDate.value) {
                const start = new Date(pickupDate.value);
                const end = new Date(returnDate.value);
                const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
                
                if (days > 0) {
                    const rate = parseFloat(dailyRate.value) || 0;
                    const subtotal = days * rate;
                    const tax = subtotal * 0.1;
                    const total = subtotal + tax;
                    
                    priceDisplay.innerHTML = `
                        <div class="price-breakdown">
                            <div>Days: ${days}</div>
                            <div>Daily Rate: $${rate.toFixed(2)}</div>
                            <div>Subtotal: $${subtotal.toFixed(2)}</div>
                            <div>Tax (10%): $${tax.toFixed(2)}</div>
                            <div class="total"><strong>Total: $${total.toFixed(2)}</strong></div>
                        </div>
                    `;
                }
            }
        }
        
        pickupDate.addEventListener('change', calculatePrice);
        returnDate.addEventListener('change', calculatePrice);
    }
    
    // Image Gallery
    const galleryImages = document.querySelectorAll('.gallery-image');
    const mainImage = document.getElementById('main-image');
    
    galleryImages.forEach(img => {
        img.addEventListener('click', function() {
            if (mainImage) {
                mainImage.src = this.src;
                
                // Update active state
                galleryImages.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });
    
    // Smooth Scroll
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Search Functionality
    const searchInput = document.getElementById('search');
    const searchButton = document.getElementById('searchButton');
    
    if (searchInput && searchButton) {
        searchButton.addEventListener('click', function() {
            const searchTerm = searchInput.value.trim();
            if (searchTerm) {
                window.location.href = `?search=${encodeURIComponent(searchTerm)}`;
            }
        });
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchButton.click();
            }
        });
    }
    
    // Confirmation Dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // Dynamic Status Badge Colors
    const statusBadges = document.querySelectorAll('.status-badge');
    statusBadges.forEach(badge => {
        const status = badge.textContent.toLowerCase();
        switch(status) {
            case 'available':
                badge.style.backgroundColor = '#10b981';
                break;
            case 'booked':
                badge.style.backgroundColor = '#f59e0b';
                break;
            case 'maintenance':
                badge.style.backgroundColor = '#ef4444';
                break;
            case 'completed':
                badge.style.backgroundColor = '#3b82f6';
                break;
            case 'pending':
                badge.style.backgroundColor = '#6b7280';
                break;
        }
        badge.style.color = 'white';
        badge.style.padding = '0.25rem 0.75rem';
        badge.style.borderRadius = '0.375rem';
        badge.style.fontSize = '0.875rem';
        badge.style.fontWeight = '500';
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 500);
        }, 5000);
    });
    
    // Tab Navigation
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // Update active states
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Show/hide content
            tabContents.forEach(content => {
                if (content.id === targetTab) {
                    content.style.display = 'block';
                } else {
                    content.style.display = 'none';
                }
            });
        });
    });
    
    // Print functionality
    const printButtons = document.querySelectorAll('.print-button');
    printButtons.forEach(button => {
        button.addEventListener('click', function() {
            window.print();
        });
    });
});

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Export functions for use in other scripts
window.AuroraMotors = {
    formatCurrency,
    formatDate
};