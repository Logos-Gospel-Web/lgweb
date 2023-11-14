from django.conf import settings
from pipeline.compilers import SubProcessCompiler

DEBUG_RELOAD = False

class ScriptCompiler(SubProcessCompiler):
    output_extension = 'js'

    def match_file(self, path):
        return path.endswith('.ts')

    def compile_file(self, infile, outfile, outdated=False, force=False):
        if not DEBUG_RELOAD and not outdated and not force:
            return

        command = (
            'npx',
            'rollup',
            '--config',
            'rollup.config.mjs',
            '--input',
            infile,
            '--file',
            outfile,
        )
        return self.execute_command(command, settings.BASE_DIR)
