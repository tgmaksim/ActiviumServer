const subjectInput = document.getElementById('subject');
const placeInput = document.getElementById('place');

const startTimeInput = document.getElementById('start-time');

const endTimeInput = document.getElementById('end-time');

const dateInput = document.getElementById('date');

const timeError = document.getElementById('time-error');


function getQueryParameters() {
    const params = new URLSearchParams(window.location.search);

    return {
        subject: params.get('subject') || '',
        place: params.get('place') || '',
        date: params.get('date') || '',
        startTime: params.get('start_time') || '',
        endTime: params.get('end_time') || ''
    };
}


function timeToMinutes(value) {
    if (!value) {
        return NaN;
    }

    const [hours, minutes] = value.split(':').map(Number);

    if (
        Number.isNaN(hours) ||
        Number.isNaN(minutes)
    ) {
        return NaN;
    }

    return hours * 60 + minutes;
}

function loadData() {
    const data = getQueryParameters();

    subjectInput.value = data.subject;
    placeInput.value = data.place;

    dateInput.value = data.date;

    startTimeInput.value = data.startTime;

    endTimeInput.value = data.endTime;
}


function clearTimeError() {
    timeError.textContent = '';
    timeError.classList.add('hidden');
}


function showTimeError(message) {
    timeError.textContent = message;
    timeError.classList.remove('hidden');
}


function validateTime() {
    clearTimeError();

    const start = timeToMinutes(startTimeInput.value);
    const end = timeToMinutes(endTimeInput.value);

    if (
        Number.isNaN(start) ||
        Number.isNaN(end)
    ) {
        return true;
    }

    if (start >= end) {
        showTimeError(
            'Время начала должно быть раньше времени окончания.'
        );

        return false;
    }

    return true;
}

function save() {
    if (!validateTime()) {
        return;
    }

    const payload = {
        subject: subjectInput.value.trim(),

        place: placeInput.value.trim(),

        date: dateInput.value,

        start_time: startTimeInput.value,

        end_time: endTimeInput.value
    };

    tg.sendData(
        JSON.stringify(payload)
    );
}

function cancel() {
    tg.close();
}

function configureButtons() {
    tg.MainButton.setText('Сохранить');
    tg.MainButton.show();

    tg.SecondaryButton.setText('Отмена');
    tg.SecondaryButton.show();
}


tg.MainButton.onClick(() => {
    save();
});


tg.SecondaryButton.onClick(() => {
    cancel();
});

startTimeInput.addEventListener(
    'change',
    validateTime
);

endTimeInput.addEventListener(
    'change',
    validateTime
);

loadData();
configureButtons();