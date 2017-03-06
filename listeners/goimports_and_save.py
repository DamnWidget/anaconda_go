"""
Workaround for https://github.com/DamnWidget/anaconda_go/issues/9
"""
import re
import sublime, sublime_plugin

class GoImportsOnSave(sublime_plugin.EventListener):
    """
    Run goimports against Go language syntax documents, on save.
    For use in combination with the GoImports SublimeText plugin package.
    
    Enable 'goimports_on_save' in your project or application settings.
    """
    # Supported syntax
    _SYNTAX = frozenset(["go"])
    _RX_SOURCE = re.compile(r'source\.(\S+)')

    def on_pre_save(self, view):
        enabled = view.settings().get("goimports_on_save", False)
        if not enabled:
            return

        scope = view.scope_name(0)
        match = self._RX_SOURCE.match(scope)
        if not match:
            return

        syntax = match.group(1)
        if syntax.lower() not in self._SYNTAX:
            return

        try:
            view.run_command("go_imports")
        except Exception as e:
            pass
