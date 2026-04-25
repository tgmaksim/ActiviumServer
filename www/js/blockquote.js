document.querySelectorAll('blockquote[expandable]').forEach(el => {
    const text = el.textContent.trim();

    const previewLength = 32;
    const preview = text.length > previewLength
        ? text.slice(0, previewLength) + '…'
        : text;

    const wrapper = document.createElement('details');
    wrapper.className = 'expandable-quote';

    const summary = document.createElement('summary');
    summary.textContent = preview;

    const content = document.createElement('div');
    content.className = 'quote-content';
    content.innerHTML = el.innerHTML;

    wrapper.appendChild(summary);
    wrapper.appendChild(content);

    el.replaceWith(wrapper);
});