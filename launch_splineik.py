# -*- coding: utf-8 -*-
"""Portable Maya launcher: drag this file into the viewport or execute it as a file."""
import os
import sys

_REPO_DIR = os.path.dirname(os.path.abspath(__file__))


def show():
    """Open SplineIK_Tool from the repository containing this launcher."""
    if not os.path.isfile(os.path.join(_REPO_DIR, 'SplineIK_Tool', '__init__.py')):
        raise RuntimeError('Keep launch_splineik.py next to the SplineIK_Tool folder.')
    if _REPO_DIR in sys.path:
        sys.path.remove(_REPO_DIR)
    sys.path.insert(0, _REPO_DIR)
    existing = sys.modules.get('SplineIK_Tool')
    if existing is not None:
        loaded = os.path.normcase(os.path.abspath(getattr(existing, '__file__', '')))
        expected = os.path.normcase(os.path.join(_REPO_DIR, 'SplineIK_Tool', '__init__.py'))
        if loaded not in (expected, expected + 'c', expected + 'o'):
            for name in list(sys.modules):
                if name == 'SplineIK_Tool' or name.startswith('SplineIK_Tool.'):
                    sys.modules.pop(name, None)
    import SplineIK_Tool
    return SplineIK_Tool.show()


def onMayaDroppedPythonFile(*args):
    """Maya Python-file drag-and-drop entry point."""
    return show()


if __name__ == '__main__':
    show()
