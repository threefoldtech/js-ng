import sys
import traceback
import better_exceptions

from functools import partial

from prompt_toolkit.keys import Keys
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.completion import Completion

from ptpython.prompt_style import PromptStyle


def patched_handle_exception(self, e):
    """
    a new handler for ptpython repl exceptions
    it will call excepthook after ommitting all this framework's calls from traceback

    for the original, see ptpython.repl.PythonInput._handle_exception
    """
    output = self.app.output

    t, v, tb = sys.exc_info()

    # Required for pdb.post_mortem() to work.
    sys.last_type, sys.last_value, sys.last_traceback = t, v, tb

    # loop until getting actual traceback
    last_stdin_tb = tb
    while tb:
        if tb.tb_frame.f_code.co_filename == "<stdin>":
            last_stdin_tb = tb
        tb = tb.tb_next

    # except hook does not work as expected
    # sys.excepthook(t, v, last_stdin_tb)
    # just print formatted exception for now
    formatted = better_exceptions.format_exception(t, v, last_stdin_tb)
    print_formatted_text(ANSI(formatted))

    output.write("%s\n" % e)
    output.flush()


def eval_code(stmts, locals_=None, globals_=None):
    """
    a helper function to ignore incomplete syntax erros when evaluating code
    while typing incomplete lines, e.g.: j.clien...
    """
    if not stmts:
        return

    try:
        code = compile(stmts, filename="<kosmos>", mode="eval")
    except SyntaxError:
        return

    return eval(code, globals_, locals_)
def get_current_line(document):
    tbc = document.current_line_before_cursor
    if tbc:
        line = tbc.split(".")
        parent, member = ".".join(line[:-1]), line[-1]
        if member.startswith("__"):  # then we want to show private methods
            prefix = "__"
        elif member.startswith("_"):  # then we want to show private methods
            prefix = "_"
        else:
            prefix = ""
        return parent, member, prefix
    raise ValueError("nothing is written")

def get_completions(self, document, complete_event):
    """
    get completions for j objects (using _method_) and others (using dir)
    :rtype: `Completion` generator
    """

    def colored_completions(names, color):
        for name in names:
            if not name:
                continue
            if name.startswith(member):
                completion = name[len(member) :]
                yield Completion(
                    completion, 0, display=name, style="bg:%s fg:ansiblack" % color, selected_style="bg:ansidarkgray"
                )

    try:
        parent, member, prefix = get_current_line(document)
    except ValueError:
        return

    obj = eval_code(parent, self.get_locals(), self.get_globals())
    if obj:
        members = sorted(dir(obj), key=sort_children_key)
        yield from colored_completions(members, "ansigray")


def sort_children_key(name):
    """Sort members of an object
    :param name: name
    :type name: str
    :return: the order of sorting
    :rtype: int
    """
    if name.startswith("__"):
        return 3
    elif name.startswith("_"):
        return 2
    elif name.isupper():
        return 1
    else:
        return 0

def ptconfig(repl):
    repl.exit_message = "Bye!"
    repl.show_docstring = True

    # When CompletionVisualisation.POP_UP has been chosen, use this
    # scroll_offset in the completion menu.
    repl.completion_menu_scroll_offset = 0

    # Show line numbers (when the input contains multiple lines.)
    repl.show_line_numbers = True

    # Show status bar.
    repl.show_status_bar = True

    # When the sidebar is visible, also show the help text.
    # repl.show_sidebar_help = True

    # Highlight matching parethesis.
    repl.highlight_matching_parenthesis = True

    # Line wrapping. (Instead of horizontal scrolling.)
    repl.wrap_lines = True

    # Mouse support.
    repl.enable_mouse_support = True

    # Complete while typing. (Don't require tab before the
    # completion menu is shown.)
    # repl.complete_while_typing = True

    # Vi mode.
    repl.vi_mode = False

    # Paste mode. (When True, don't insert whitespace after new line.)
    repl.paste_mode = False

    # Use the classic prompt. (Display '>>>' instead of 'In [1]'.)
    repl.prompt_style = "classic"  # 'classic' or 'ipython'

    # Don't insert a blank line after the output.
    repl.insert_blank_line_after_output = False

    # History Search.
    # When True, going back in history will filter the history on the records
    # starting with the current input. (Like readline.)
    # Note: When enable, please disable the `complete_while_typing` option.
    #       otherwise, when there is a completion available, the arrows will
    #       browse through the available completions instead of the history.
    # repl.enable_history_search = False

    # Enable auto suggestions. (Pressing right arrow will complete the input,
    # based on the history.)
    repl.enable_auto_suggest = True

    # Enable open-in-editor. Pressing C-X C-E in emacs mode or 'v' in
    # Vi navigation mode will open the input in the current editor.
    # repl.enable_open_in_editor = True

    # Enable system prompt. Pressing meta-! will display the system prompt.
    # Also enables Control-Z suspend.
    repl.enable_system_bindings = False

    # Ask for confirmation on exit.
    repl.confirm_exit = False

    # Enable input validation. (Don't try to execute when the input contains
    # syntax errors.)
    # repl.enable_input_validation = True

    # Use this colorscheme for the code.
    repl.use_code_colorscheme("perldoc")

    # Set color depth (keep in mind that not all terminals support true color).
    repl.color_depth = "DEPTH_24_BIT"  # True color.

    repl.enable_syntax_highlighting = True

    repl.min_brightness = 0.3

    # Add custom key binding for PDB.

    @repl.add_key_binding(Keys.ControlB)
    def _debug_event(event):
        ' Pressing Control-B will insert "pdb.set_trace()" '
        event.cli.current_buffer.insert_text("\nimport pdb; pdb.set_trace()\n")

    # Custom key binding for some simple autocorrection while typing.

    corrections = {"impotr": "import", "pritn": "print", "pr": "print("}

    @repl.add_key_binding(" ")
    def _(event):
        " When a space is pressed. Check & correct word before cursor. "
        b = event.cli.current_buffer
        w = b.document.get_word_before_cursor()
        if w is not None:
            if w in corrections:
                b.delete_before_cursor(count=len(w))
                b.insert_text(corrections[w])
        b.insert_text(" ")

    class CustomPrompt(PromptStyle):
        """
        The classic Python prompt.
        """

        def in_prompt(self):
            return [("class:prompt", "JS-NG> ")]

        def in2_prompt(self, width):
            return [("class:prompt.dots", "...")]

        def out_prompt(self):
            return []

    repl.all_prompt_styles["custom"] = CustomPrompt()
    repl.prompt_style = "custom"

    repl._handle_exception = partial(patched_handle_exception, repl)
    better_exceptions.hook()


    old_get_completions = repl._completer.__class__.get_completions


    def custom_get_completions(self, document, complete_event):
        try:
            _, _, prefix = get_current_line(document)
        except ValueError:
            return

        completions = []
        try:
            completions = list(get_completions(self, document, complete_event))
        except Exception:
            RuntimeError("Error while getting completions\n" + traceback.format_exc())

        if not completions:
            completions = old_get_completions(self, document, complete_event)
        def filter_completions_on_prefix(completions, prefix=None):
            HIDDEN_PREFIXES = ("_", "__")

            for completion in completions:
                text = completion.text
                if prefix not in HIDDEN_PREFIXES and text.startswith(HIDDEN_PREFIXES):
                    continue
                yield completion
        yield from filter_completions_on_prefix(completions, prefix)

    repl._completer.__class__.get_completions = custom_get_completions
