Chromium als Standardbrowser in Emacs
=====================================

:date: 2010-02-26 11:45:40
:tags: de, emacs

.. code-block:: lisp

   (setq browse-url-browser-function 'browse-url-generic
      browse-url-generic-program "chromium")
