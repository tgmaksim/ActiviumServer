(function(){
    const screenshotsBox = document.getElementById('screenshotsBox');
    const screenshots = document.getElementById('screenshots');

    function updateScreenshotsWidth() {
        screenshots.style.maxWidth = `${screenshotsBox.clientWidth - 30}px`;
    }

    updateScreenshotsWidth();
    window.addEventListener('resize', updateScreenshotsWidth);
})();