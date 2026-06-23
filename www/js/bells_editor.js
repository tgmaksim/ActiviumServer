const MAX_LESSONS = 20;

const MONTH_NAMES = [
    'Янв', 'Фев', 'Мар', 'Апр',
    'Май', 'Июн', 'Июл', 'Авг',
    'Сен', 'Окт', 'Ноя', 'Дек'
];

const WEEKDAY_NAMES = [
    'Пн',
    'Вт',
    'Ср',
    'Чт',
    'Пт',
    'Сб',
    'Вс'
];

const bellsList = document.getElementById('bells-list');

const modalBackdrop = document.getElementById('modal-backdrop');

const modalTitle = document.getElementById('modal-title');

const startInput = document.getElementById('start-time');
const endInput = document.getElementById('end-time');

const monthsSelector = document.getElementById('months-selector');
const weekdaysSelector = document.getElementById('weekdays-selector');
const emptyState = document.getElementById('empty-state');

let bells = [];
let editIndex = null;
let modalOpened = false;
let selectedMonths = [];
let selectedWeekdays = [];

function loadInitialData() {

    const params =
        new URLSearchParams(window.location.search);

    const bellsRaw = params.get('bells');
    const monthsRaw = params.get('months');
    const weekdaysRaw = params.get('weekdays');

    try {

        bells = bellsRaw
            ? JSON.parse(decodeURIComponent(bellsRaw))
            : [];

    } catch {

        bells = [];
    }

    try {

        selectedMonths = monthsRaw
            ? JSON.parse(decodeURIComponent(monthsRaw))
            : [];

    } catch {

        selectedMonths = [];
    }

    try {

        selectedWeekdays = weekdaysRaw
            ? JSON.parse(decodeURIComponent(weekdaysRaw))
            : [];

    } catch {

        selectedWeekdays = [];
    }
}

function render() {
    bellsList.innerHTML = '';

    bells.forEach((item, index) => {

        const row = document.createElement('div');
        row.className = 'bell-item';

        row.innerHTML = `
            <div class="bell-time">
                ${item.start} — ${item.end}
            </div>

            <div class="actions">
                <button class="icon-btn edit-btn">
                    ✏️
                </button>

                <button class="icon-btn delete-btn">
                    ❌
                </button>
            </div>
        `;

        row.querySelector('.edit-btn')
            .addEventListener('click', () => openEdit(index));

        row.querySelector('.delete-btn')
            .addEventListener('click', () => {

                tg.showConfirm(
                    'Удалить урок?',
                    confirmed => {

                        if (!confirmed) {
                            return;
                        }

                        bells.splice(index, 1);

                        render();
                    }
                );
            });

        bellsList.appendChild(row);
    });

    emptyState.style.display =
    bells.length
        ? 'none'
        : 'block';
}

function renderMonths() {

    monthsSelector.innerHTML = '';

    MONTH_NAMES.forEach((name, index) => {

        const month = index + 1;

        const button =
            document.createElement('button');

        button.className = 'chip';

        if (selectedMonths.includes(month)) {
            button.classList.add('selected');
        }

        button.textContent = name;

        button.onclick = () => {

            if (selectedMonths.includes(month)) {

                selectedMonths =
                    selectedMonths.filter(
                        m => m !== month
                    );

            } else {

                selectedMonths.push(month);
            }

            renderMonths();
        };

        monthsSelector.appendChild(button);
    });
}

function renderWeekdays() {

    weekdaysSelector.innerHTML = '';

    WEEKDAY_NAMES.forEach((name, weekday) => {

        const button =
            document.createElement('button');

        button.className = 'chip';

        if (
            selectedWeekdays.includes(
                weekday
            )
        ) {
            button.classList.add('selected');
        }

        button.textContent = name;

        button.onclick = () => {

            if (
                selectedWeekdays.includes(
                    weekday
                )
            ) {

                selectedWeekdays =
                    selectedWeekdays.filter(
                        d => d !== weekday
                    );

            } else {

                selectedWeekdays.push(
                    weekday
                );
            }

            renderWeekdays();
        };

        weekdaysSelector.appendChild(button);
    });
}

function openCreate() {

    if (bells.length >= MAX_LESSONS) {

        tg.showPopup({
            title: 'Ошибка',
            message: 'Можно добавить не более 20 уроков.',
            buttons: [{type: 'ok'}]
        });

        return;
    }

    editIndex = null;

    startInput.value = '';
    endInput.value = '';

    modalTitle.textContent = 'Новый урок';

    openModal();
}

function openEdit(index) {

    editIndex = index;

    startInput.value = bells[index].start;
    endInput.value = bells[index].end;

    modalTitle.textContent = 'Редактирование';

    openModal();
}

function openModal() {

    modalOpened = true;

    modalBackdrop.classList.remove('hidden');

    tg.MainButton.setText('Добавить');
    tg.MainButton.show();

    tg.SecondaryButton.setText('Отмена');
    tg.SecondaryButton.show();

    tg.BackButton.show();
}

function closeModal() {

    modalOpened = false;

    modalBackdrop.classList.add('hidden');

    configureMainButtons();

    tg.BackButton.hide();
}

function toMinutes(value) {

    const [h, m] = value.split(':').map(Number);

    return h * 60 + m;
}

function validateLesson(start, end) {

    if (toMinutes(start) >= toMinutes(end)) {

        tg.showPopup({
            title: 'Ошибка',
            message: 'Время начала должно быть раньше времени окончания.',
            buttons: [{type: 'ok'}]
        });

        return false;
    }

    const copy = [...bells];

    const lesson = {
        start,
        end
    };

    if (editIndex === null) {
        copy.push(lesson);
    } else {
        copy[editIndex] = lesson;
    }

    for (let i = 0; i < copy.length - 1; i++) {

        const currentEnd =
            toMinutes(copy[i].end);

        const nextStart =
            toMinutes(copy[i + 1].start);

        if (nextStart <= currentEnd) {

            tg.showPopup({
                title: 'Ошибка',
                message:
                    'Следующий урок должен начинаться позже окончания предыдущего.',
                buttons: [{type: 'ok'}]
            });

            return false;
        }
    }

    return true;
}

function saveLesson() {

    const start = startInput.value;
    const end = endInput.value;

    if (!start || !end) {

        tg.showPopup({
            title: 'Ошибка',
            message: 'Укажите время начала и окончания.',
            buttons: [{type: 'ok'}]
        });

        return;
    }

    if (!validateLesson(start, end)) {
        return;
    }

    const lesson = { start, end };

    if (editIndex === null) {
        bells.push(lesson);
    } else {
        bells[editIndex] = lesson;
    }

    closeModal();
    render();
}

function saveSchedule() {

    const payload = {

        months: [...selectedMonths],

        weekdays: [...selectedWeekdays],

        bells: bells.map(item => ({
            start: item.start,
            end: item.end,
            string: `${item.start} - ${item.end}`
        }))
    };

    if (!bells.length) {

        tg.showPopup({
            title: 'Пустое расписание',
            message: 'Отправить пустое расписание?',
            buttons: [
                {
                    id: 'yes',
                    type: 'default',
                    text: 'Да'
                },
                {
                    id: 'no',
                    type: 'cancel'
                }
            ]
        }, buttonId => {

            if (buttonId === 'yes') {

                tg.sendData(
                    JSON.stringify(payload)
                );

                tg.close();
            }
        });

        return;
    }

    tg.sendData(
        JSON.stringify(payload)
    );

    tg.close();
}

function configureMainButtons() {

    tg.MainButton.setText('Добавить');
    tg.MainButton.show();

    tg.SecondaryButton.setText('Сохранить');
    tg.SecondaryButton.show();
}

tg.MainButton.onClick(() => {

    if (modalOpened) {
        saveLesson();
    } else {
        openCreate();
    }
});

tg.SecondaryButton.onClick(() => {

    if (modalOpened) {
        closeModal();
    } else {
        saveSchedule();
    }
});

tg.BackButton.onClick(() => {

    if (modalOpened) {
        closeModal();
    }
});

loadInitialData();

renderMonths();
renderWeekdays();

render();

configureMainButtons();