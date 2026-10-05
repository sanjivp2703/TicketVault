/*
 * Seller dashboard (templates/index.html).
 * Moved verbatim from the inline script. handleCreateListing() stays inline in
 * the template because it needs the signed-in email from Jinja.
 */
        // Global ticket verification functions
        window.markTicketIncorrect = function(transactionId) {
            if (confirm('Are you sure the ticket sent was incorrect? This will cancel the transaction.')) {
                fetch('/api/ticket-verification', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        transaction_id: transactionId,
                        action: 'incorrect'
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Transaction marked as incorrect and cancelled.');
                        location.reload();
                    } else {
                        alert('Error: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error processing request');
                });
            }
        };

        window.markTicketCorrect = function(transactionId) {
            if (confirm('Are you sure the ticket sent was correct? This will proceed to payment processing.')) {
                fetch('/api/ticket-verification', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        transaction_id: transactionId,
                        action: 'correct'
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Ticket confirmed as correct. Proceeding to payment.');
                        location.reload();
            } else {
                        alert('Error: ' + data.error);
            }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error processing request');
                });
            }
        };

        window.testTicketSent = function(transactionId) {
            if (confirm('Confirm that you have sent the ticket to Safe Transaction at the email address shown above. The transaction will move to the next step.')) {
                const button = event.target.closest('button');
                if (button) {
                    button.disabled = true;
                    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                }

                fetch('/api/test-ticket-sent', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        transaction_id: transactionId,
                        test_mode: true
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ Ticket confirmed as sent!\n\nThe transaction will now proceed to the next step.');
                        location.reload();
                    } else {
                        alert('Error: ' + (data.error || 'Unable to process request'));
                        if (button) {
                            button.disabled = false;
                            button.innerHTML = '<i class="fas fa-check-circle"></i> I\'ve Sent the Ticket';
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error processing request. Please try again.');
                    if (button) {
                        button.disabled = false;
                        button.innerHTML = '<i class="fas fa-check-circle"></i> I\'ve Sent the Ticket';
                    }
                });
            }
        };

        // Test payment function - opens Stripe checkout directly
        window.testBuyerPayment = function(transactionId) {
            if (confirm('🧪 TEST MODE: This will open the Stripe payment page that the buyer sees. Continue?')) {
                console.log('🎯 Opening Stripe checkout for transaction:', transactionId);
                
                const button = event.target.closest('button');
                if (button) {
                    button.disabled = true;
                    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Opening Stripe...';
                }
                
                // Call the API to get Stripe checkout URL and redirect directly
                fetch('/api/transactions/' + transactionId + '/pay', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.checkout_url) {
                        console.log('🎯 Redirecting to Stripe checkout:', data.checkout_url);
                        window.location.href = data.checkout_url;
                    } else {
                        alert('Error creating payment session: ' + (data.error || 'Unknown error'));
                        if (button) {
                            button.disabled = false;
                            button.innerHTML = '<i class="fas fa-credit-card"></i> TEST: Go to Buyer Payment Page';
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error opening payment page');
                    if (button) {
                        button.disabled = false;
                        button.innerHTML = '<i class="fas fa-credit-card"></i> TEST: Go to Buyer Payment Page';
                    }
                });
            }
        };



        // Send "Ticket Sent" Email function
        window.sendTicketSentEmail = function(transactionId) {
            if (confirm('Send "Ticket Sent" notification email to the buyer?\n\nThis will send a professional email notifying the buyer that their tickets have been sent.')) {
                const button = event.target.closest('button');
                if (button) {
                    button.disabled = true;
                    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
                }
                
                fetch('/send-ticket-sent-email/' + transactionId, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (button) {
                        button.disabled = false;
                        button.innerHTML = '<i class="fas fa-envelope"></i> Send "Ticket Sent" Email';
                    }
                    
                    if (data.success) {
                        alert('✅ Email sent successfully!\n\nThe buyer has been notified that their tickets have been sent.');
                    } else {
                        alert('❌ Failed to send email: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    if (button) {
                        button.disabled = false;
                        button.innerHTML = '<i class="fas fa-envelope"></i> Send "Ticket Sent" Email';
                    }
                    alert('❌ Network error. Please try again.');
                });
            }
        };

        // Toggle finished listing details dropdown
        window.toggleFinishedDetails = function(transactionId) {
            const detailsDiv = document.getElementById(`details-${transactionId}`);
            const chevron = document.getElementById(`chevron-${transactionId}`);
            const toggle = chevron.parentElement;
            
            if (detailsDiv.style.display === 'none' || detailsDiv.style.display === '') {
                detailsDiv.style.display = 'block';
                toggle.classList.add('active');
                chevron.style.transform = 'rotate(180deg)';
            } else {
                detailsDiv.style.display = 'none';
                toggle.classList.remove('active');
                chevron.style.transform = 'rotate(0deg)';
            }
        };
        
        // SIMPLE GLOBAL SCROLL FUNCTION - GUARANTEED TO WORK
        function simpleScroll() {
            console.log('🚀 SIMPLE SCROLL TRIGGERED!');
            
            // Try multiple scroll methods for maximum compatibility
            const scrollDistance = window.innerHeight * 0.8;
            
            // Method 1: window.scrollBy
            window.scrollBy(0, scrollDistance);
            
            // Method 2: document.documentElement.scrollTop
            document.documentElement.scrollTop += scrollDistance;
            
            // Method 3: document.body.scrollTop (for older browsers)
            document.body.scrollTop += scrollDistance;
            
            // Visual feedback
            const btn = document.getElementById('scrollCatalyst');
            if (btn) {
                btn.style.transform = 'scale(1.1)';
                btn.style.background = 'linear-gradient(135deg, #10b981, #34d399)';
                setTimeout(() => {
                    btn.style.transform = '';
                    btn.style.background = '';
                }, 500);
            }
            
            console.log('📍 Scrolled by:', scrollDistance, 'pixels');
        }













    // Welcome Modal Functions - Global scope for onclick handlers
    window.closeWelcomeModal = function() {
        const overlay = document.getElementById('welcomeOverlay');
        if (overlay) {
            overlay.style.opacity = '0';
            overlay.style.transform = 'scale(0.9)';
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 300);
            // Mark as seen for this session when manually closed
            sessionStorage.setItem('hasSeenIntroductionThisSession', 'true');
            console.log('📝 Introduction marked as seen for this session (manually closed)');
        }
    }

    // How It Works Modal Functions - Global scope for onclick handlers
    window.openHowItWorksModal = function() {
        try {
            console.log('🎯 Opening How It Works modal...');
            console.log('Function called successfully!');
            
            // First close the welcome modal
            if (typeof window.closeWelcomeModal === 'function') {
                console.log('Closing welcome modal first...');
                window.closeWelcomeModal();
            } else {
                console.log('No welcome modal to close');
            }
            
            // Then open the how it works modal after a brief delay
            setTimeout(() => {
                const overlay = document.getElementById('howItWorksOverlay');
                if (overlay) {
                    console.log('Found howItWorksOverlay, opening modal...');
                    overlay.style.display = 'flex';
                    overlay.style.opacity = '1';
                    overlay.style.transform = 'scale(1)';
                    
                    // Reset to first step
                    const modal = overlay.querySelector('.how-it-works-modal');
                    if (modal) {
                        currentStep = 1;
                    
                    // Initialize step navigation after modal is visible
                    setTimeout(() => {
                        console.log('Initializing modal navigation...');
                        
                                                 // Force show first step content and hide others
                        const modal = document.getElementById('howItWorksOverlay');
                        const allSections = modal ? modal.querySelectorAll('.step-section') : document.querySelectorAll('.step-section');
                        console.log('Found step sections:', allSections.length);
                        
                         allSections.forEach((section, index) => {
                             if (index === 0) {
                                 section.classList.add('active');
                                section.style.opacity = '1';
                                section.style.transform = 'translateX(0)';
                                section.style.pointerEvents = 'auto';
                                section.style.zIndex = '10';
                                console.log('First step section activated with inline styles');
                             } else {
                                 section.classList.remove('active');
                             }
                         });
                        
                        activateStepInTracker(1);
                        updateNavigationButtons();
                        setupStepNavigation(); // Ensure navigation is set up
                        console.log('Modal opened, navigation ready');
                    }, 300);
                }
            }
        }, 400);
        } catch (error) {
            console.error('Error opening How It Works modal:', error);
        }
    }

    window.closeHowItWorksModal = function() {
        console.log('🔄 Closing How It Works modal...');
        const overlay = document.getElementById('howItWorksOverlay');
        if (overlay) {
            overlay.style.opacity = '0';
            overlay.style.transform = 'scale(0.9)';
            setTimeout(() => {
                overlay.style.display = 'none';
                console.log('✅ How It Works modal closed');
            }, 300);
        } else {
            console.error('❌ Could not find howItWorksOverlay element');
        }
        
        // Reset step navigation
        currentStep = 1;
    }

    function showWelcomeModal() {
        // Check if we should show the modal based on navigation type
        const hasSeenIntroThisSession = sessionStorage.getItem('hasSeenIntroductionThisSession');
        const navigationEntry = performance.getEntriesByType('navigation')[0];
        const navigationType = navigationEntry ? navigationEntry.type : 'navigate';
        
        console.log('🔍 Navigation type:', navigationType);
        console.log('🔍 Has seen intro this session:', hasSeenIntroThisSession);
        
        // Show modal for:
        // 1. Fresh navigations (typing URL, bookmarks, links from other sites)
        // 2. First time in this session (login, new browser session)
        const shouldShow = (
            !hasSeenIntroThisSession ||  // First time this session
            navigationType === 'navigate'  // Fresh navigation (not reload)
        ) && navigationType !== 'reload';  // But never on reload
        
        if (shouldShow) {
            console.log('🎉 Showing introduction modal (fresh visit or login)');
        const overlay = document.getElementById('welcomeOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
                // Mark as seen for this session
                sessionStorage.setItem('hasSeenIntroductionThisSession', 'true');
            }
        } else {
            console.log('✅ Skipping modal - page reload or already seen this session');
        }
    }

    // Setup click-outside-to-close functionality
    function setupWelcomeModalEvents() {
        const overlay = document.getElementById('welcomeOverlay');
        const modal = overlay?.querySelector('.welcome-modal');
        
        if (overlay && modal) {
            // Close modal when clicking on overlay background
            overlay.addEventListener('click', function(e) {
                if (e.target === overlay) {
                    window.closeWelcomeModal();
                }
            });
            
            // Prevent modal from closing when clicking inside the modal content
            modal.addEventListener('click', function(e) {
                e.stopPropagation();
            });
            
            // Setup "See How It Works" button as backup
            const howItWorksButton = modal.querySelector('.start-button');
            if (howItWorksButton) {
                howItWorksButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('How It Works button clicked via event listener');
                    if (typeof window.openHowItWorksModal === 'function') {
                        window.openHowItWorksModal();
                    }
                });
            }
        }
    }

    function setupHowItWorksModalEvents() {
        const overlay = document.getElementById('howItWorksOverlay');
        const modal = overlay?.querySelector('.welcome-modal');
        
        if (overlay && modal) {
            // Close modal when clicking on overlay background
            overlay.addEventListener('click', function(e) {
                if (e.target === overlay) {
                    window.closeHowItWorksModal();
                }
            });
            
            // Prevent modal from closing when clicking inside the modal content
            modal.addEventListener('click', function(e) {
                e.stopPropagation();
            });

            // Setup step navigation with delay to ensure elements are rendered
            setTimeout(() => {
                setupStepNavigation();
            }, 100);
        }
    }

    // Current step tracking - declare globally
    let currentStep = 1;
    const totalSteps = 6;

    function setupStepNavigation() {
        const stepSections = document.querySelectorAll('.step-section');
        const trackerSteps = document.querySelectorAll('.tracker-step');
        
        if (!stepSections.length || !trackerSteps.length) return;

        // Initially activate first step
        activateStepInTracker(1);
        updateNavigationButtons();

        // Add click handlers to tracker steps
        trackerSteps.forEach((step, index) => {
            step.addEventListener('click', () => {
                const stepNumber = index + 1;
                navigateToStep(stepNumber);
            });
        });
    }

    window.navigateStep = function(direction) {
        const newStep = currentStep + direction;
        
        // Check bounds
        if (newStep >= 1 && newStep <= totalSteps) {
            navigateToStep(newStep);
        }
    }

    function navigateToStep(stepNumber) {
        if (stepNumber === currentStep) return; // Already on this step
        
        currentStep = stepNumber;
        activateStepInTracker(stepNumber);
        updateNavigationButtons();
        
        console.log('Navigating to step:', stepNumber);
    }

    function updateNavigationButtons() {
        // Update step navigation arrow buttons
        const stepPrevButton = document.getElementById('stepNavPrev');
        const stepNextButton = document.getElementById('stepNavNext');
        
        if (stepPrevButton && stepNextButton) {
            stepPrevButton.disabled = currentStep === 1;
            stepNextButton.disabled = currentStep === totalSteps;
        }
        
        // Update progress dots
        const progressDots = document.querySelectorAll('.progress-dot');
        progressDots.forEach((dot, index) => {
            dot.classList.remove('active');
            if (index + 1 === currentStep) {
                dot.classList.add('active');
            }
        });
        
        // Legacy navigation buttons (if they exist)
        const prevButton = document.getElementById('prevButton');
        const nextButton = document.getElementById('nextButton');
        
        console.log('Updating navigation buttons, currentStep:', currentStep);
        console.log('Found buttons:', { prev: !!prevButton, next: !!nextButton });
        
        if (prevButton && nextButton) {
            // Update button states
            prevButton.disabled = currentStep === 1;
            nextButton.disabled = currentStep === totalSteps;
            
            // Update button labels with step info
            const prevLabel = prevButton.querySelector('.nav-label');
            const nextLabel = nextButton.querySelector('.nav-label');
            
            console.log('Found labels:', { prevLabel: !!prevLabel, nextLabel: !!nextLabel });
            
            if (prevLabel && currentStep > 1) {
                prevLabel.textContent = `Step ${currentStep - 1}`;
            } else if (prevLabel) {
                prevLabel.textContent = 'Previous';
            }
            
            if (nextLabel && currentStep < totalSteps) {
                nextLabel.textContent = `Step ${currentStep + 1}`;
            } else if (nextLabel) {
                nextLabel.textContent = 'Next';
            }
            
            console.log('Navigation buttons updated successfully');
        } else {
            console.log('Navigation buttons not found!');
        }
    }

    // New step navigation functions
    window.previousStep = function() {
        if (currentStep > 1) {
            navigateToStep(currentStep - 1);
        }
    }

    window.nextStep = function() {
        if (currentStep < totalSteps) {
            navigateToStep(currentStep + 1);
        }
    }

    window.goToStepDot = function(stepNumber) {
        if (stepNumber >= 1 && stepNumber <= totalSteps) {
            navigateToStep(stepNumber);
        }
    }

    function activateStepInTracker(stepNumber) {
        console.log('Activating step:', stepNumber);
        
        // Update tracker highlighting with requestAnimationFrame for smooth transitions
        requestAnimationFrame(() => {
            const trackerSteps = document.querySelectorAll('.tracker-step');
            const stepSections = document.querySelectorAll('.step-section');
            
            console.log('Found', trackerSteps.length, 'tracker steps and', stepSections.length, 'step sections');
            
            // First, remove active class from ALL elements
            trackerSteps.forEach(step => step.classList.remove('active'));
            stepSections.forEach(section => section.classList.remove('active'));
            
            // Then add active class to the target elements
            trackerSteps.forEach((step, index) => {
                if (index + 1 === stepNumber) {
                    step.classList.add('active');
                    console.log('Activated tracker step', index + 1);
                }
            });

            // Update step section visibility - using data-step attribute for more reliable selection
            const targetSection = document.querySelector(`.step-section[data-step="${stepNumber}"]`);
            if (targetSection) {
                targetSection.classList.add('active');
                console.log('Activated step section', stepNumber, targetSection);
            } else {
                // Fallback to index-based selection
                stepSections.forEach((section, index) => {
                    if (index + 1 === stepNumber) {
                        section.classList.add('active');
                        console.log('Activated step section by index', index + 1, section);
                    }
                });
            }
        });
    }



    // Helper function to reset introduction flag (for testing)
    window.resetIntroduction = function() {
        sessionStorage.removeItem('hasSeenIntroductionThisSession');
        console.log('🔄 Introduction flag reset - will show on next fresh navigation');
    }

    // Initialize everything when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 DOM Content Loaded - Setting up modals...');
        console.log('💡 Tip: To reset introduction popup, run: resetIntroduction()');
        
        // Setup modal events (close on outside click)
        setupWelcomeModalEvents();
        setupHowItWorksModalEvents();
        
        // Setup "See How It Works" button as backup event listener
        const howItWorksButtons = document.querySelectorAll('button[onclick*="openHowItWorksModal"]');
        console.log('Found', howItWorksButtons.length, 'How It Works buttons');
        
        howItWorksButtons.forEach((button, index) => {
            console.log(`Setting up button ${index + 1}:`, button);
            button.addEventListener('click', function(e) {
                console.log('🎯 How It Works button clicked via event listener!');
                e.preventDefault();
                if (typeof window.openHowItWorksModal === 'function') {
                    window.openHowItWorksModal();
                } else {
                    console.error('openHowItWorksModal function not found!');
                }
            });
        });
        
        // Show welcome modal for first-time users
        showWelcomeModal();
        

        
        // Simple initialization - just visual effects, no click handlers
        const catalyst = document.getElementById('scrollCatalyst');
        if (catalyst) {
            console.log('✅ Scroll catalyst found and ready for inline onclick!');
            
            // Just add visual effects
            catalyst.addEventListener('mouseenter', function() {
                catalyst.style.transform = 'translateZ(40px) translateY(-15px) rotateX(15deg) rotateY(10deg) scale(1.1)';
            });
            
            catalyst.addEventListener('mouseleave', function() {
                catalyst.style.transform = '';
            });
        }
        
        // Setup step navigation progress dots click handlers
        const progressDots = document.querySelectorAll('.progress-dot');
        progressDots.forEach((dot, index) => {
            dot.addEventListener('click', function() {
                const stepNumber = parseInt(this.getAttribute('data-step'));
                if (stepNumber && stepNumber >= 1 && stepNumber <= totalSteps) {
                    navigateToStep(stepNumber);
                }
            });
        });
        
        // Setup keyboard navigation for step cards
        document.addEventListener('keydown', function(e) {
            // Only handle keyboard navigation when the How It Works modal is open
            const howItWorksModal = document.getElementById('howItWorksOverlay');
            if (howItWorksModal && howItWorksModal.style.display !== 'none') {
                if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                    e.preventDefault();
                    if (e.key === 'ArrowLeft' && currentStep > 1) {
                        previousStep();
                    } else if (e.key === 'ArrowRight' && currentStep < totalSteps) {
                        nextStep();
                    }
                }
            }
        });
    });



    // Add additional animations
    const additionalStyles = document.createElement('style');
    additionalStyles.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        @keyframes wallHitShake {
            0% { transform: translate(0, 0); }
            20% { transform: translate(-5px, 0); }
            40% { transform: translate(5px, 0); }
            60% { transform: translate(-3px, 0); }
            80% { transform: translate(3px, 0); }
            100% { transform: translate(0, 0); }
        }
    `;
    document.head.appendChild(additionalStyles);

    // Ultra-Modern Creative Scroll Catalyst
    function initializeScrollCatalyst() {
        const scrollCatalyst = document.getElementById('scrollCatalyst');
        if (!scrollCatalyst) {
            console.error('❌ ScrollCatalyst element not found!');
                return;
            }
            
        let isVisible = true;
        let isAnimating = false;

        console.log('🚀 Scroll Catalyst initialized!', scrollCatalyst); // Debug log
        console.log('🎯 Element position:', scrollCatalyst.getBoundingClientRect()); // Debug log

        // Smart visibility based on scroll position
        function updateCatalystVisibility() {
            const heroHeight = document.querySelector('.hero-section')?.offsetHeight || 600;
            const scrollPosition = window.scrollY;
            const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPercentage = scrollPosition / documentHeight;

            // Hide when user is at the bottom of the page (90% scrolled)
            if (scrollPercentage > 0.9) {
                if (isVisible) {
                    scrollCatalyst.classList.add('hidden');
                    isVisible = false;
                }
                    } else {
                if (!isVisible) {
                    scrollCatalyst.classList.remove('hidden');
                    isVisible = true;
                }
            }
        }

        // Simplified and guaranteed scroll function
        function scrollToNextSection() {
            if (isAnimating) return;
            isAnimating = true;

            console.log('🎯 Scroll catalyst clicked!'); // Debug log
            console.log('📍 Current scroll position:', window.scrollY); // Debug log

            // Add success transformation
            scrollCatalyst.classList.add('success');

            // Simple, reliable scroll logic
            const currentScroll = window.scrollY;
            const viewportHeight = window.innerHeight;
            let targetScroll;

            // Always scroll down by one viewport, or to specific sections
            if (currentScroll < 100) {
                // At very top - scroll to after hero
                targetScroll = viewportHeight * 0.8;
            } else {
                // Anywhere else - scroll down one viewport
                targetScroll = currentScroll + (viewportHeight * 0.8);
            }

            // Ensure we don't scroll past the bottom
            const maxScroll = document.documentElement.scrollHeight - viewportHeight;
            targetScroll = Math.min(targetScroll, maxScroll);

            console.log('📍 Scrolling from', currentScroll, 'to', targetScroll); // Debug log

            // Force scroll with both methods for maximum compatibility
            try {
                window.scrollTo({
                    top: targetScroll,
                    behavior: 'smooth'
                });
            } catch (e) {
                // Fallback for older browsers
                window.scrollTo(0, targetScroll);
            }

            // Also try alternative scroll method
            document.documentElement.scrollTop = targetScroll;

            // Reset state with visual feedback
            setTimeout(() => {
                scrollCatalyst.classList.remove('success');
                isAnimating = false;
            }, 800);
        }

        // Enhanced touch/swipe support
        let touchStartY = 0;
        let touchStartTime = 0;

        function handleTouchStart(e) {
            touchStartY = e.touches[0].clientY;
            touchStartTime = Date.now();
            console.log('👆 Touch start detected'); // Debug log
        }

        function handleTouchEnd(e) {
            const touchEndY = e.changedTouches[0].clientY;
            const touchEndTime = Date.now();
            const deltaY = touchEndY - touchStartY;
            const deltaTime = touchEndTime - touchStartTime;

            console.log('👆 Touch end - deltaY:', deltaY, 'deltaTime:', deltaTime); // Debug log

            // Detect downward swipe (faster than 600ms, more than 20px down)
            if (deltaY > 20 && deltaTime < 600) {
                e.preventDefault();
                scrollToNextSection();
            }
        }

        // DIRECT SIMPLE CLICK HANDLER
        scrollCatalyst.onclick = function(e) {
            console.log('🖱️ DIRECT ONCLICK TRIGGERED!');
            console.log('🎯 Event target:', e.target);
            e.preventDefault();
            
            // IMMEDIATE SCROLL ACTION
            console.log('📍 Attempting to scroll NOW...');
            const scrollAmount = window.innerHeight * 0.8;
            console.log('📍 Scroll amount:', scrollAmount);
            
            window.scrollBy({
                top: scrollAmount,
                behavior: 'smooth'
            });
            
            // Visual feedback
            scrollCatalyst.classList.add('success');
            setTimeout(() => {
                scrollCatalyst.classList.remove('success');
            }, 800);
        };

        // ALSO TRY addEventListener as backup
        scrollCatalyst.addEventListener('click', function(e) {
            console.log('🖱️ ADDEVENTLISTENER TRIGGERED!');
            e.preventDefault();
            window.scrollBy(0, window.innerHeight * 0.8);
        });

        scrollCatalyst.addEventListener('touchstart', handleTouchStart, { passive: false });
        scrollCatalyst.addEventListener('touchend', handleTouchEnd, { passive: false });

        // Scroll listener for visibility
        window.addEventListener('scroll', updateCatalystVisibility);
        
        // Initial visibility check
        updateCatalystVisibility();

        // Enhanced keyboard accessibility
        scrollCatalyst.addEventListener('keydown', (e) => {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                console.log('⌨️ Keyboard trigger'); // Debug log
                scrollToNextSection();
            }
        });

        // Make it fully accessible
        scrollCatalyst.setAttribute('tabindex', '0');
        scrollCatalyst.setAttribute('role', 'button');
        scrollCatalyst.setAttribute('aria-label', 'Scroll to next section - Creative navigation catalyst');
        scrollCatalyst.style.outline = 'none'; // Custom focus styling via CSS

        console.log('✅ Scroll Catalyst fully initialized with enhanced features!'); // Debug log
    }



    // Event Search Autocomplete - Reusable function
    function initializeEventAutocomplete(suffix = '') {
        const eventNameInput = document.getElementById('event_name' + suffix);
        const eventLocationInput = document.getElementById('event_location' + suffix);
        const eventDatetimeInput = document.getElementById('event_datetime' + suffix);
        const suggestionsContainer = document.getElementById('event_suggestions' + suffix);
        const eventDetailsContainer = document.getElementById('event_details_container' + suffix);
        const eventLocationDisplay = document.getElementById('event_location_display' + suffix);
        const eventDatetimeDisplay = document.getElementById('event_datetime_display' + suffix);
        
        // Find venue and datetime cards within the appropriate form
        let venueCard, datetimeCard;
        if (suffix) {
            // For bottom form, find cards within that specific form
            const bottomForm = document.getElementById('createListingFormBottom');
            if (bottomForm) {
                venueCard = bottomForm.querySelector('.venue-card');
                datetimeCard = bottomForm.querySelector('.datetime-card');
            }
        } else {
            // For create listing form, find cards within that specific form
            const createForm = document.getElementById('createListingFormBottom');
            if (createForm) {
                venueCard = createForm.querySelector('.venue-card');
                datetimeCard = createForm.querySelector('.datetime-card');
            }
        }

        if (!eventNameInput || !suggestionsContainer) return;

        let searchTimeout;

        eventNameInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            // Hide event details if user is changing the event name
            if (eventDetailsContainer && eventDetailsContainer.classList.contains('show')) {
                eventDetailsContainer.classList.remove('show');
                setTimeout(() => {
                    eventDetailsContainer.style.display = 'none';
                }, 300);
                
                // Remove populated classes
                if (venueCard) venueCard.classList.remove('populated');
                if (datetimeCard) datetimeCard.classList.remove('populated');
                
                // Clear hidden inputs
                if (eventLocationInput) eventLocationInput.value = '';
                if (eventDatetimeInput) eventDatetimeInput.value = '';
            }
            
            if (query.length < 2) {
                suggestionsContainer.style.display = 'none';
                return;
            }

            searchTimeout = setTimeout(() => {
                // Get current school selection
                const schoolInput = document.getElementById('selected_school');
                const school = schoolInput ? schoolInput.value : 'michigan';
                
                fetch(`/api/events?q=${encodeURIComponent(query)}&school=${encodeURIComponent(school)}`)
                    .then(response => response.json())
                    .then(events => {
                        if (events.length > 0) {
                            showSuggestions(events);
        } else {
                            suggestionsContainer.style.display = 'none';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching events:', error);
                        suggestionsContainer.style.display = 'none';
                    });
            }, 300);
        });

        function showSuggestions(events) {
            suggestionsContainer.innerHTML = '';
            
            events.forEach(event => {
                const suggestion = document.createElement('div');
                suggestion.className = 'event-suggestion';
                suggestion.innerHTML = `
                    <strong>${event.name}</strong><br>
                    <small>${event.location} • ${event.datetime}</small>
                `;
                
                suggestion.addEventListener('click', function() {
                    eventNameInput.value = event.name;
                    
                    // Set hidden form inputs
                    if (eventLocationInput) {
                        eventLocationInput.value = event.location;
                    }
                    
                    // Convert to datetime-local format for HTML5 input
                    if (eventDatetimeInput && event.raw_datetime) {
                        const dt = new Date(event.raw_datetime);
                        const localISO = new Date(dt.getTime() - dt.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
                        eventDatetimeInput.value = localISO;
                    }
                    
                    // Update display cards
                    if (eventLocationDisplay) {
                        eventLocationDisplay.textContent = event.location;
                    }
                    if (eventDatetimeDisplay) {
                        eventDatetimeDisplay.textContent = event.datetime;
                    }
                    
                    // Set max price validation
                    if (event.max_ticket_price) {
                        const maxPriceDollars = event.max_ticket_price / 100;
                        const ticketPriceInput = document.getElementById('ticket_price' + suffix);
                        if (ticketPriceInput) {
                            ticketPriceInput.setAttribute('max', maxPriceDollars);
                            ticketPriceInput.setAttribute('data-max-price', maxPriceDollars);
                            
                            // Remove existing event listeners to avoid duplicates
                            const newInput = ticketPriceInput.cloneNode(true);
                            ticketPriceInput.parentNode.replaceChild(newInput, ticketPriceInput);
                            
                            // Add real-time validation
                            newInput.addEventListener('input', function() {
                                const currentPrice = parseFloat(this.value);
                                const maxPrice = parseFloat(this.getAttribute('data-max-price'));
                                const errorSpan = document.getElementById('price-error' + suffix);
                                
                                if (currentPrice > maxPrice) {
                                    if (!errorSpan) {
                                        const error = document.createElement('span');
                                        error.id = 'price-error' + suffix;
                                        error.style.color = '#ef4444';
                                        error.style.fontSize = '12px';
                                        error.style.marginTop = '4px';
                                        error.style.display = 'block';
                                        error.textContent = `Maximum ticket price is $${maxPrice}`;
                                        this.parentNode.appendChild(error);
                                    }
                                    this.style.borderColor = '#ef4444';
                                } else {
                                    if (errorSpan) {
                                        errorSpan.remove();
                                    }
                                    this.style.borderColor = '';
                                }
                            });
                        }
                    }
                    
                    // Show and animate the event details container
                    if (eventDetailsContainer) {
                        eventDetailsContainer.style.display = 'block';
                        setTimeout(() => {
                            eventDetailsContainer.classList.add('show');
                        }, 10);
                    }
                    
                    // Add populated class to cards for styling
                    if (venueCard) {
                        venueCard.classList.add('populated');
                    }
                    if (datetimeCard) {
                        datetimeCard.classList.add('populated');
                    }
                    
                    suggestionsContainer.style.display = 'none';
                });
                
                suggestionsContainer.appendChild(suggestion);
            });
            
            suggestionsContainer.style.display = 'block';
        }

        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!eventNameInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
                suggestionsContainer.style.display = 'none';
            }
        });
    }

    // Initialize autocomplete for both forms
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize for normal position form (no suffix)
        initializeEventAutocomplete();
        
        // Initialize for bottom position form (_bottom suffix)
        initializeEventAutocomplete('_bottom');
    });

    // Tooltip functionality
    document.addEventListener('DOMContentLoaded', function() {
        const tooltipIcons = document.querySelectorAll('.tooltip-icon');
        
        tooltipIcons.forEach(icon => {
            let tooltipTimeout;
            
            icon.addEventListener('mouseenter', function() {
                const tooltipId = this.getAttribute('data-tooltip');
                const tooltipContent = document.getElementById(tooltipId);
                
                if (tooltipContent) {
                    clearTimeout(tooltipTimeout);
                    tooltipContent.classList.add('show');
                }
            });
            
            icon.addEventListener('mouseleave', function() {
                const tooltipId = this.getAttribute('data-tooltip');
                const tooltipContent = document.getElementById(tooltipId);
                
                if (tooltipContent) {
                    tooltipTimeout = setTimeout(() => {
                        tooltipContent.classList.remove('show');
                    }, 150);
                }
            });
            
            // Mobile touch support
            icon.addEventListener('click', function(e) {
                e.preventDefault();
                const tooltipId = this.getAttribute('data-tooltip');
                const tooltipContent = document.getElementById(tooltipId);
                
                if (tooltipContent) {
                    // Hide all other tooltips
                    document.querySelectorAll('.tooltip-content').forEach(tooltip => {
                        if (tooltip !== tooltipContent) {
                            tooltip.classList.remove('show');
                        }
                    });
                    
                    // Toggle this tooltip
                    tooltipContent.classList.toggle('show');
                }
            });
        });
        
        // Hide tooltips when clicking elsewhere
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.tooltip-icon') && !e.target.closest('.tooltip-content')) {
                document.querySelectorAll('.tooltip-content').forEach(tooltip => {
                    tooltip.classList.remove('show');
                });
            }
        });

        // Transaction management functions
        window.showTransactionDetails = function(transactionId) {
            // You can implement a modal or redirect to a details page
            window.open(`/ticket/${transactionId}`, '_blank');
        };

        window.cancelTransaction = function(transactionId) {
            if (confirm('We will send your ticket back to you. Are you sure you want to cancel this transaction?')) {
                fetch(`/api/transactions/${transactionId}/cancel`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Transaction cancelled successfully');
                        location.reload();
        } else {
                        alert('Error cancelling transaction: ' + data.error);
        }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error cancelling transaction');
                });
    }
        };

        window.simulateTicketSent = function(transactionId) {
            if (confirm('Simulate Safe Transaction transferring the ticket to the buyer? This will send a ticket delivery email to the buyer.')) {
                fetch(`/api/transactions/${transactionId}/simulate-ticket-sent`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ Ticket transfer simulated! Delivery confirmation email sent to buyer.');
                        location.reload();
                    } else {
                        alert('Error simulating ticket transfer: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error simulating ticket transfer');
                });
    }
        };
    });


    // User dropdown toggle functionality
    function toggleUserDropdown() {
        const dropdown = document.getElementById('userDropdown');
        dropdown.classList.toggle('active');
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        const userProfile = document.querySelector('.user-profile');
        const dropdown = document.getElementById('userDropdown');
        
        if (!userProfile.contains(event.target)) {
            dropdown.classList.remove('active');
        }
    });

    // Close dropdown on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.getElementById('userDropdown').classList.remove('active');
        }
    });

    // School selection toggle functionality
    document.addEventListener('DOMContentLoaded', function() {
        const schoolInputs = document.querySelectorAll('input[name="school"]');
        const schoolToggleGroup = document.querySelector('.school-toggle-group');
        
        // Handle school selection changes
        schoolInputs.forEach(input => {
            input.addEventListener('change', function() {
                if (this.checked) {
                    console.log('Selected school:', this.value);
                    
                    // Update CSS classes for sliding animation fallback
                    updateToggleAnimation(this.value);
                    
                    // Update form behavior based on selected school
                    updateFormForSchool(this.value);
                }
            });
        });
        
        function updateToggleAnimation(school) {
            if (schoolToggleGroup) {
                // Remove all selection classes
                schoolToggleGroup.classList.remove('michigan-selected', 'florida-selected');
                
                // Add the appropriate class for the selected school
                if (school === 'michigan') {
                    schoolToggleGroup.classList.add('michigan-selected');
                } else if (school === 'florida') {
                    schoolToggleGroup.classList.add('florida-selected');
                }
            }
        }
        
        function updateFormForSchool(school) {
            // Update placeholder text based on school selection
            const eventInput = document.getElementById('event_name_bottom');
            if (eventInput) {
                if (school === 'michigan') {
                    eventInput.placeholder = 'e.g., Ohio State vs Michigan';
                } else if (school === 'florida') {
                    eventInput.placeholder = 'e.g., Georgia vs Florida';
                }
            }
            
            // Update buyer email label and placeholder based on school
            const buyerEmailLabel = document.querySelector('label[for="buyer_email_bottom"]');
            const buyerEmailInput = document.getElementById('buyer_email_bottom');
            
            if (buyerEmailLabel && buyerEmailInput) {
                if (school === 'michigan') {
                    buyerEmailLabel.textContent = 'Buyer Michigan Athletics Email';
                    buyerEmailInput.placeholder = 'buyer@umich.edu';
                } else if (school === 'florida') {
                    buyerEmailLabel.textContent = 'Buyer Email';
                    buyerEmailInput.placeholder = 'buyer@ufl.edu';
                }
            }
            
            // Update hidden form field
            const hiddenSchoolInput = document.getElementById('selected_school');
            if (hiddenSchoolInput) {
                hiddenSchoolInput.value = school;
            }
            
            // Clear event input and suggestions when school changes
            if (eventInput) {
                eventInput.value = '';
            }
            const suggestions = document.getElementById('event_suggestions_bottom');
            if (suggestions) {
                suggestions.innerHTML = '';
                suggestions.style.display = 'none';
            }
            
            // You can add more school-specific behavior here
            // For example, filtering event suggestions, updating colors, etc.
        }
        
        // Initialize with default selection
        const defaultSchool = document.querySelector('input[name="school"]:checked');
        if (defaultSchool) {
            updateToggleAnimation(defaultSchool.value);
            updateFormForSchool(defaultSchool.value);
        }
    });
