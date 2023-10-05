from django.conf import settings
import os
from pipeline.compilers import SubProcessCompiler


class ScriptCompiler(SubProcessCompiler):
    output_extension = 'js'

    def match_file(self, path):
        return path.endswith('.ts')

    def compile_file(self, infile, outfile, outdated=False, force=False):
        command = (
            'npx',
            'webpack',
            'build',
            '--entry',
            infile,
            '--output-path',
            os.path.dirname(outfile),
            '--output-filename',
            os.path.basename(outfile),
        )
        return self.execute_command(command, settings.BASE_DIR)
