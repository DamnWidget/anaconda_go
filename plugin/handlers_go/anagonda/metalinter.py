
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details


class MetaLinter(object):
    """Just a convenience wrapper to handle GoMetaLinter options
    """

    _slow_linters = [
        'structcheck', 'varcheck', 'errcheck', 'aligncheck',
        'testify', 'test', 'interfacer', 'unconvert', 'deadcode'
    ]

    @staticmethod
    def lint_fast_only(options):
        """
        Process options to create a gometalinter
        options string to run fast linters only
        """

        linter_flags = MetaLinter._build_linter_flags(options)
        opts = ['--disable-all']
        for linter in options['linters']:
            linter_name, enabled = linter.popitem()
            linter_name = linter_name.replace('anaconda_go_', '')
            if linter_name not in MetaLinter._slow_linters and enabled:
                opts.append('--enable={0}'.format(linter_name))
                if linter_name in linter_flags:
                    linter_flags[linter_name]['enabled'] = True

        return MetaLinter._lint_defaults(opts, linter_flags, options)

    @staticmethod
    def lint_slow_only(options):
        """
        Process options to create a gometalinter
        options string to run slow linters only
        """

        linter_flags = MetaLinter._build_linter_flags(options)
        opts = ['--disable-all']
        for linter in options['linters']:
            linter_name, enabled = linter.popitem()
            linter_name = linter_name.replace('anaconda_go_', '')
            if linter_name in MetaLinter._slow_linters and enabled:
                opts.append('--enable={0}'.format(linter_name))
                if linter_name in linter_flags:
                    linter_flags[linter_name]['enabled'] = True

        return MetaLinter._lint_defaults(opts, linter_flags, options)

    @staticmethod
    def lint_all(options):
        """
        Process options to create a gometalinter
        options string to run all linters
        """

        linter_flags = MetaLinter._build_linter_flags(options)
        opts = ['--disable-all']
        for linter in options['linters']:
            linter_name, enabled = linter.popitem()
            linter_name = linter_name.replace('anaconda_go_', '')
            if enabled:
                opts.append('--enable={0}'.format(linter_name))
                if linter_name in linter_flags:
                    linter_flags[linter_name]['enabled'] = True

        return MetaLinter._lint_defaults(opts, linter_flags, options)

    @staticmethod
    def _lint_defaults(opts, linter_flags, options):
        """Apply default options
        """

        for linter in linter_flags:
            if linter_flags[linter]['enabled']:
                opts.append(linter_flags[linter]['opt'])

        if options.get('lint_test', False):
            opts.append('--tests')

        opts.append('--json')

        exclude = options.get('exclude_regexps', [])
        if len(exclude) > 0:
            opts.append('--exclude="{0}"'.format('|'.join(exclude)))

        opts.append(options.get('path', ''))

        return ' '.join(opts)

    @staticmethod
    def _build_linter_flags(options):
        """Build linter flags based in the given options
        """

        return {
            'lll': {
                'enabled': False,
                'opt': '--line-length={0}'.format(
                    options.get('max_line_length', 120)
                )
            },
            'gocyclo': {
                'enabled': False,
                'opt': '--cyclo-over={0}'.format(
                    options.get('gocyclo_threshold', 10)
                )
            },
            'golint': {
                'enabled': False,
                'opt': '--min-confidence={0}'.format(
                    options.get('golint_min_confidence', 0.80)
                )
            },
            'goconst': {
                'enabled': False,
                'opt': '--min-occurrences={0} --min-const-length={1}'.format(
                    options.get('goconst_min_occurrences', 3),
                    options.get('min_const_length', 3)
                )
            },
            'dupl': {
                'enabled': False,
                'opt': '--dupl-threshold={0}'.format(
                    options.get('dupl_threshold', 50)
                )
            }
        }
