# Sublime Todoflow

![icon](icon.png)

Sublime Text 3 package for taskpaper files based on [TodoFlow](https://github.com/bevesce/TodoFlow).

## Features

### Syntex definition

You can change it to highlight your own tags

![syntax highlighted in mini.dark](screenshots/syntax.png)

### Filter

command: `filter`   

![filter](screenshots/filter.gif)


### Saved filters

**<kbd>⌘+shift+f</kbd>**, command: `saved_filters`

![saved filter](screenshots/saved_filter.gif)

### Toggle done

**<kbd>⌘+.</kbd>**, command: `toggle_done`

![toggle done](screenshots/toggle_done.gif)

### Move to project

command: `move_to_project`

![move to project](screenshots/move_to_project.gif)

## Installation

Clone package with submodules into Packages folder and adjusts tags in *SublimeTodoflow.sublime-syntax*.

```
git clone --recursive https://github.com/bevesce/todoflow_sublime.git path/to/Sublime Text 3/Packages/SublimeTodoflow
```

## Requirements/Includes

SublimeTodoflow requires my python package [TodoFlow](https://github.com/bevesce/TodoFlow), it's included in this repo as submodule.
