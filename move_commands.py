from .todoflow import todoflow
from .todoflow import textutils
import sublime
import sublime_plugin

from .base import get_full_content


class MoveToProjectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.edit = edit
        projects = self.get_projects()
        self.projects, self.projects_ranges = self.get_titles_and_ranges(projects)
        self.view.window().show_quick_panel(
            self.projects, self.move_to_project_with_index
        )

    def get_projects(self):
        text = get_full_content(self.view)
        todolist = todoflow.from_text(text)
        return todolist.search('type = "project"')

    def get_titles_and_ranges(self, projects):
        titles, ranges = [], []
        for project in projects:
            titles.append(str(project)[:-1])
            ranges.append((project.start, project.end))
        return titles, ranges

    def move_to_project_with_index(self, index):
        selected_lines = []
        for region in self.view.sel():
            region = self.view.full_line(region)
            selected_lines.append((region.a, region.b))
        self.view.window().run_command('insert_tasks_into_project', {
            'project_range': self.projects_ranges[index],
            'selected_lines': selected_lines
        })


class InsertTasksIntoProjectCommand(sublime_plugin.TextCommand):
    def run(self, edit, project_range, selected_lines):
        lines_texts = self.get_lines_text(selected_lines)
        project_s, project_e = project_range
        project_line = self.view.substr(
            sublime.Region(*project_range)
        )
        text_to_insert = self.prepare_text_to_insert(
            project_line, lines_texts
        )
        insert = self.prepare_insert(project_e, text_to_insert)
        removes = self.prepare_removes(selected_lines)
        self.do_changes(edit, [insert] + list(removes))

    def get_lines_text(self, selected_lines):
        for s, e in selected_lines:
            yield self.view.substr(sublime.Region(s, e)).strip()

    def prepare_removes(self, selected_lines):
        for s, e in selected_lines:
            yield sublime.Region(s, e), ''

    def prepare_text_to_insert(self, project, lines):
        level = textutils.calculate_indent_level(project) + 1
        return '\n' + '\n'.join(
            ('\t' * level + l for l in lines)
        )

    def prepare_insert(self, project_end, text_to_insert):
        return sublime.Region(project_end, project_end), text_to_insert

    def do_changes(self, edit, changes):
        changes.sort(key=lambda k: k[0], reverse=True)
        for region, replacement in changes:
            self.view.replace(edit, region, replacement)
