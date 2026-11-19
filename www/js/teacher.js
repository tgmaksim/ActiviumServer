document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("reportForm");

    // Скрипт нужен только авторизованному учителю.
    if (!form) return;

    const classSelect = document.getElementById("classSelect");

    const subjectsToggle = document.getElementById("subjectsToggle");
    const subjectsPanel = document.getElementById("subjectsPanel");
    const subjectsStatus = document.getElementById("subjectsStatus");
    const subjectsList = document.getElementById("subjectsList");
    const subjectsSelection = document.getElementById("subjectsSelection");

    const reportButton = document.getElementById("reportButton");

    const withoutMarks = document.getElementById("withoutMarks");
    const average = document.getElementById("average");
    const rating = document.getElementById("rating");

    const withoutMarksValue = document.getElementById("withoutMarksValue");
    const averageValue = document.getElementById("averageValue");
    const ratingValue = document.getElementById("ratingValue");

    const selectedSubjectsInputs = document.getElementById("selectedSubjectsInputs");

    let loadedGroupId = null;
    let requestController = null;

    // Обновление подписи о выбранных предметах.
    function updateSelectionLabel() {
        const checkboxes = subjectsList.querySelectorAll(
            'input[type="checkbox"]'
        );

        const total = checkboxes.length;
        const selected = subjectsList.querySelectorAll(
            'input[type="checkbox"]:checked'
        ).length;

        if (total === 0) {
            subjectsSelection.textContent = "Предметы не загружены";
        } else if (selected === total) {
            subjectsSelection.textContent = "Все предметы";
        } else if (selected === 0) {
            subjectsSelection.textContent = "Предметы не выбраны";
        } else {
            subjectsSelection.textContent =
                `Выбрано: ${selected} из ${total}`;
        }
    }

    // Создание элемента списка предметов.
    function createSubjectItem(subject) {
        const label = document.createElement("label");
        label.className = "teacher-subject-item";

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = String(subject.id);

        // По умолчанию выбраны все предметы.
        checkbox.checked = true;

        const name = document.createElement("span");
        name.textContent = subject.name;

        checkbox.addEventListener("change", updateSelectionLabel);

        label.append(checkbox, name);

        return label;
    }

    // Загрузка предметов выбранного класса.
    async function loadSubjects(groupId) {
        if (loadedGroupId === groupId) return;

        if (requestController) {
            requestController.abort();
        }

        const controller = new AbortController();
        requestController = controller;

        subjectsList.replaceChildren();

        subjectsStatus.hidden = false;
        subjectsStatus.className = "teacher-subjects-status loading";
        subjectsStatus.textContent = "Загружаем список предметов…";

        try {
            const params = new URLSearchParams({ groupId });

            const response = await fetch(
                `/teacher/listSubjects?${params.toString()}`,
                {
                    method: "GET",
                    credentials: "same-origin",
                    headers: {
                        "Accept": "application/json"
                    },
                    signal: controller.signal
                }
            );

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            const subjects = await response.json();

            if (!Array.isArray(subjects)) {
                throw new Error("Сервер вернул некорректный список предметов.");
            }

            // Проверяем, что за время запроса класс не изменился.
            if (classSelect.value !== groupId) return;

            const validSubjects = subjects.filter(subject =>
                subject &&
                subject.id !== undefined &&
                subject.name !== undefined
            );

            if (validSubjects.length === 0) {
                subjectsStatus.className = "teacher-subjects-status";
                subjectsStatus.textContent =
                    "Для выбранного класса предметы не найдены.";

                loadedGroupId = groupId;
                updateSelectionLabel();
                return;
            }

            const fragment = document.createDocumentFragment();

            validSubjects.forEach(subject => {
                fragment.append(createSubjectItem(subject));
            });

            subjectsList.append(fragment);

            // Убираем класс loading вместе с анимацией.
            subjectsStatus.className = "teacher-subjects-status";
            subjectsStatus.hidden = true;

            loadedGroupId = groupId;

            updateSelectionLabel();

        } catch (error) {
            if (error.name === "AbortError") return;

            subjectsStatus.hidden = false;
            subjectsStatus.className = "teacher-subjects-status error";
            subjectsStatus.textContent =
                "Не удалось загрузить предметы. Попробуйте ещё раз.";

            console.error("Ошибка загрузки предметов:", error);

        } finally {
            if (requestController === controller) {
                requestController = null;
            }
        }
    }

    // Открытие и закрытие списка предметов.
    subjectsToggle.addEventListener("click", async () => {
        const isOpen =
            subjectsToggle.getAttribute("aria-expanded") === "true";

        if (isOpen) {
            subjectsToggle.setAttribute("aria-expanded", "false");
            subjectsPanel.hidden = true;
            return;
        }

        subjectsToggle.setAttribute("aria-expanded", "true");
        subjectsPanel.hidden = false;

        const groupId = classSelect.value;

        if (!groupId) {
            subjectsStatus.hidden = false;
            subjectsStatus.className = "teacher-subjects-status";
            subjectsStatus.textContent = "Сначала выберите класс.";
            return;
        }

        await loadSubjects(groupId);
    });

    // При смене класса сбрасываем загруженный список.
    classSelect.addEventListener("change", () => {
        if (requestController) {
            requestController.abort();
            requestController = null;
        }

        loadedGroupId = null;

        subjectsList.replaceChildren();
        subjectsPanel.hidden = true;
        subjectsToggle.setAttribute("aria-expanded", "false");

        subjectsStatus.hidden = false;
        subjectsStatus.className = "teacher-subjects-status";
        subjectsStatus.textContent =
            "Нажмите, чтобы загрузить предметы выбранного класса.";

        updateSelectionLabel();
    });

    // Подготовка обычной POST-формы для скачивания PDF.
    form.addEventListener("submit", () => {
        const groupId = classSelect.value;

        // Передаём все логические параметры явно: true или false.
        withoutMarksValue.value = String(withoutMarks.checked);
        averageValue.value = String(average.checked);
        ratingValue.value = String(rating.checked);

        // Указываем groupId именно в query string.
        const params = new URLSearchParams({ groupId });
        form.action = `/teacher/report?${params.toString()}`;

        // Передаём выбранные предметы отдельными параметрами.
        selectedSubjectsInputs.replaceChildren();

        const selectedSubjects = subjectsList.querySelectorAll(
            'input[type="checkbox"]:checked'
        );

        selectedSubjects.forEach(subject => {
            const input = document.createElement("input");

            input.type = "hidden";
            input.name = "listSubjects";
            input.value = subject.value;

            selectedSubjectsInputs.append(input);
        });

        // Показываем анимацию формирования отчёта.
        reportButton.disabled = true;
        reportButton.classList.add("loading");

        // После завершения скачивания PDF возвращаем кнопку в исходное состояние.
        window.addEventListener("focus", () => {
            setTimeout(() => {
                reportButton.disabled = false;
                reportButton.classList.remove("loading");
            }, 500);
        }, { once: true });
    });
});
