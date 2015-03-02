from textwrap import dedent

from IPython.config.loader import Config
from IPython.utils.traitlets import Unicode, Bool, Dict
from IPython.nbconvert.preprocessors import ClearOutputPreprocessor

from nbgrader.apps.baseapp import (
    BaseNbConvertApp, nbconvert_aliases, nbconvert_flags)
from nbgrader.preprocessors import (
    FindStudentID, SaveAutoGrades, OverwriteGradeCells, Execute)

aliases = {}
aliases.update(nbconvert_aliases)
aliases.update({
    'assignment': 'AssignmentExporter.assignment_id',
    'student': 'AssignmentExporter.student_id',
    'db': 'AssignmentExporter.db_url'
})

flags = {}
flags.update(nbconvert_flags)
flags.update({
    'overwrite-cells': (
        {'AutogradeApp': {'overwrite_cells': True}},
        "Overwrite grade cells from the database."
    )
})

class AutogradeApp(BaseNbConvertApp):

    name = Unicode(u'nbgrader-autograde')
    description = Unicode(u'Autograde a notebook by running it')
    aliases = Dict(aliases)
    flags = Dict(flags)

    examples = Unicode(dedent(
        """
        Running `nbgrader autograde` on a file by itself will produce a student
        version of that file in the same directory. In this case, it will produce
        "Problem 1.nbconvert.ipynb" (note that you need to specify the assignment
        name and the student id):
        
        > nbgrader autograde "Problem 1.ipynb" --assignment="Problem Set 1" --student=student1

        If you want to override the .nbconvert part of the filename, you can use
        the --output flag:

        > nbgrader autograde "Problem 1.ipynb" --output "Problem 1.graded.ipynb" --assignment="Problem Set 1" --student=student1

        Or, you can put the graded version in a different directory. In the
        following example, there will be a file "graded/Problem 1.ipynb" after
        running `nbgrader autograde`:

        > nbgrader autograde "Problem 1.ipynb" --build-dir=graded --assignment="Problem Set 1" --student=student1

        You can also use shell globs, and copy files from one directory to another:

        > nbgrader autograde submitted/*.ipynb --build-dir=graded --assignment="Problem Set 1" --student=student1

        If you want to overwrite grade cells with the source and metadata that
        was stored in the database when running `nbgrader assign` with --save-cells,
        you can use the --overwrite-cells flag:

        > nbgrader autograde "Problem 1.ipynb" --assignment="Problem Set 1" --student=student1 --overwrite-cells

        """
    ))

    student_id = Unicode(u'', config=True)
    overwrite_cells = Bool(False, config=True, help="Overwrite grade cells from the database")

    def _classes_default(self):
        """This has to be in a method, for TerminalIPythonApp to be available."""
        classes = super(AutogradeApp, self)._classes_default()
        classes.extend([
            FindStudentID,
            ClearOutputPreprocessor,
            OverwriteGradeCells,
            Execute,
            SaveAutoGrades
        ])
        return classes

    def build_extra_config(self):
        self.extra_config = Config()
        self.extra_config.Exporter.preprocessors = [
            'nbgrader.preprocessors.FindStudentID',
            'IPython.nbconvert.preprocessors.ClearOutputPreprocessor'
        ]
        if self.overwrite_cells:
            self.extra_config.Exporter.preprocessors.append(
                'nbgrader.preprocessors.OverwriteGradeCells'
            )
        self.extra_config.Exporter.preprocessors.extend([
            'nbgrader.preprocessors.Execute',
            'nbgrader.preprocessors.SaveAutoGrades'
        ])
        self.config.merge(self.extra_config)
