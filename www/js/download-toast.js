(function() {
    const downloadBtn = document.getElementById('downloadApk');
    const toast = document.getElementById('downloadToast');
    const closeBtn = document.getElementById('toastClose');
    const goSiteBtn = document.getElementById('toastGoSite');

    if (!downloadBtn || !toast) return;

    function showToast() {
        toast.hidden = false;

        setTimeout(() => {
            toast.hidden = true;
        }, 8000);
    }

    function hideToast() {
        toast.hidden = true;
    }

    downloadBtn.addEventListener('click', () => {
        showToast();
    });

    closeBtn?.addEventListener('click', hideToast);

    goSiteBtn?.addEventListener('click', () => {
        hideToast();

        const block = document.getElementById('screenshotsBox');
        if (block) {
            block.scrollIntoView({ behavior: 'smooth' });
        }
    });
})();