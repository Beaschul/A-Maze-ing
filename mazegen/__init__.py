"""mazegen: reusable maze generation package.

This package is distributed on its own (``mazegen-*.whl``) to be reused by
later projects, so it must stay independent from the application: it never
imports ``app``, never prints, never reads user input and never exits.
Errors are reported with exceptions.
"""
