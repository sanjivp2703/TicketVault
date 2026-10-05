/* Pending listing popup (templates/pending_listing_popup.html). Moved verbatim from the inline script. */
let currentTicketEmail = '';

function showPendingListingPopup(ticketEmail, transactionId) {
    currentTicketEmail = ticketEmail;
    window.currentTransactionId = transactionId;
    document.getElementById('ticketEmail').value = ticketEmail;
    const popup = document.getElementById('pendingListingPopup');
    popup.style.display = 'flex';
    popup.style.justifyContent = 'center';
    popup.style.alignItems = 'center';
}

function closePendingPopup() {
    console.log(`🔄 CLOSING POPUP at ${new Date().toLocaleTimeString()} - NO EMAIL SENT NOW (emails are sent during verification, not during popup close)`);
    document.getElementById('pendingListingPopup').style.display = 'none';
    // Refresh the page to show updated listings
    window.location.reload();
}

function copyToClipboard(text, button) {
    // Use the modern clipboard API if available
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showCopyFeedback(button);
        }).catch(err => {
            // Fallback for clipboard API failure
            fallbackCopyToClipboard(text, button);
        });
    } else {
        // Fallback for older browsers or non-secure contexts
        fallbackCopyToClipboard(text, button);
    }
}

function fallbackCopyToClipboard(text, button) {
    // Create a temporary textarea element
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
    document.execCommand('copy');
        showCopyFeedback(button);
    } catch (err) {
        console.error('Fallback: Could not copy text: ', err);
    }
    
    document.body.removeChild(textArea);
}

function showCopyFeedback(button) {
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    button.style.background = '#00d4aa';
    button.style.color = 'white';
    
    setTimeout(() => {
        button.textContent = originalText;
        button.style.background = '#667eea';
        button.style.color = 'white';
    }, 2000);
}

function openMichiganAthletics() {
    // Open Michigan Athletics ticket transfer page
    window.open('https://mgoblue.evenue.net/account/login', '_blank');
    
    // Show a helpful message
    setTimeout(() => {
        alert('🎟️ Michigan Athletics page opened!\n\nUse the transfer details from this popup to complete your ticket transfer.');
    }, 500);
}

function markAsTransferred() {
    // Show confirmation message
    document.getElementById('sentStatus').style.display = 'block';
    
    // Hide the action buttons
    const actionButtons = document.querySelectorAll('button[onclick*="Michigan"], button[onclick*="markAsTransferred"]');
    actionButtons.forEach(button => {
        button.style.display = 'none';
    });
    
    console.log('🚀 User marked transfer as complete - monitoring for verification');
}

function markAsTransferredAndClose() {
    const transactionId = getCurrentTransactionId();
    
    if (!transactionId) {
        alert('Error: No transaction ID found');
        return;
    }
    
    if (confirm('Confirm that you have sent the ticket to Safe Transaction. The transaction will move to verification.')) {
        const button = event.target;
        if (button) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            button.style.opacity = '0.6';
        }

        fetch('/api/test-ticket-sent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                transaction_id: transactionId,
                test_mode: false
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('✅ Ticket marked as sent successfully');
                closePendingPopup();
                // Reload page to show updated status
                setTimeout(() => {
                    location.reload();
                }, 500);
            } else {
                alert('Error: ' + (data.error || 'Unable to process request'));
                if (button) {
                    button.disabled = false;
                    button.innerHTML = 'I\'ve completed the transfer';
                    button.style.opacity = '1';
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error processing request. Please try again.');
            if (button) {
                button.disabled = false;
                button.innerHTML = 'I\'ve completed the transfer';
                button.style.opacity = '1';
            }
        });
    }
}

function getCurrentTransactionId() {
    // This will be set when the popup is shown
    return window.currentTransactionId || null;
}

// Test Verify Function for Popup
function testVerifyFromPopup() {
    const transactionId = getCurrentTransactionId();
    
    if (!transactionId) {
        alert('Error: No transaction ID found');
        return;
    }
    
    if (confirm('⚡ TEST MODE: This will instantly verify the listing and send buyer notification. Continue?')) {
        const button = document.getElementById('testVerifyButton');
        if (button) {
            button.disabled = true;
            button.innerHTML = 'Verifying...';
            button.style.opacity = '0.6';
        }

        fetch('/api/test-verify', {
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
                alert('✅ TEST VERIFICATION COMPLETE!\n\n' + 
                      '• Listing instantly verified\n' + 
                      '• Buyer notification email sent\n' + 
                      '• Payment deadline set\n' + 
                      '• Status updated to waiting for payment');
                
                // Close popup and refresh page to show updated status
                closePendingPopup();
            } else {
                alert('Error: ' + data.error);
                // Reset button state
                if (button) {
                    button.disabled = false;
                    button.innerHTML = 'TEST: Instant Verify';
                    button.style.opacity = '1';
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error processing test verification');
            // Reset button state
            if (button) {
                button.disabled = false;
                button.innerHTML = 'TEST: Instant Verify';
                button.style.opacity = '1';
            }
        });
    }
}

// Note: Popup no longer closes when clicking outside since there's no X button

// Add hover effects for buttons
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effect to primary button
    const primaryButton = document.querySelector('button[onclick="markAsTransferredAndClose()"]');
    if (primaryButton) {
        primaryButton.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
            this.style.transform = 'translateY(-1px)';
        });
        primaryButton.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)';
            this.style.transform = 'translateY(0)';
        });
    }
});
