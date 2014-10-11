Skripte automatisch ausführbar machen
=====================================

:date: 2010-03-13 17:12:25
:tags: de, emacs

Einfach

.. code-block:: lisp

   (add-hook 'after-save-hook 'executable-make-buffer-file-executable-if-script-p)

zur Konfiguration hinzufügen, dann werden Dateien mit Shebang
automatisch beim Speichern ausführbar gemacht.
