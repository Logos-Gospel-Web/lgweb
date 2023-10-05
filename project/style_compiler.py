import os
from django.conf import settings
from pipeline.compilers import SubProcessCompiler


class StyleCompiler(SubProcessCompiler):
    output_extension = 'css'

    def match_file(self, filename):
        return filename.endswith(('.scss', '.sass'))

    def compile_file(self, infile, outfile, outdated=False, force=False):
        command = (
            'npx',
            'sass',
            '-s',
            'expanded' if settings.DEBUG else 'compressed',
            infile,
            outfile
        )
        return self.execute_command(command, cwd=os.path.dirname(infile))
