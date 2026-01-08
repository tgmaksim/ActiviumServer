(function(){
    const themeToggle = document.getElementById('themeToggle');
    const themeSvg = document.getElementById('themeSvg');
    const root = document.documentElement;
    const PAGE = document.getElementById('page');

    function applyTheme(theme){
        if(theme === 'dark') {
            root.setAttribute('data-theme','dark');
            themeSvg.style.fill = 'white';
            themeToggle.alt = 'Тема — тёмная';
        } else {
            root.removeAttribute('data-theme');
            themeSvg.style.fill = 'black';
            themeToggle.alt = 'Тема — светлая';
        }
        localStorage.setItem('site-theme', theme);
    }

    const saved = localStorage.getItem('site-theme') || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    applyTheme(saved);

    themeToggle.addEventListener('click', function(e) {
        const cur = localStorage.getItem('site-theme') === 'dark' ? 'dark' : 'light';
        applyTheme(cur === 'dark' ? 'light' : 'dark');
    });
})();