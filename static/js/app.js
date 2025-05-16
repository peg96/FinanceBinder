document.addEventListener('DOMContentLoaded', function() {
    // Set default date to today for new transactions
    const today = new Date().toISOString().split('T')[0];
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });
    
    // Binder header toggle functionality
    const binderHeaders = document.querySelectorAll('.binder-header');
    binderHeaders.forEach(header => {
        header.addEventListener('click', function(event) {
            // Don't toggle if clicked on the button group
            if (event.target.closest('.btn-group')) {
                return;
            }
            
            const binderId = this.getAttribute('data-binder-id');
            const binderCard = this.closest('.binder-card');
            const binderContent = binderCard.querySelector('.binder-content');
            const toggleIcon = binderCard.querySelector('.toggle-icon i');
            
            binderContent.classList.toggle('show');
            
            if (binderContent.classList.contains('show')) {
                toggleIcon.classList.remove('fa-chevron-down');
                toggleIcon.classList.add('fa-chevron-up');
            } else {
                toggleIcon.classList.remove('fa-chevron-up');
                toggleIcon.classList.add('fa-chevron-down');
            }
        });
    });

    // Category selector functionality
    const categorySelectors = document.querySelectorAll('.category-selector');
    categorySelectors.forEach(selector => {
        selector.addEventListener('click', function() {
            const binderId = this.getAttribute('data-binder-id');
            const category = this.getAttribute('data-category');
            const categoryId = this.getAttribute('data-category-id');
            const binderCard = this.closest('.binder-card');
            
            // Update current category name display
            const currentCategoryName = binderCard.querySelector('.current-category-name');
            const currentCategoryTotalName = binderCard.querySelector('.current-category-total-name');
            
            if (category === 'all') {
                currentCategoryName.textContent = 'Tutte le categorie';
                currentCategoryTotalName.textContent = 'Tutte le categorie';
            } else {
                currentCategoryName.textContent = this.textContent.trim();
                currentCategoryTotalName.textContent = 'categoria ' + this.textContent.trim();
            }
            
            // Filter transactions
            const table = binderCard.querySelector('.transactions-table');
            const rows = table.querySelectorAll('tbody tr.transaction-row');
            
            let categoryTotal = 0;
            
            rows.forEach(row => {
                const rowCategoryId = row.getAttribute('data-category-id');
                
                if (category === 'all' || rowCategoryId === categoryId) {
                    row.style.display = '';
                    
                    // Add to category total if visible
                    const amountCell = row.querySelector('td:nth-child(4)');
                    if (amountCell) {
                        const amountText = amountCell.textContent.trim().replace('€', '').trim();
                        const amount = parseFloat(amountText);
                        if (!isNaN(amount)) {
                            categoryTotal += amount;
                        }
                    }
                } else {
                    row.style.display = 'none';
                }
            });
            
            // Update total if filtering by category
            if (category !== 'all') {
                const totalElement = binderCard.querySelector('.total-amount');
                totalElement.textContent = categoryTotal.toFixed(2) + ' €';
                
                // Update class for color
                if (categoryTotal < 0) {
                    totalElement.classList.add('text-danger');
                    totalElement.classList.remove('text-success');
                } else {
                    totalElement.classList.add('text-success');
                    totalElement.classList.remove('text-danger');
                }
            } else {
                // Restore original total for all categories
                const totalElement = binderCard.querySelector('.total-amount');
                const allTotal = parseFloat(totalElement.getAttribute('data-all-total'));
                totalElement.textContent = allTotal.toFixed(2) + ' €';
                
                // Update class for color
                if (allTotal < 0) {
                    totalElement.classList.add('text-danger');
                    totalElement.classList.remove('text-success');
                } else {
                    totalElement.classList.add('text-success');
                    totalElement.classList.remove('text-danger');
                }
            }
            
            // Show/hide back button
            const backButton = binderCard.querySelector('.back-to-categories-btn');
            if (category !== 'all') {
                backButton.classList.remove('d-none');
            } else {
                backButton.classList.add('d-none');
            }
        });
    });
    
    // Back to categories button
    const backButtons = document.querySelectorAll('.back-to-categories-btn');
    backButtons.forEach(button => {
        button.addEventListener('click', function() {
            const binderName = this.getAttribute('data-binder');
            const binderCard = this.closest('.binder-card');
            
            // Find and click the "all" category selector
            const allCategorySelector = binderCard.querySelector('.category-selector[data-category="all"]');
            if (allCategorySelector) {
                allCategorySelector.click();
            }
        });
    });
    
    // Handler for Delete Binder Modal
    const deleteBinderModal = document.getElementById('deleteBinderModal');
    if (deleteBinderModal) {
        deleteBinderModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const binderName = button.getAttribute('data-binder');
            
            const deleteBinderName = document.getElementById('deleteBinderName');
            const deleteBinderForm = document.getElementById('deleteBinderForm');
            
            deleteBinderName.textContent = binderName;
            deleteBinderForm.action = `/api/binder/${binderName}/delete`;
        });
    }
    
    // Handler for New Category Modal
    const newCategoryModal = document.getElementById('newCategoryModal');
    if (newCategoryModal) {
        newCategoryModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const binderName = button.getAttribute('data-binder');
            
            const newCategoryForm = document.getElementById('newCategoryForm');
            newCategoryForm.action = `/api/binder/${binderName}/category`;
        });
    }
    
    // Handler for Delete Category Modal
    const deleteCategoryModal = document.getElementById('deleteCategoryModal');
    if (deleteCategoryModal) {
        deleteCategoryModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const binderName = button.getAttribute('data-binder');
            const categoryName = button.getAttribute('data-category');
            
            const deleteCategoryName = document.getElementById('deleteCategoryName');
            const deleteCategoryForm = document.getElementById('deleteCategoryForm');
            
            deleteCategoryName.textContent = categoryName;
            deleteCategoryForm.action = `/api/binder/${binderName}/category/${categoryName}/delete`;
        });
    }
    
    // Handler for Add Transaction Modal
    const addTransactionModal = document.getElementById('addTransactionModal');
    if (addTransactionModal) {
        addTransactionModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const binderName = button.getAttribute('data-binder');
            
            const addTransactionForm = document.getElementById('addTransactionForm');
            const categorySelect = document.getElementById('transaction_category');
            
            // Clear previous options
            categorySelect.innerHTML = '<option value="" disabled selected>Seleziona una categoria</option>';
            
            // Fetch categories for the selected binder
            fetch(`/api/binder/${binderName}/data`)
                .then(response => response.json())
                .then(data => {
                    const categories = data.categories || {};
                    
                    // Add categories to select
                    Object.keys(categories).forEach(categoryName => {
                        const option = document.createElement('option');
                        option.value = categoryName;
                        option.textContent = categoryName;
                        categorySelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Error fetching categories:', error));
            
            addTransactionForm.action = `/api/binder/${binderName}/transaction`;
        });
    }
    
    // Handler for Edit Transaction Modal
    const editTransactionModal = document.getElementById('editTransactionModal');
    if (editTransactionModal) {
        editTransactionModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const binderName = button.getAttribute('data-binder');
            const transactionId = button.getAttribute('data-transaction');
            const date = button.getAttribute('data-date');
            const category = button.getAttribute('data-category');
            const description = button.getAttribute('data-description');
            const amount = button.getAttribute('data-amount');
            
            const editTransactionForm = document.getElementById('editTransactionForm');
            const dateInput = document.getElementById('edit_transaction_date');
            const categorySelect = document.getElementById('edit_transaction_category');
            const descriptionInput = document.getElementById('edit_transaction_description');
            const amountInput = document.getElementById('edit_transaction_amount');
            
            // Clear previous options
            categorySelect.innerHTML = '<option value="" disabled selected>Seleziona una categoria</option>';
            
            // Fetch categories for the selected binder
            fetch(`/api/binder/${binderName}/data`)
                .then(response => response.json())
                .then(data => {
                    const categories = data.categories || {};
                    
                    // Add categories to select
                    Object.keys(categories).forEach(categoryName => {
                        const option = document.createElement('option');
                        option.value = categoryName;
                        option.textContent = categoryName;
                        if (categoryName === category) {
                            option.selected = true;
                        }
                        categorySelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Error fetching categories:', error));
            
            // Set form values
            dateInput.value = date;
            descriptionInput.value = description || '';
            amountInput.value = amount;
            
            editTransactionForm.action = `/api/binder/${binderName}/transaction/${transactionId}/edit`;
        });
    }
    
    // Handler for Delete Transaction Modal
    const deleteTransactionModal = document.getElementById('deleteTransactionModal');
    if (deleteTransactionModal) {
        deleteTransactionModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const binderName = button.getAttribute('data-binder');
            const transactionId = button.getAttribute('data-transaction');
            
            const deleteTransactionForm = document.getElementById('deleteTransactionForm');
            deleteTransactionForm.action = `/api/binder/${binderName}/transaction/${transactionId}/delete`;
        });
    }
    
    // Initialize all charts after all document is loaded
    const charts = document.querySelectorAll('.transaction-chart');
    charts.forEach(canvas => {
        const binderName = canvas.getAttribute('data-binder');
        if (binderName) {
            initChart(canvas, binderName);
        }
    });
});
