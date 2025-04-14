// Custom JavaScript for Inventory Workflow Management System

document.addEventListener('DOMContentLoaded', function() {
    // Dynamic calculation of item totals in order forms
    const quantityInputs = document.querySelectorAll('.quantity-input');
    const priceInputs = document.querySelectorAll('.price-input');
    
    // Function to calculate totals
    function calculateTotals() {
        const rows = document.querySelectorAll('.item-row');
        let grandTotal = 0;
        
        rows.forEach(row => {
            const quantity = parseFloat(row.querySelector('.quantity-input').value) || 0;
            const price = parseFloat(row.querySelector('.price-input').value) || 0;
            const totalElem = row.querySelector('.item-total');
            
            const itemTotal = quantity * price;
            if (totalElem) {
                totalElem.textContent = itemTotal.toFixed(2);
            }
            
            grandTotal += itemTotal;
        });
        
        const orderTotalElem = document.getElementById('order-total');
        if (orderTotalElem) {
            orderTotalElem.textContent = grandTotal.toFixed(2);
        }
    }
    
    // Add event listeners to inputs
    quantityInputs.forEach(input => {
        input.addEventListener('change', calculateTotals);
        input.addEventListener('keyup', calculateTotals);
    });
    
    priceInputs.forEach(input => {
        input.addEventListener('change', calculateTotals);
        input.addEventListener('keyup', calculateTotals);
    });
    
    // Initialize calculation
    calculateTotals();
    
    // Add dynamic form fields for order creation
    const addItemBtn = document.getElementById('add-item-btn');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function() {
            const formsetContainer = document.getElementById('formset-container');
            const formsetPrefix = 'form';
            const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');
            
            // Get current form count
            let formCount = parseInt(totalFormsInput.value);
            
            // Clone the first form
            const template = document.querySelector('.empty-form').cloneNode(true);
            template.classList.remove('empty-form');
            template.classList.add('item-form');
            template.style.display = 'block';
            
            // Update form index
            template.innerHTML = template.innerHTML.replace(/__prefix__/g, formCount);
            
            // Update form count
            formsetContainer.appendChild(template);
            totalFormsInput.value = formCount + 1;
            
            // Reinitialize any select elements if needed
            initializeSelect2();
        });
    }
    
    // Delete item button functionality
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('delete-item-btn')) {
            const formRow = e.target.closest('.item-form');
            const deleteInput = formRow.querySelector('input[name$="-DELETE"]');
            
            if (deleteInput) {
                deleteInput.value = 'on';
                formRow.style.display = 'none';
            } else {
                formRow.remove();
            }
            
            calculateTotals();
        }
    });
    
    // Initialize Select2 if available
    function initializeSelect2() {
        if (typeof $.fn.select2 !== 'undefined') {
            $('.product-select').select2({
                placeholder: 'Select a product',
                allowClear: true,
                width: '100%'
            });
        }
    }
    
    // Initialize any Select2 elements
    initializeSelect2();
    
    // Print functionality
    const printButtons = document.querySelectorAll('.print-btn');
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });
}); 