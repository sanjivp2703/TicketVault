function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked tab
    event.target.classList.add('active');
}

function resolveComplaint(transactionId, resolution) {
    if (confirm(`Are you sure you want to ${resolution.replace('_', ' ')} for transaction #${transactionId}?`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/resolve-complaint/${transactionId}`;
        
        const resolutionInput = document.createElement('input');
        resolutionInput.type = 'hidden';
        resolutionInput.name = 'resolution';
        resolutionInput.value = resolution;
        
        form.appendChild(resolutionInput);
        document.body.appendChild(form);
        form.submit();
    }
}

function declareTicketSent(transactionId) {
    if (confirm(`Are you sure you want to declare that the ticket was sent for transaction #${transactionId}?\n\n⚠️ This should only be done AFTER the buyer has paid!\n\nThis will:\n- Update the transaction status to "ticket_sent"\n- Process payment to seller\n- Send notification emails to buyer and seller\n- Close the transaction`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/declare-ticket-sent/${transactionId}`;
        
        document.body.appendChild(form);
        form.submit();
    }
}

function verifyTicket(transactionId) {
    if (confirm(`Are you sure you want to verify the ticket for transaction #${transactionId}?\n\n✅ This will:\n- Mark the ticket as verified\n- Send payment email to the buyer\n- Change status to "waiting_for_payment"\n\n⚠️ Only do this AFTER you've received and verified the ticket from the seller!`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/verify-ticket/${transactionId}`;
        
        document.body.appendChild(form);
        form.submit();
    }
}

function releaseFunds(transactionId) {
    if (confirm(`Are you sure you want to release funds for transaction #${transactionId}?\n\n💰 This will:\n- Mark transaction as completed\n- Release funds to the seller\n- Close the transaction\n\n⚠️ Only do this AFTER you've forwarded the ticket to the buyer!`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/release-funds/${transactionId}`;
        
        document.body.appendChild(form);
        form.submit();
    }
}

function acceptTicket(transactionId) {
    if (confirm(`Are you sure you want to ACCEPT the ticket for transaction #${transactionId}?\n\n✅ This will:\n- Mark the ticket as verified\n- Send payment link to the buyer\n- Change status to "waiting_for_payment"\n\n⚠️ Only accept if the ticket is valid and correct!`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/accept-ticket/${transactionId}`;
        
        document.body.appendChild(form);
        form.submit();
    }
}

function rejectTicket(transactionId) {
    const reason = prompt(`Why are you rejecting this ticket?\n\nThis reason will be sent to the seller so they can fix the issue and resubmit.\n\nCommon reasons:\n- Wrong event\n- Invalid ticket format\n- Missing information\n- Unclear/blurry image`);
    
    if (reason && reason.trim()) {
        if (confirm(`Reject ticket for transaction #${transactionId}?\n\n❌ This will:\n- Return ticket to seller\n- Send rejection reason: "${reason}"\n- Reset status to "pending_ticket_submission"\n- Seller can resubmit a corrected ticket\n\nContinue?`)) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/admin/reject-ticket/${transactionId}`;
            
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'rejection_reason';
            input.value = reason;
            form.appendChild(input);
            
            document.body.appendChild(form);
            form.submit();
        }
    } else if (reason !== null) {
        alert('Please provide a reason for rejection.');
    }
}

function markWithdrawalComplete(withdrawalId) {
    if (confirm(`✅ Mark withdrawal #${withdrawalId} as complete?\n\n⚠️ Make sure you have already sent the money to the user before clicking OK!\n\nThis will:\n- Mark the withdrawal as completed\n- Send completion email to the user\n- Remove from pending list`)) {
        // Show loading state
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = 'Processing...';
        button.disabled = true;
        
        // Send AJAX request
        fetch(`/admin/withdrawal/complete/${withdrawalId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ Withdrawal marked as complete! Completion email sent to user.');
                location.reload(); // Reload page to update the pending withdrawals list
            } else {
                alert('❌ Error: ' + (data.error || 'Failed to mark withdrawal as complete'));
                button.innerHTML = originalText;
                button.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('❌ Network error. Please try again.');
            button.innerHTML = originalText;
            button.disabled = false;
        });
    }
}

// Countdown timer for payment deadlines
function updateCountdownTimers() {
    const timers = document.querySelectorAll('.countdown-timer');
    timers.forEach(timer => {
        const deadline = timer.getAttribute('data-deadline');
        if (!deadline) return;

        try {
            // Parse the deadline - handle both formats
            let deadlineDate;
            if (deadline.includes('T')) {
                deadlineDate = new Date(deadline);
            } else {
                deadlineDate = new Date(deadline.replace(/-/g, '/'));
            }

            const now = new Date();
            const diff = deadlineDate - now;

            if (diff <= 0) {
                timer.textContent = 'Expired';
                timer.style.color = 'var(--color-danger)';
                timer.style.fontWeight = '800';
            } else {
                const hours = Math.floor(diff / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);

                let countdownText = '';
                if (hours > 0) {
                    countdownText = `${hours}h ${minutes}m ${seconds}s remaining`;
                } else if (minutes > 0) {
                    countdownText = `${minutes}m ${seconds}s remaining`;
                } else {
                    countdownText = `${seconds}s remaining`;
                }

                timer.textContent = countdownText;
                
                // Change color based on urgency
                if (diff < 5 * 60 * 1000) { // Less than 5 minutes
                    timer.style.color = 'var(--color-danger)';
                } else if (diff < 15 * 60 * 1000) { // Less than 15 minutes
                    timer.style.color = 'var(--color-warning)';
                } else {
                    timer.style.color = 'var(--color-info)';
                }
            }
        } catch (e) {
            timer.textContent = 'Invalid deadline format';
            console.error('Countdown error:', e);
        }
    });
}

// Update countdown timers every second
setInterval(updateCountdownTimers, 1000);
// Initial update
updateCountdownTimers();
