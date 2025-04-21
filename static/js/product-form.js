/**
 * Product Form Handler
 * This file handles the product form submission and validation
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Product form handler loaded');
    
    // Find the product form
    const productForm = document.getElementById('productForm');
    if (!productForm) {
        console.log('Product form not found');
        return;
    }
    
    console.log('Product form found:', productForm);
    
    // Add required attribute to mandatory fields
    const titleField = document.querySelector('[name="title"]');
    const codeField = document.querySelector('[name="code"]');
    const priceField = document.querySelector('[name="price_per_unit"]');
    const unitField = document.querySelector('[name="unit_ref"]');
    
    if (titleField) titleField.setAttribute('required', 'required');
    if (codeField) codeField.setAttribute('required', 'required');
    if (priceField) priceField.setAttribute('required', 'required');
    
    // Handle form submission
    productForm.addEventListener('submit', function(event) {
        // For debugging
        console.log('Form submit event triggered');
        
        // Validate form
        let isValid = true;
        
        // Check required fields
        if (titleField && !titleField.value.trim()) {
            isValid = false;
            titleField.classList.add('is-invalid');
        } else if (titleField) {
            titleField.classList.remove('is-invalid');
        }
        
        if (codeField && !codeField.value.trim()) {
            isValid = false;
            codeField.classList.add('is-invalid');
        } else if (codeField) {
            codeField.classList.remove('is-invalid');
        }
        
        if (priceField && !priceField.value.trim()) {
            isValid = false;
            priceField.classList.add('is-invalid');
        } else if (priceField) {
            priceField.classList.remove('is-invalid');
        }
        
        if (!isValid) {
            console.log('Form validation failed');
            event.preventDefault();
            return false;
        }
        
        // If everything is valid, let the form submit
        console.log('Form is valid, continuing submission');
    });
    
    // Add click handler for the save button
    const saveButton = document.getElementById('saveProductBtn');
    if (saveButton) {
        console.log('Save button found');
        saveButton.addEventListener('click', function(e) {
            console.log('Save button clicked manually');
            // Don't prevent default here - we want the normal form submission to work
        });
    }
    
    // Fix any issues with form inputs
    const formInputs = productForm.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        // Add required class for styling
        if (input.hasAttribute('required')) {
            const label = productForm.querySelector(`label[for="${input.id}"]`);
            if (label) {
                label.classList.add('required-field');
            }
        }
        
        // Fix any autocomplete issues
        input.autocomplete = 'off';
    });
}); 