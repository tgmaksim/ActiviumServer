const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

async function toggleLike(reviewId, btn) {
    const isActive = btn.classList.contains('active');

    btn.disabled = true;

    try {
        const path = isActive ? '/reviews/deleteReviewLike/0' : '/reviews/likeReview/0'
        const res = await fetch(path + '?reviewId=' + reviewId, {
            method: isActive ? 'DELETE' : 'POST',
            headers: {
                'X-CSRF-Token': csrfToken
            }
        });

        if (!res.ok) throw new Error();

        const data = await res.json();

        if (data.error && data.error.errorMessage) {
            alert(data.error.errorMessage)
        } else {
            const countEl = btn.querySelector('.like-count');
            countEl.textContent = data.answer.review.likes;

            btn.classList.toggle('active', !isActive);
        }
    } catch {
        alert('Ошибка');
    }

    setTimeout(() => btn.disabled = false, 500);
}

function loadMoreReviews() {
    const btn = document.querySelector('[data-next-offset]');
    if (!btn) return;

    const nextOffset = btn.dataset.nextOffset;
    if (!nextOffset) return;

    const url = new URL(window.location);

    url.searchParams.set('likes-offset', nextOffset);
    url.hash = 'reviews'

    window.location.href = url.toString();
}

function changeSort(sort) {
    const url = new URL(window.location);

    url.searchParams.set('likes-sort', sort);
    url.searchParams.set('likes-offset', 0);
    url.hash = 'reviews'

    window.location.href = url.toString();
}