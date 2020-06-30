from pyarabic.araby import strip_tashkeel, is_tashkeel

from .models import MarkPosition


class ArabicUtilities(object):
    start_mark = 'mark_start'
    note_start_mark = 'note_mark_start'
    start_mark_len = len(start_mark)
    end_mark = 'mark_end'
    end_mark_len = len(end_mark)
    highlight_tag_start = '<span class=\'highlighted\' style=\'background-color:#E0E0E0\'>'
    note_tag_start = '<span class=\'highlighted note\' style=\'background-color:#E0E0E0\'>'
    tag_end = '</span>'

    @staticmethod
    def get_tashkeel_position(page, start, end):
        if not page or start is None or start < 0 or not end:
            return None
        tashkeel_start = None
        tashkeel_end = None
        counter = -1
        index = 0
        for char in page:
            if not is_tashkeel(char):
                counter += 1
                if counter == start:
                    tashkeel_start = index
            if counter == end:
                tashkeel_end = index
                break
            index += 1
        return MarkPosition(tashkeel_start, tashkeel_end)

    @staticmethod
    def get_no_tashkeel_position(page, start, end):
        if not page or start is None or start < 0 or not end:
            return None
        marked = page[:end] + ArabicUtilities.end_mark + page[end:]
        no_tashkeel = strip_tashkeel(marked[:start] + ArabicUtilities.start_mark + marked[start:])
        return MarkPosition(no_tashkeel.index(ArabicUtilities.start_mark),
                            no_tashkeel.index(ArabicUtilities.end_mark) - len(ArabicUtilities.start_mark))

    @staticmethod
    def get_highlighted_text(comments, page, page_no, with_tashkeel=False):
        if not comments or not page:
            return page
        added = []
        if not with_tashkeel:
            page = strip_tashkeel(page)
        for comment in comments:
            if comment.page != page_no or not comment.end or comment.start is None or comment.start < 0:
                continue
            start = comment.start
            end = comment.end
            mark_start = ArabicUtilities.start_mark
            if with_tashkeel:
                start = comment.tashkeel_start
                end = comment.tashkeel_end
            if comment.note:
                mark_start = ArabicUtilities.note_start_mark
            start = start - 1 + sum([len(mark) for mark in added])
            page = page[:start] + mark_start + page[start:]
            added.append(mark_start)
            end = end - 1 + sum([len(mark) for mark in added])
            page = page[:end] + ArabicUtilities.end_mark + page[end:]
            added.append(ArabicUtilities.end_mark)

        return page.replace(ArabicUtilities.end_mark, ArabicUtilities.tag_end) \
            .replace(ArabicUtilities.note_start_mark, ArabicUtilities.note_tag_start) \
            .replace(ArabicUtilities.start_mark, ArabicUtilities.highlight_tag_start)
