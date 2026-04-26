function darkTheme() {
    document.documentElement.setAttribute('data-theme', 'dark');
}

function updateCountViewings(count) {
    document.getElementById('count_viewings').innerText = `👁 ${count}`;
}

function updateCountLikes(count) {
    document.getElementById('count_likes').innerText = `👍 ${count}`;
}
