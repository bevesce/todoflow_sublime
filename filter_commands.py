from .todoflow import todoflow
from .todoflow.todoflow import textutils
from . import datedrop
import sublime
import sublime_plugin
import re

from .base import get_full_content


class FilterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.prepare()
        self.query_from_input()

    def prepare(self):
        self.content = self.view.substr(sublime.Region(0, self.view.size()))
        self.content_size = len(self.content.splitlines())
        self.todos = todoflow.Todos(self.content)

    def query_from_input(self):
        self.view.window().show_input_panel(
            'query', '',
            on_done=self.filter,
            on_change=self.filter,
            on_cancel=self.unfold_all
        )

    def filter(self, query):
        lines_to_fold = self.find_lines_to_fold(query)
        self.fold_lines(lines_to_fold)

    def find_lines_to_fold(self, query):
        not_to = set(self.find_lines_not_to_fold(query))
        for i in range(0, self.content_size):
            if i not in not_to:
                print('find_lines_to_fold', i)
                yield i

    def find_lines_not_to_fold(self, query):
        for item in self.todos.filter(query):
            line = item.get_line_number()
            print('line', line, item.todoitem)
            if line is not None:
                yield line

    def fold_lines(self, indices):
        self.unfold_all()
        regions_to_fold = self.find_regions_to_fold(indices)
        for region in self.coalesce_neighboring_regions(regions_to_fold):
            self.view.fold(region)

    def find_regions_to_fold(self, indices):
        for index in indices:
            yield self.view.line(self.view.text_point(index, 0))

    def coalesce_neighboring_regions(self, regions):
        prev_region = None
        for region in regions:
            if prev_region:
                if prev_region.b == region.a - 1:
                    prev_region = sublime.Region(prev_region.a, region.b)
                else:
                    yield prev_region
                    prev_region = region
            else:
                prev_region = region
            # yield region
        if prev_region: yield prev_region

    def unfold_all(self):
        self.view.unfold(sublime.Region(0, self.view.size()))


class SavedFiltersCommand(FilterCommand):
    OTHER_QUERY = '> Other'
    SHOW_ALL_QUERY = '| ALL'

    def run(self, edit):
        self.prepare()
        self.searches = self.find_searches()
        self.view.window().show_quick_panel(
            self.searches, self.select_query
        )

    def find_searches(self):
        self.content = self.view.substr(sublime.Region(0, self.view.size()))
        searches = todoflow.Todos(self.content).search('@search')
        return list(s.get_text().strip() for s in searches)

    def select_query(self, index):
        if index == -1:
            return
        query = self.retrieve_search_from_index(index)
        if query is not None:
            self.filter(query)

    def retrieve_search_from_index(self, index):
        item = self.searches[index]
        return textutils.get_tag_param(item, 'search')
