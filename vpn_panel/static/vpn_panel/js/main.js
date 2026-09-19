document.addEventListener('DOMContentLoaded', () => {
    // Universal Modal Handlers
    const openModal = (modalEl) => {
        if (!modalEl) return;
        modalEl.classList.remove('opacity-0', 'pointer-events-none');
        document.body.classList.add('modal-active');
    };

    const closeModal = (modalEl) => {
        if (!modalEl) return;
        modalEl.classList.add('opacity-0', 'pointer-events-none');
        const anyOpen = document.querySelectorAll('.modal:not(.opacity-0)');
        if (anyOpen.length === 0) {
            document.body.classList.remove('modal-active');
        }
    };

    const closeAllModals = () => {
        document.querySelectorAll('.modal').forEach(m => {
            m.classList.add('opacity-0', 'pointer-events-none');
        });
        document.body.classList.remove('modal-active');
    };

    // Open Create Modal
    const createModal = document.querySelector('.modal-create');
    const createBtns = document.querySelectorAll('.modal-open');
    createBtns.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            openModal(createModal);
        });
    });

    // Close Modals on close button or overlay click
    const modalCloses = document.querySelectorAll('.modal-close');
    modalCloses.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const parentModal = e.target.closest('.modal');
            if (parentModal) {
                closeModal(parentModal);
            } else {
                closeAllModals();
            }
        });
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });

    // View Configuration Logic
    const viewModal = document.getElementById('view-config-modal');
    const viewModalName = document.getElementById('view-modal-name');
    const viewModalEndpoint = document.getElementById('view-modal-endpoint');
    const viewModalContent = document.getElementById('view-modal-content');
    const copyConfigBtn = document.getElementById('copy-config-btn');
    const copyText = document.getElementById('copy-text');
    const copyIcon = document.getElementById('copy-icon');

    const viewBtns = document.querySelectorAll('.view-config-btn');
    viewBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const configId = btn.dataset.id;
            const configName = btn.dataset.name;
            const configEndpoint = btn.dataset.endpoint;
            const rawScript = document.getElementById(`config-raw-${configId}`);
            const rawContent = rawScript ? rawScript.textContent : '';

            if (viewModalName) viewModalName.textContent = configName;
            if (viewModalEndpoint) viewModalEndpoint.textContent = configEndpoint ? `Endpoint: ${configEndpoint}` : '';
            if (viewModalContent) viewModalContent.textContent = rawContent;

            // Reset copy button state
            if (copyText) copyText.textContent = 'Copy';
            if (copyIcon) {
                copyIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>';
                copyIcon.classList.remove('text-emerald-400');
                copyIcon.classList.add('text-gray-400');
            }

            openModal(viewModal);
        });
    });

    // Copy to Clipboard Logic
    if (copyConfigBtn) {
        copyConfigBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const contentToCopy = viewModalContent ? viewModalContent.textContent : '';
            if (!contentToCopy) return;

            try {
                if (navigator.clipboard && window.isSecureContext) {
                    await navigator.clipboard.writeText(contentToCopy);
                } else {
                    // Fallback for non-https/local
                    const textArea = document.createElement('textarea');
                    textArea.value = contentToCopy;
                    textArea.style.position = 'fixed';
                    textArea.style.opacity = '0';
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                }

                if (copyText) copyText.textContent = 'Copied! ✓';
                if (copyIcon) {
                    copyIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>';
                    copyIcon.classList.remove('text-gray-400');
                    copyIcon.classList.add('text-emerald-400');
                }

                setTimeout(() => {
                    if (copyText) copyText.textContent = 'Copy';
                    if (copyIcon) {
                        copyIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>';
                        copyIcon.classList.remove('text-emerald-400');
                        copyIcon.classList.add('text-gray-400');
                    }
                }, 2000);
            } catch (err) {
                console.error('Failed to copy configuration:', err);
            }
        });
    }

    // Edit Configuration Logic
    const editModal = document.getElementById('edit-config-modal');
    const editForm = document.getElementById('edit-config-form');
    const editNameInput = document.getElementById('edit-config-name');
    const editContentInput = document.getElementById('edit-config-content');
    const editActiveWarning = document.getElementById('edit-active-warning');

    const editBtns = document.querySelectorAll('.edit-config-btn');
    editBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const configId = btn.dataset.id;
            const configName = btn.dataset.name;
            const isActive = btn.dataset.active === 'true';
            const rawScript = document.getElementById(`config-raw-${configId}`);
            const rawContent = rawScript ? rawScript.textContent : '';

            if (editForm) editForm.action = `/config/${configId}/edit/`;
            if (editNameInput) editNameInput.value = configName;
            if (editContentInput) editContentInput.value = rawContent;

            if (editActiveWarning) {
                if (isActive) {
                    editActiveWarning.classList.remove('hidden');
                } else {
                    editActiveWarning.classList.add('hidden');
                }
            }

            openModal(editModal);
        });
    });

    // Ping Logic (Updates all instances across mobile cards and desktop tables)
    const pingButtons = document.querySelectorAll('.ping-btn');
    pingButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const configId = e.currentTarget.dataset.id;
            const latencySpans = document.querySelectorAll(`.latency-${configId}, #latency-${configId}`);
            const currentPingBtns = document.querySelectorAll(`.ping-btn[data-id="${configId}"]`);
            
            // Set loading state on all matching latency spans
            latencySpans.forEach(span => {
                span.innerHTML = '<span class="animate-pulse text-indigo-400 text-xs sm:text-sm font-mono">Pinging...</span>';
            });

            currentPingBtns.forEach(b => {
                b.disabled = true;
                b.classList.add('opacity-50', 'animate-spin');
            });
            
            try {
                const response = await fetch(`/config/${configId}/ping/`);
                const data = await response.json();
                
                let colorClass = 'text-gray-400';
                if (data.latency && data.latency.includes('ms')) {
                    const ms = parseFloat(data.latency);
                    if (ms < 100) colorClass = 'text-emerald-400';
                    else if (ms < 250) colorClass = 'text-amber-400';
                    else colorClass = 'text-rose-400';
                } else if (data.latency === 'Timeout' || data.latency === 'Error') {
                    colorClass = 'text-rose-400';
                }
                
                latencySpans.forEach(span => {
                    span.innerHTML = `<span class="${colorClass} font-mono font-medium text-xs sm:text-sm">${data.latency}</span>`;
                });
            } catch (error) {
                latencySpans.forEach(span => {
                    span.innerHTML = '<span class="text-rose-400 font-mono text-xs sm:text-sm">Error</span>';
                });
            } finally {
                currentPingBtns.forEach(b => {
                    b.disabled = false;
                    b.classList.remove('opacity-50', 'animate-spin');
                });
            }
        });
    });
});


