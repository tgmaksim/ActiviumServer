import type {
    MarksOther,
    MarksSubjectRatingResult,
} from "@/api/dnevnik";

/**
 * Представление ученика в рейтинговом списке.
 *
 * isOldMark и isRatingUp добавляются для отображения
 * предыдущего места, а не приходят внутри MarksOther.
 */
export type RatingPerson = MarksOther & {
    isOldMark?: boolean;
    isRatingUp?: boolean | null;
};

/**
 * Формирует список предметного рейтинга.
 *
 * Предыдущее место вставляется в ту же позицию,
 * что и в Android: после последнего места,
 * которое не выше предыдущего.
 */
export function getSubjectRatingPeople(
    data: MarksSubjectRatingResult,
): RatingPerson[] {
    const people: RatingPerson[] = [...data.rating];

    const oldMark = data.oldMark;

    if (!oldMark || oldMark.number === null) {
        return people;
    }

    let insertIndex = -1;

    for (let index = 0; index < people.length; index++) {
        const number = people[index].number;

        if (
            number !== null &&
            oldMark.number >= number
        ) {
            insertIndex = index;
        }
    }

    if (insertIndex !== -1) {
        people.splice(insertIndex + 1, 0, {
            ...oldMark,
            isOldMark: true,
            isRatingUp: data.isRatingUp,
        });
    }

    return people;
}