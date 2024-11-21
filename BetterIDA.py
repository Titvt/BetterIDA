from ida_hexrays import decompile
from ida_idaapi import PLUGIN_KEEP, plugin_t
from ida_kernwin import (
    AST_ENABLE_ALWAYS,
    BWN_PSEUDOCODE,
    LROEF_CPS_RANGE,
    SETMENU_APP,
    UI_Hooks,
    action_desc_t,
    action_handler_t,
    attach_action_to_menu,
    get_widget_type,
    line_rendering_output_entry_t,
    refresh_custom_viewer,
    register_action,
)
from ida_lines import tag_remove
from ida_segment import get_segm_class, getseg
from idautils import Functions, Segments

INDENT_RAINBOW_COLORS = [0x40FF9E40, 0x403AC267, 0x403CA2E6, 0x406C6CF5]


class IndentRainbowUIHooks(UI_Hooks):
    def __init__(self):
        UI_Hooks.__init__(self)
        self.enabled = True

    def get_lines_rendering_info(self, out, widget, info):
        if not self.enabled or get_widget_type(widget) != BWN_PSEUDOCODE:
            return

        for i in info.sections_lines:
            for j in i:
                line = tag_remove(j.line)
                length = len(line) - len(line.lstrip())
                indent = 0

                while indent * 2 < length:
                    color = INDENT_RAINBOW_COLORS[indent % len(INDENT_RAINBOW_COLORS)]
                    entry = line_rendering_output_entry_t(
                        j,
                        indent * 2,
                        min(length - indent * 2, 2),
                        LROEF_CPS_RANGE,
                        color,
                    )
                    out.entries.push_back(entry)
                    indent += 1


class IndentRainbowActionHandler(action_handler_t):
    def __init__(self):
        action_handler_t.__init__(self)
        self.ui_hooks = IndentRainbowUIHooks()
        self.ui_hooks.hook()

    def activate(self, ctx):
        self.ui_hooks.enabled = not self.ui_hooks.enabled

        if ctx.widget_type == BWN_PSEUDOCODE:
            refresh_custom_viewer(ctx.widget)

        return 0

    def update(self, ctx):
        return AST_ENABLE_ALWAYS


PSEUDO_SEARCH_DECOMPILATIONS = []


def redecompile():
    PSEUDO_SEARCH_DECOMPILATIONS.clear()
    functions = []

    for i in Segments():
        segment = getseg(i)

        if get_segm_class(segment) == "CODE":
            for j in Functions(segment.start_ea, segment.end_ea):
                functions.append(j)

    while True:
        done = True

        for i in functions[:]:
            decompilation = decompile(i)

            if decompilation is None:
                continue

            PSEUDO_SEARCH_DECOMPILATIONS.append((i, str(decompilation)))
            functions.remove(i)
            done = False

        if done:
            break


class PseudoSearchActionHandler(action_handler_t):
    def __init__(self):
        action_handler_t.__init__(self)

    def activate(self, ctx):
        redecompile()
        print(PSEUDO_SEARCH_DECOMPILATIONS)
        return 0

    def update(self, ctx):
        return AST_ENABLE_ALWAYS


def register_menu(name, label, handler, shortcut):
    register_action(action_desc_t(name, label, handler, shortcut))
    attach_action_to_menu(
        f"Edit/BetterIDA/{name}",
        name,
        SETMENU_APP,
    )


class BetterIDA(plugin_t):
    wanted_name = "BetterIDA"
    flags = PLUGIN_KEEP

    def init(self):
        register_menu(
            "IndentRainbow",
            "Indent Rainbow",
            IndentRainbowActionHandler(),
            "Shift+R",
        )
        register_menu(
            "PseudoSearch",
            "Pseudo Search",
            PseudoSearchActionHandler(),
            "Shift+F",
        )
        print("[+] BetterIDA Plugin Loaded Successfully!")
        print("[+] Version: 1.3")
        print("[+] Author: @Titvt")
        return PLUGIN_KEEP

    def run(self, arg):
        pass

    def term(self):
        pass


def PLUGIN_ENTRY():
    return BetterIDA()
