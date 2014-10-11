===========================
Emacs: Open file in browser
===========================

:date: 2014-08-20 23:12:28
:tags: de, emacs

Inspiriert vom `Idea-GitLab-Integration-Plugin
<http://plugins.jetbrains.com/plugin/7319>`_, das ein *open file in
browser* anbietet, habe ich das ganze mal für Emacs gebaut:

.. code:: common-lisp

   (require 'magit)
   
   (setq git-browser-url-templates
         '(("bitbucket.org" . "https://bitbucket.org/{{repo}}/src/{{branch}}/{{file-name}}#cl-{{lineno}}")
        ("github.com" . "https://github.com/{{repo}}/blob/{{branch}}/{{file-name}}#L{{lineno}}")
        ("pwmt.org" . "https://git.pwmt.org/?p={{repo}}.git;a=blob;f={{file-name}};hb={{branch}}#l{{lineno}}")))
   
   (defun format-gitviewer-url (template vars)
     (let ((expand (lambda (match)
                  (let* ((name (substring match 2 -2))
                         (value (assoc name vars)))
                    (unless value
                      (error (format "Unknown variable %s" name)))
                    (cdr value)))))
       (replace-regexp-in-string "{{.+?}}" expand template)))
     
   
   (defun git-open-in-browser ()
     (interactive)
     (let* ((remote (magit-get-remote nil))
         (remote-url (magit-get "remote" remote "url"))
         (branch (substring (magit-get-tracked-branch) (+ 1 (length remote))))
         (file-name (magit-file-relative-name (buffer-file-name)))
         (lineno (line-number-at-pos)))
       (unless (string-match "\\(@\\|://\\|^\\)\\([^:@/]+?\\)[:/]\\([^/].*?\\)\\(.git\\)?$" remote-url)
         (error "Could not find repo name"))
       (let* ((host-name (match-string 2 remote-url))
           (repo-name (match-string 3 remote-url))
           (url-template (assoc host-name git-browser-url-templates)))
         (unless url-template
        (error (format "Could not find URL template for host %s" host-name)))
         (browse-url (format-gitviewer-url (cdr url-template)
                                        (list
                                         (cons "repo" repo-name)
                                         (cons "branch" branch)
                                         (cons "file-name" file-name)
                                         (cons "lineno" (number-to-string lineno))))))))
