import re
import compileall
import os

work_dir = os.path.dirname(os.path.abspath(__file__))
#compileall.compile_dir(work_dir, force=True)

# Perform same compilation, excluding files in .svn directories.
#compileall.compile_dir(work_dir, rx=re.compile(r'[/\\][.](unused|test)'), force=True)
compileall.compile_dir(work_dir, rx=re.compile(
    r'[/\\](unused|test|[.]git)'), force=True, quiet=True)
