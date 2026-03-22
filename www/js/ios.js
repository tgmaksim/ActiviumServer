function scrollToIOSFaq() {
    const el = document.getElementById('faq-ios');
    if (!el) return;

    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    el.open = true;
}