from . import todoflow
from . import datedrop
import sublime
import sublime_plugin
import re

from .base import get_full_content


class FilterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.query_from_input()

    def query_from_input(self):
        self.view.window().show_input_panel(
            'query', '',
            on_done=self.filter,
            on_change=self.filter,
            on_cancel=self.unfold_all
        )

    def filter(self, query):
        self.unfold_all()
        ranges_not_to_fold = self._get_ranges_not_to_fold(query)
        ranges_to_fold = self._calculate_ranges_to_fold(
            self.view.size(), ranges_not_to_fold
        )
        self._do_folding(ranges_to_fold)

    def expand_query(self, query):
        return re.sub(
            '{([^}])*}',
            lambda m: datedrop.expand(m.group(1)),
            query
        )

    def _get_ranges_not_to_fold(self, query):
        text = self.get_full_content()
        todolist = todoflow.from_text(text)
        ranges_not_to_fold = []
        for i in todolist.filter(query):
            ranges_not_to_fold.append((i.start, i.end))
        return ranges_not_to_fold

    def get_full_content(self):
        return get_full_content(self.view)

    def _calculate_ranges_to_fold(self, document_length, ranges_not_to_fold):
        range_start = 0
        ranges = []
        if not ranges_not_to_fold:
            return ((0, document_length), )
        if ranges_not_to_fold[0][0] == 0:
            range_start = ranges_not_to_fold[0][1]
            ranges_not_to_fold = ranges_not_to_fold[1:]
        for s, e in ranges_not_to_fold:
            if range_start + 1 == s:
                range_start = e
                continue
            if range_start != 0:
                range_start += 1
            ranges.append((range_start, s - 1))
            range_start = e
        if e != document_length:
            ranges.append((e + 1, document_length))
        return ranges

    def _do_folding(self, ranges_to_fold):
        for s, e in ranges_to_fold:
            self.view.fold(sublime.Region(s, e))

    def unfold_all(self):
        self.view.unfold(sublime.Region(0, self.view.size()))


class SavedFiltersCommand(FilterCommand):
    OTHER_QUERY = '> Other'
    SHOW_ALL_QUERY = '| ALL'

    def run(self, edit):
        self.view.window().show_quick_panel(
            self._get_queries(), self.select_query
        )

    def _get_queries(self):
        settings = sublime.load_settings('SublimeTodoflow.sublime-settings')
        queries = settings.get('queries')
        self.queries_input = [
            [k, v] for k, v in queries.items()
        ] + [self.OTHER_QUERY, self.SHOW_ALL_QUERY]
        return self.queries_input

    def select_query(self, index):
        if index == -1:
            return
        query = self._retrieve_query_from_index(index)
        if query is not None:
            self.filter(query)

    def _retrieve_query_from_index(self, index):
        query_item = self.queries_input[index]
        if query_item == self.SHOW_ALL_QUERY:
            return ''
        elif query_item == self.OTHER_QUERY:
            self.query_from_input()
            return None  # it works asynchronously
        else:
            return query_item[1]
