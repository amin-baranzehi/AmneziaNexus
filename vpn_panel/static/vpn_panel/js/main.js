document.addEventListener('DOMContentLoaded', () => {
    // Modal Logic
    const modal = document.querySelector('.modal');
    const toggleModal = () => {
        if (!modal) return;
        modal.classList.toggle('opacity-0');
        modal.classList.toggle('pointer-events-none');
        document.body.classList.toggle('modal-active');
    };

    const modalOpen = document.querySelectorAll('.modal-open');
    modalOpen.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            toggleModal();
        });
    });

    const modalClose = document.querySelectorAll('.modal-close');
    modalClose.forEach(button => {
        button.addEventListener('click', toggleModal);
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal && !modal.classList.contains('opacity-0')) {
            toggleModal();
        }
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

