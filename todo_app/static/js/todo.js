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

// Automatically style static form fields on page load
document.addEventListener('DOMContentLoaded', () => {
    styleFormFields();
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
                        window.location.href = result.data.redirect || '/';
                    } else {
                        content.innerHTML = result.text;
                        styleFormFields(content);
                    }
                })
                .catch(err => {
                    console.error('Error submitting form:', err);
                });
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

// Automatically submit the form on checkbox changes
function submitSearchForm() {
    const form = document.getElementById('search-filter-form');
    if (form) {
        form.submit();
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

// Automatically open profile drawer if '?profile=1' is in query string
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('profile')) {
        toggleProfileDrawer();
        // Clean up URL without reloading
        const cleanUrl = window.location.pathname + window.location.hash;
        window.history.replaceState({}, document.title, cleanUrl);
    }
});
