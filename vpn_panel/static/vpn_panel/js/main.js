document.addEventListener('DOMContentLoaded', () => {
    // Modal Logic
    const toggleModal = () => {
        const modal = document.querySelector('.modal');
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

    // Ping Logic
    const pingButtons = document.querySelectorAll('.ping-btn');
    pingButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const configId = e.currentTarget.dataset.id;
            const latencySpan = document.getElementById(`latency-${configId}`);
            
            latencySpan.innerHTML = '<span class="animate-pulse text-gray-400">Pinging...</span>';
            
            try {
                const response = await fetch(`/config/${configId}/ping/`);
                const data = await response.json();
                
                let colorClass = 'text-gray-400';
                if (data.latency.includes('ms')) {
                    const ms = parseFloat(data.latency);
                    if (ms < 100) colorClass = 'text-green-500';
                    else if (ms < 250) colorClass = 'text-yellow-500';
                    else colorClass = 'text-red-500';
                } else if (data.latency === 'Timeout' || data.latency === 'Error') {
                    colorClass = 'text-red-500';
                }
                
                latencySpan.innerHTML = `<span class="${colorClass} font-mono">${data.latency}</span>`;
            } catch (error) {
                latencySpan.innerHTML = '<span class="text-red-500">Error</span>';
            }
        });
    });

    // Theme Switcher Logic
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        // Load preference
        if (localStorage.getItem('theme') === 'light') {
            document.body.classList.add('light-theme');
        }

        themeBtn.addEventListener('click', () => {
            document.body.classList.toggle('light-theme');
            const isLight = document.body.classList.contains('light-theme');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
        });
    }
});
