        function toggleOtherReason() {
            const reasonSelect = document.getElementById('reason');
            const otherDiv = document.getElementById('otherReasonDiv');
            const otherTextarea = document.getElementById('other_reason');
            
            if (reasonSelect.value === 'Other') {
                otherDiv.style.display = 'block';
                otherTextarea.required = true;
            } else {
                otherDiv.style.display = 'none';
                otherTextarea.required = false;
                otherTextarea.value = '';
            }
        }
