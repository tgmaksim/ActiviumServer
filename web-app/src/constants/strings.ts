export const strings = {
    appName: "Активиум",

    errorApi: "Произошла ошибка на сервере…",
    errorInternet: "Нет подключения к интернету",
    errorServer: "Сервер в данное время недоступен",
    ok: "Ок",

    notificationBroadcastTitle: "Фоновое действие",
    notificationBroadcastSuccessText: "Успешно выполнено",
    notificationBroadcastUnsuccessText:
        "Ошибка при выполнении, откройте приложение",
    notificationBroadcastUnknownText:
        "Кнопка не поддерживается в данной версии приложения",

    changeActiveChild: (profile: string) =>
        `Профиль сменен на ${profile}`,

    titleDialogPermissionDnevnikNotifications:
        "Разрешение на уведомления",
    messageDialogPermissionDnevnikNotifications:
        "Предоставьте разрешения на уведомления. Если окно не откроется, посетите настройки",
    buttonDialogPermissionDnevnikNotifications: "Предоставить",

    hello:
        "Активиум — это приложение для школьников, которое поможет всегда узнавать о новых оценках, не забывать о внеурочных занятиях и быть в курсе всех мероприятий",
    loginWithDnevnik: "Войти через Дневник.ру",
    errorLogin: "Произошла ошибка при попытке авторизоваться",

    highlightPerson: "Выделить",
    unhighlightPerson: "Снять",
    titleDialogHighlightAtMarks: "Выделить одноклассника",
    messageDialogHighlightAtMarks:
        "Выделение одноклассников можно сделать на странице Оценок",

    menuItemSchedule: "Расписание",
    lessonNumber: (number: number) => `${number}.`,
    homeworkEmoji: "✏️",
    homeworkDocumentEmoji: "📎",
    homeworkDocumentNotFound: "Файл",
    noteEmoji: "📝",
    errorSchedule: "Произошла ошибка при загрузке расписания",

    noteNotFound: "Заметка отсутствует",

    lessonNoteAdd: "Добавить заметку",
    lessonNoteEdit: "Изменить заметку",
    lessonNoteDelete: "Удалить заметку",
    sendPraise: "Похвалить ребенка",
    openRating: "Другие оценки за урок",
    openLessonDnevnikru: "Открыть в Дневнике.ру",

    titleDialogCreateNote: "Добавить заметку",
    titleDialogEditNote: "Изменить заметку",
    messageDialogCreateNote: "Напишите текст заметки",
    switchPublicNote: "Показывать заметку родителю",
    noteRemindIn: "Напоминание",
    noteRemindDatetime: "Выбрать",
    noteRemindDatetimeFormat: (date: string, time: string) =>
        `${date} в ${time}`,
    titleDialogNoteRemindDateEditor: "Выберите дату",
    titleDialogNoteRemindTimeEditor: "Выберите время",
    buttonDialogCreateNote: "Сохранить заметку",
    errorNote: "Произошла ошибка при сохранении заметки",
    errorDeleteNote: "Произошла ошибка при удалении заметки",

    titleDialogNoNoteText: "Пустая заметка",
    messageDialogNoNoteText:
        "Нельзя создать заметку с пустым текстом",
    buttonDialogNoNoteText: "А, точно!",

    titleDialogDeleteNote: "Удалить заметку",
    messageDialogDeleteNote:
        "Удалить заметку об уроке? Это действие нельзя отменить!",
    buttonDialogDeleteNote: "Да, удалить",

    titleDialogSendPraise: "Похвалить ребенка",
    messageDialogSendPraise:
        "Напишите сообщение (необязательно)",
    buttonDialogSendPraise: "Похвалить",
    praiseTextCounter: (current: number, max: number) =>
        `${current}/${max}`,
    praiseSent: "Похвала отправлена",
    errorPraise: "Произошла ошибка при отправке похвалы",

    myMark: "Ваша оценка:",
    myMarks: "Ваши оценки:",
    personNumber: (number: number) => `${number}.`,
    ratingInfo: (
        subject: string,
        period: string,
        additional: string,
    ) =>
        `Оценки класса по предмету ${subject} (${period})${additional}`,
    ratingInfoTime: (mark: string) =>
        `. Вам выставили ${mark}`,
    avgGroupLessonMark: "Средний балл класса на уроке:",
    avgGroupWorkMark: "В среднем по классу:",
    errorLessonRatingStats:
        "Произошла ошибка при загрузке статистики урока",

    menuItemMarks: "Оценки",
    classRating: "📊 Рейтинг в классе",
    oldMarkInfo: "Прошлое место в рейтинге",
    marksCurrent: "Текущий период",
    marksYear: "Год",
    lastMarkDetailNoWork: (date: string) =>
        `За ${date}`,
    lastMarkDetail: (mark: string, date: string) =>
        `${mark} за ${date}`,
    subjectRatingInfo: (subject: string) =>
        `Рейтинг в классе по предмету ${subject}`,
    classRatingInfo:
        "Общий рейтинг в классе по всем предметам",
    errorMarks: "Произошла ошибка при загрузке оценок",

    menuItemSchool: "Актив",
    noSchoolPosts:
        "Пока что здесь нет публикаций. Как только Ваше учебное заведение опубликует новость, ее можно будет прочитать на этой странице",
    errorMarkSchoolPost:
        "Произошла ошибка при пометке поста",
    errorNewSchoolPosts:
        "Произошла ошибка при проверке новых постов",
    errorSchoolPosts:
        "Произошла ошибка при получении школьных постов",
    schoolPostUpdated: "· изменено",
    schoolPostSchedule: (event: string) =>
        `📅 Мероприятие: ${event}`,
    schoolPostViewings: (count: number) =>
        `👁 ${count}`,

    menuItemSettings: "Настройки",
    settings: "Настройки",

    settingsTheme: "Использовать темную тему",
    settingsEaNotifications:
        "Напоминать о внеурочных занятиях",
    settingsMarksNotifications:
        "Уведомлять об оценках",
    errorMarksNotifications:
        "Произошла ошибка при загрузке статуса уведомлений об оценках",
    errorEaNotifications:
        "Произошла ошибка при загрузке статуса уведомлений о внеурочных занятиях",
    settingsShowNullSubjectMarks:
        "Показывать предметы без оценок",
    settingsSchedulePeriod: "Диапазон расписания",
    scheduleRangeLabelToday: "сегодня",
    scheduleRangeLabelTomorrow: "завтра",
    scheduleRangeLabelFrom: (days: number) =>
        `${days} до`,
    scheduleRangeLabelTo: (days: number) =>
        `${days} после`,
    settingsScheduleWarning:
        "Большой диапазон расписания влияет на скорость загрузки",
    settingsLastMarksPeriod: "Период последних оценок",
    lastMarksLabel: (days: number) => {
        const mod10 = days % 10;
        const mod100 = days % 100;

        if (mod10 === 1 && mod100 !== 11) {
            return `за ${days} день`;
        }

        if (
            mod10 >= 2 &&
            mod10 <= 4 &&
            (mod100 < 10 || mod100 >= 20)
        ) {
            return `за ${days} дня`;
        }

        return `за ${days} дней`;
    },
    settingsLastMarksWarning:
        "Большой период последних оценок влияет на скорость загрузки",

    update: "⚠️ Обновление",
    updateDescription: (
        version: string,
        versionCode: number,
        description: string,
    ) => `${version} (${versionCode})\n${description}`,
    updateButton: "Обновить",
    buttonDialogNewVersion: "Настройки",
    errorCheckVersion:
        "Произошла ошибка при проверке версии",
    errorInfoNotifications:
        "Произошла ошибка при загрузке личных уведомлений",

    activeProfile: "Активный профиль",
    loadActiveProfile: "Загрузка…",
    contentDescriptionArrow: "v",
    selectProfile: "Выберите активный профиль",
    noChild: "Не выбран",
    errorChildren:
        "Произошла ошибка при загрузке активного профиля",

    review: "Отзыв",
    reviewMeta: (
        author: string,
        date: string,
        marker: string,
    ) => `${author} • ${date}${marker}`,
    reviewEditMarker: "изменен",
    reviewModerationMarker: "на модерации",
    writeReview: "Написать отзыв",
    editReview: "Изменить отзыв",
    deleteReview: "Удалить отзыв",
    openAllReviews: "Открыть отзывы на сайте",
    errorReview: "Произошла ошибка при загрузке отзыва",

    reviewEditorNewTitle: "Написать отзыв",
    reviewEditorEditTitle: "Изменить отзыв",
    reviewTextCounter: (current: number, max: number) =>
        `${current}/${max}`,
    reviewTextHint: "Напишите отзыв (необязательно)",
    send: "Отправить",
    titleDialogReviewNoStars: "Оценка",
    messageDialogReviewNoStars:
        "Поставьте от 1 до 5 звезд, пожалуйста",
    buttonDialogReviewNoStars: "А, точно!",
    messageDialogReviewSent:
        "Отзыв отправлен на модерацию. После проверки вам придет уведомление",
    buttonDialogReviewSent: "Ок",
    titleDialogReviewSent: "Отзыв отправлен",
    errorCreateReview:
        "Произошла ошибка при отправке отзыва",

    messageDialogDeleteReview:
        "Удалить Ваш отзыв? Это действие нельзя отменить!",
    buttonDialogDeleteReview: "Да, удалить",
    errorDeleteReview:
        "Произошла ошибка при удалении отзыва",

    referral: "Приглашения",
    referralInfo:
        "Приглашайте своих друзей и знакомых в Активиум по реферальной ссылке",
    referralCountZero: "🤜🤛 Вы не приглашали друзей",
    referralCount: (count: number) => {
        const mod10 = count % 10;
        const mod100 = count % 100;

        if (mod10 === 1 && mod100 !== 11) {
            return `🤜🤛 Вы пригласили ${count} друга`;
        }

        if (
            mod10 >= 2 &&
            mod10 <= 4 &&
            (mod100 < 10 || mod100 >= 20)
        ) {
            return `🤜🤛 Вы пригласили ${count} друга`;
        }

        return `🤜🤛 Вы пригласили ${count} друзей`;
    },
    activeRelativesChildren: (
        school: string,
        current: number,
        total: number,
    ) => `🧒 Дети в ${school}: ${current} из ${total}`,
    allActiveRelativesChildren: (school: string) =>
        `🧒 Ваши дети уже в ${school}!`,
    activeRelativesParents: (
        school: string,
        current: number,
        total: number,
    ) => `👩👨 Родители в ${school}: ${current} из ${total}`,
    allActiveRelativesParents: (school: string) =>
        `👩👨 Ваши родители уже в ${school}!`,
    meReferral: (name: string) =>
        `📥 Вас пригласили: ${name}`,
    share: "Пригласить",
    shareText: (url: string) =>
        `Я приглашаю в Активиум — приложения для учеников и их родителей\n\nСкачивание на сайте: ${url}`,
    errorReferral:
        "Произошла ошибка при загрузке реферальной программы",

    account: "Аккаунт",
    accountInfo:
        "Ваш профиль в приложении связан с аккаунтом в Дневнике.ру. Все предоставленные данные используются только в целях работы приложения и доступны только Вам в приложении",
    logout: "Выйти из профиля",

    about: "О приложении",
    appInfo:
        "Удобно и бесплатно пользуйтесь всеми возможностями Дневника.ру в своем телефоне и всегда будьте в курсе новостей и мероприятий школы",
    openSite: "Открыть сайт",

    version: (version: string, versionCode: number) =>
        `Версия: ${version} (${versionCode})`,
    defaultVersion: "Версия: 0.0.1",
    android: (version: string, api: number) =>
        `Android ${version} (API ${api})`,
    defaultAndroid: "Android",
    developer: "Разработчик: Максим Дрючин, 2026",

    studyLessonMenu:
        "Долгое нажатие на карточку урока открывает меню",
    studyMarkRating:
        "Нажатие на любую оценку открывает рейтинг",
    studySubjectRating:
        "Нажатие на название предмета открывает рейтинг",

    adLabel: "Реклама",
    errorAd: "Произошла ошибка при загрузке рекламы",
    errorClickAd:
        "Произошла ошибка при отправке статистики",
} as const;