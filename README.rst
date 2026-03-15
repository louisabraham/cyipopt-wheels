========================
README for cyipopt-wheels
========================

This is a fork of `cyipopt <https://github.com/mechmotum/cyipopt>`_ that
provides **pre-built binary wheels** on PyPI for Linux (x86_64, aarch64),
macOS (arm64), and Windows (AMD64), as well as Pyodide (wasm32) wheels
attached to GitHub releases.

The upstream ``cyipopt`` package only distributes a source distribution on PyPI,
which requires users to compile Ipopt and its dependencies themselves. This fork
automates that process using `cibuildwheel <https://cibuildwheel.pypa.io>`_ so
that ``pip install cyipopt-wheels`` works out of the box without any system-level
dependencies.

Installation
============

::

   pip install cyipopt-wheels

This installs the same ``cyipopt`` Python package — usage is identical to
upstream::

   from cyipopt import minimize_ipopt

For full documentation, see `cyipopt.readthedocs.io <https://cyipopt.readthedocs.io>`_.

Using in Pyodide (browser/WASM)
================================

cyipopt can run in the browser via `Pyodide <https://pyodide.org>`_, with Ipopt
compiled to WebAssembly. Since PyPI does not accept Pyodide wheels, they are
attached to `GitHub releases <https://github.com/louisabraham/cyipopt-wheels/releases>`_.

Install with micropip in a Pyodide environment:

.. code-block:: python

   import micropip
   await micropip.install(
       "https://github.com/louisabraham/cyipopt-wheels/releases/download/v1.7.0.dev0/cyipopt_wheels-1.7.0.dev0-cp312-cp312-pyodide_2024_0_wasm32.whl"
   )

Then use it normally:

.. code-block:: python

   import numpy as np
   from cyipopt import minimize_ipopt
   from scipy.optimize import rosen, rosen_der

   x0 = np.array([1.3, 0.7, 0.8, 1.9, 1.2])
   res = minimize_ipopt(rosen, x0, jac=rosen_der)
   print(res.x)

**Full example**: see the `grecov calculator <https://louisabraham.github.io/grecov/>`_
for a working web app that uses cyipopt in Pyodide to solve nonlinear optimization
problems entirely in the browser.

License
=======

cyipopt is open-source code released under the EPL_ license, see the
``LICENSE`` file.

.. _EPL: https://www.eclipse.org/legal/epl-2.0/
