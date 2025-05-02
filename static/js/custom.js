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
            $('.product-select').each(function() {
                // ذخیره مقدار فعلی قبل از راه‌اندازی Select2
                const currentValue = $(this).val();
                
                $(this).select2({
                    placeholder: 'انتخاب محصول...',
                    allowClear: true,
                    width: '100%',
                    language: {
                        inputTooShort: function () {
                            return "لطفا برای جستجو حداقل یک حرف وارد کنید";
                        },
                        noResults: function () {
                            return "نتیجه‌ای یافت نشد";
                        },
                        searching: function () {
                            return "در حال جستجو...";
                        }
                    },
                    dir: "rtl",
                    minimumInputLength: 1,
                    // تابع جستجوی سفارشی برای بهبود نتایج جستجو
                    matcher: function(params, data) {
                        // اگر هیچ متنی برای جستجو وارد نشده باشد، همه گزینه‌ها را نمایش بده
                        if ($.trim(params.term) === '') {
                            return data;
                        }

                        // اگر داده‌ای وجود نداشته باشد، هیچ چیزی نمایش نده
                        if (typeof data.text === 'undefined') {
                            return null;
                        }

                        // عبارت جستجو را به حروف کوچک تبدیل کن
                        var term = params.term.toLowerCase();
                        
                        // داده‌های جستجو را از داخل data-search بخوان
                        var searchData = data.element.getAttribute('data-search') || '';
                        searchData = searchData.toLowerCase();
                        
                        // اگر متن جستجو شده در عنوان یا کد محصول یافت شود، آن را نمایش بده
                        if (data.text.toLowerCase().indexOf(term) > -1 || 
                            searchData.indexOf(term) > -1) {
                            return data;
                        }

                        // در غیر این صورت نمایش نده
                        return null;
                    }
                }).on('select2:open', function() {
                    document.querySelector('.select2-search__field').focus();
                });
                
                // بازگرداندن مقدار قبلی بعد از راه‌اندازی Select2
                if (currentValue) {
                    $(this).val(currentValue).trigger('change');
                }
                
                // بروزرسانی برچسب واحد بعد از انتخاب محصول
                const unitLabel = $(this).closest('.item-form').find('.unit-label');
                if (currentValue && unitLabel.length) {
                    const selectedOption = $(this).find('option[value="' + currentValue + '"]');
                    const unit = selectedOption.data('unit') || 'واحد';
                    unitLabel.text(unit);
                }
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
    
    // Fix for product form submission
    const productForm = document.querySelector('form[action*="product"]');
    if (productForm) {
        // Log that we found the product form
        console.log('Product form found:', productForm);
        
        // Add explicit submit handler
        productForm.addEventListener('submit', function(event) {
            // Prevent the default form submit to debug first
            console.log('Form submit triggered');
            
            // Check for any validation issues
            const requiredFields = productForm.querySelectorAll('[required]');
            let hasErrors = false;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    console.log('Field is empty:', field);
                    field.classList.add('is-invalid');
                    hasErrors = true;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (hasErrors) {
                event.preventDefault();
                console.log('Form has validation errors');
                return;
            }
            
            // If everything is valid, ensure the form submits properly
            console.log('Form is valid, submitting...');
        });
        
        // Check for save button and add click handler
        const saveButton = productForm.querySelector('button[type="submit"]');
        if (saveButton) {
            console.log('Save button found:', saveButton);
            saveButton.addEventListener('click', function(e) {
                console.log('Save button clicked');
                // Programmatically submit the form
                productForm.submit();
            });
        }
    }
}); 