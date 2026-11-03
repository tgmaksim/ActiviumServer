import { DnevnikTools } from "./dtools";

export const Praise = {
    sendForLesson(
        lessonKey: string,
        text: string | null,
    ) {
        return DnevnikTools.sendPraise(
            lessonKey,
            null,
            text,
        );
    },

    sendForMark(
        ratingKey: string,
        text: string | null,
    ) {
        return DnevnikTools.sendPraise(
            null,
            ratingKey,
            text,
        );
    },
};