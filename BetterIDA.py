from ida_idaapi import PLUGIN_KEEP, plugin_t
from ida_kernwin import (
    AST_DISABLE_FOR_WIDGET,
    AST_ENABLE_FOR_WIDGET,
    BWN_PSEUDOCODE,
    LROEF_CPS_RANGE,
    SETMENU_APP,
    UI_Hooks,
    action_desc_t,
    action_handler_t,
    attach_action_to_menu,
    line_rendering_output_entry_t,
    refresh_custom_viewer,
    register_action,
)
from ida_lines import tag_remove

INDENT_RAINBOW_COLORS = [0x40FF9E40, 0x403AC267, 0x403CA2E6, 0x406C6CF5]


class IndentRainbowUIHooks(UI_Hooks):
    def __init__(self):
        UI_Hooks.__init__(self)
        self.enabled = True

    def get_lines_rendering_info(self, out, widget, info):
        if not self.enabled:
            return

        for i in info.sections_lines:
            for j in i:
                t = tag_remove(j.line)
                l = len(t) - len(t.lstrip())
                n = 0

                while n * 2 < l:
                    c = INDENT_RAINBOW_COLORS[n % len(INDENT_RAINBOW_COLORS)]
                    e = line_rendering_output_entry_t(j, n * 2, 2, LROEF_CPS_RANGE, c)
                    out.entries.push_back(e)
                    n += 1


class IndentRainbowActionHandler(action_handler_t):
    def __init__(self, ui_hooks):
        action_handler_t.__init__(self)
        self.ui_hooks = ui_hooks

    def activate(self, ctx):
        self.ui_hooks.enabled = not self.ui_hooks.enabled
        refresh_custom_viewer(ctx.widget)

    def update(self, ctx):
        return (
            AST_ENABLE_FOR_WIDGET
            if ctx.widget_type == BWN_PSEUDOCODE
            else AST_DISABLE_FOR_WIDGET
        )


class BetterIDA(plugin_t):
    wanted_name = "BetterIDA"
    flags = PLUGIN_KEEP

    def init(self):
        indent_rainbow_ui_hooks = IndentRainbowUIHooks()
        indent_rainbow_ui_hooks.hook()
        register_action(
            action_desc_t(
                "IndentRainbow",
                "Enable/Disable Indent Rainbow",
                IndentRainbowActionHandler(indent_rainbow_ui_hooks),
                "Shift+Alt+R",
            )
        )
        attach_action_to_menu(
            "Edit/BetterIDA/IndentRainbow",
            "IndentRainbow",
            SETMENU_APP,
        )
        print("[+] BetterIDA Plugin Loaded Successfully!")
        print("[+] Version: 1.0")
        print("[+] Author: @Titvt")
        return PLUGIN_KEEP

    def term(self):
        pass

    def run(self, arg):
        pass


def PLUGIN_ENTRY():
    return BetterIDA()
