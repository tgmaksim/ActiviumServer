let activePswpInstance = null;

function initImageZoom() {
    const images = document.querySelectorAll('.content img:not([data-no-zoom])');

    images.forEach((img) => {
        if (img.dataset.zoomInitialized) return;
        img.dataset.zoomInitialized = "true";

        img.style.cursor = 'pointer';

        img.addEventListener('click', () => {
            const items = [{
                src: img.src,
                w: img.naturalWidth || img.width || 800,
                h: img.naturalHeight || img.height || 600
            }];

            const pswp = new PhotoSwipe({
                dataSource: items,
                bgOpacity: 0.9,
                showHideAnimationType: 'zoom'
            });

            activePswpInstance = pswp;

            if (window.AndroidBridge) {
                AndroidBridge.setImageOverlayVisible(true);
            }

            pswp.on('destroy', () => {
                activePswpInstance = null;
                if (window.AndroidBridge) {
                    AndroidBridge.setImageOverlayVisible(false);
                }
            });

            pswp.init();
        });
    });
}

function closePhotoSwipe() {
    if (activePswpInstance) {
        activePswpInstance.close();
    }
}


if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', initImageZoom);
} else {
    initImageZoom();
}