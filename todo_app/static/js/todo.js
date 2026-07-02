// Function to style all inputs, selects, and textareas dynamically
function styleFormFields(container = document) {
    container.querySelectorAll('input, select, textarea').forEach(el => {
        if (el.type === 'submit' || el.type === 'button' || el.type === 'hidden') return;
        el.classList.add(
            'w-full', 'px-3', 'py-2', 'border', 'border-gray-300', 
            'rounded-md', 'shadow-sm', 'focus:outline-none', 
            'focus:ring-2', 'focus:ring-violet-500'
        );
    });
}

// Function to initialize clear date button functionality
function initDateClearButton(container = document) {
    const dateInput = container.querySelector('input[type="date"]');
    const clearDateBtn = container.querySelector('#clear-date-btn');
    if (dateInput && clearDateBtn) {
        const toggleClearBtn = () => {
            if (dateInput.value) {
                clearDateBtn.classList.remove('hidden');
            } else {
                clearDateBtn.classList.add('hidden');
            }
        };
        
        dateInput.addEventListener('input', toggleClearBtn);
        dateInput.addEventListener('change', toggleClearBtn);
        
        // Check initial state
        toggleClearBtn();
        
        clearDateBtn.addEventListener('click', () => {
            dateInput.value = '';
            toggleClearBtn();
        });
    }
}

// Automatically style static form fields on page load
document.addEventListener('DOMContentLoaded', () => {
    styleFormFields();
    initDateClearButton();
});

// Modal Controller functions
function openTodoModal(url, titleText) {
    const modal = document.getElementById('todo-modal');
    if (!modal) return;

    const content = document.getElementById('todo-modal-content');
    const title = document.getElementById('todo-modal-title');
    
    if (title) title.innerText = titleText;
    
    // Show modal and loading spinner
    modal.classList.remove('hidden');
    if (content) {
        content.innerHTML = `
            <div class="flex justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-800"></div>
            </div>
        `;
    }
    
    // Fetch the partial form
    fetch(url + '?ajax=1')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            if (content) {
                content.innerHTML = html;
                // Style newly injected fields
                styleFormFields(content);
                initDateClearButton(content);
            }
        })
        .catch(error => {
            console.error('Error fetching form:', error);
            const errText = window.TodoTranslations?.errorLoadingForm || "Ocorreu um erro ao carregar o formulário.";
            const closeText = window.TodoTranslations?.close || "Fechar";
            if (content) {
                content.innerHTML = `
                    <div class="text-center py-4 text-red-600">
                        <span class="material-icons text-4xl mb-2">error</span>
                        <p>${errText}</p>
                        <button type="button" onclick="closeTodoModal()" class="mt-4 px-4 py-2 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded-md transition font-medium">
                            ${closeText}
                        </button>
                    </div>
                `;
            }
        });
}

function closeTodoModal() {
    const modal = document.getElementById('todo-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Close modal if user clicks outside of it
window.addEventListener('click', function(event) {
    const modal = document.getElementById('todo-modal');
    if (event.target === modal) {
        closeTodoModal();
    }
});

// Intercept form submission inside modal
document.addEventListener('DOMContentLoaded', () => {
    const content = document.getElementById('todo-modal-content');
    if (content) {
        content.addEventListener('submit', function(event) {
            if (event.target.tagName === 'FORM') {
                event.preventDefault();
                const form = event.target;
                const formData = new FormData(form);
                
                fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        return response.json().then(data => ({ isJson: true, data }));
                    } else {
                        return response.text().then(text => ({ isJson: false, text }));
                    }
                })
                .then(result => {
                    if (result.isJson && result.data.success) {
                        closeTodoModal();
                        // Use HTMX to refresh the list and trigger Out-Of-Band stats updates automatically
                        htmx.ajax('GET', window.location.pathname + window.location.search, {
                            target: '#todo-list-container',
                            swap: 'innerHTML'
                        });
                    } else {
                        content.innerHTML = result.text;
                        styleFormFields(content);
                        initDateClearButton(content);
                    }
                })
                .catch(err => {
                    console.error('Error submitting form:', err);
                });
            }
        });
    }

    // Search input clear button logic
    const searchInput = document.getElementById('search-input');
    const clearBtn = document.getElementById('clear-search-btn');
    if (searchInput && clearBtn) {
        searchInput.addEventListener('input', () => {
            if (searchInput.value.length > 0) {
                clearBtn.classList.remove('hidden');
            } else {
                clearBtn.classList.add('hidden');
            }
        });

        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            clearBtn.classList.add('hidden');
            searchInput.focus();
            
            const form = document.getElementById('search-filter-form');
            if (form) {
                htmx.trigger(form, 'submit');
            }
        });
    }
});

// Toggle filter dropdown visibility
function toggleFilterDropdown() {
    const dropdown = document.getElementById('search-filter-checkbox-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}

// Automatically submit the form on checkbox changes (via HTMX trigger)
function submitSearchForm() {
    const form = document.getElementById('search-filter-form');
    if (form) {
        htmx.trigger(form, 'submit');
    }
}

// Close filter dropdown if clicked outside of it
window.addEventListener('click', function(event) {
    const dropdown = document.getElementById('search-filter-checkbox-dropdown');
    const button = document.querySelector('#search-filter-form button[type="button"]');
    if (dropdown && !dropdown.classList.contains('hidden') && button) {
        if (!dropdown.contains(event.target) && !button.contains(event.target)) {
            dropdown.classList.add('hidden');
        }
    }
});

// Toggle profile drawer visibility
function toggleProfileDrawer() {
    const drawer = document.getElementById('profile-drawer');
    if (drawer) {
        drawer.classList.toggle('hidden');
    }
}

// Close profile drawer if user clicks outside of it
window.addEventListener('click', function(event) {
    const drawer = document.getElementById('profile-drawer');
    const button = document.querySelector('button[onclick="toggleProfileDrawer()"]');
    if (drawer && !drawer.classList.contains('hidden') && button) {
        if (event.target === drawer) {
            toggleProfileDrawer();
        }
    }
});

// Automatically open profile drawer if '?profile=1' is in query string (supports static load and HTMX swaps)
document.addEventListener('htmx:load', () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('profile')) {
        const drawer = document.getElementById('profile-drawer');
        if (drawer && drawer.classList.contains('hidden')) {
            toggleProfileDrawer();
        }
        // Clean up URL without reloading
        const cleanUrl = window.location.pathname + window.location.hash;
        window.history.replaceState({}, document.title, cleanUrl);
    }
});
