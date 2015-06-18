import sublime


def get_full_content(view):
    return view.substr(sublime.Region(0, view.size()))
