from . import todoflow
import sublime
import sublime_plugin


class ToggleDoneCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.run_on_line(edit, self.view.full_line(region))

    def run_on_line(self, edit, line_reqion):
        line = self.view.substr(line_reqion).rstrip()
        replacement = self.transform_line(line) + '\n'
        self.view.replace(edit, line_reqion, replacement)

    def transform_line(self, line):
        if todoflow.has_tag(line, 'done'):
            return todoflow.remove_tag(line, 'done')
        else:
            import datetime
            return todoflow.add_tag(
                line, 'done', datetime.date.today().isoformat()
            )