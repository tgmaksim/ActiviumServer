import type {
    MarkLast,
    MarksSubjectPeriod,
    MarksSubjectFinal,
} from "@/api/dnevnik";


export interface UiMarksResult {
    recentMarks: MarkLast[];
    periodMarks: MarksSubjectPeriod[];
    ratingKey: string | null;
    finalMarks: MarksSubjectFinal[];
}
