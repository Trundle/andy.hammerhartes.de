===================================
Introducing nix-install-pkgs-action
===================================

:date: 2022-11-27 20:00
:tags: en, nix

One of the more frustrating experiences is when your project is nicely
``Nix``-ified, and yet your CI/CD workflow is full of "install this, install
that" steps. Even worse, the install steps duplicate a lot of information
already contained in your Nix files. At `YAXI`_, we wanted to re-use our
projects' Nix packaging. And this is why we came up with
`nix-install-pkgs-action`_: It allows you to re-use your project's flake in a
GitHub Actions workflow.


Prerequisites
=============

The action requires a flake-enabled Nix with support for `profiles
<https://nixos.org/manual/nix/stable/command-ref/new-cli/nix3-profile.html>`_.
If you aren't running `a self-hosted GitHub runner
<https://search.nixos.org/options?from=0&size=50&sort=relevance&type=packages&query=services.github-runner>`_
on NixOS, you can use the `cachix/install-nix-action
<https://github.com/cachix/install-nix-action#usage-with-flakes>`_ to install a
flake-enabled Nix.


Usage
=====

The action takes a comma-separated list of packages to install as input
``packages``.  The following step will install ``myPackage`` from your flake's
package output:

.. code-block:: yaml

   - uses: yaxitech/nix-install-pkgs-action@v3
     with:
       packages: ".#myPackage"
      
The package's binaries will be added to ``PATH`` and following steps can use
them.

Each package can be prefixed with a flake reference. If no flake reference is
given, ``nixpkgs`` is assumed. Extending on the previous example, the following
step will install ``figlet`` and ``swift`` from ``nixpkgs`` and ``myPackage``
from your flake's package output.

.. code-block:: yaml

   - uses: yaxitech/nix-install-pkgs-action@v3
     with:
       packages: "figlet, nixpkgs#swift, .#myPackage"

You can also install derivations using some Nix expression. Within the
expression, ``pkgs`` will refer to your flake's imported `nixpkgs`. For
example, if you want a Python environment with `lxml` and `py.test` installed,
you can use the following step:

.. code-block:: yaml

   - uses: yaxitech/nix-install-pkgs-action@v3
     with:
       expr: 'pkgs.python3.withPackages(ps: with ps; [lxml pytest])'

The above example shows that the action is also useful if your project doesn't
use Nix or flakes at all. You can still use it to install any package from the
Nix packages collection.

Please try it out! We've been using the action for quite some time now and find
it immensely useful. Still, don't hesitate to open an `issue
<https://github.com/yaxitech/nix-install-pkgs-action/issues>`_ in case you
encounter any road blocks.


.. _nix-install-pkgs-action: https://github.com/marketplace/actions/install-nix-packages
.. _YAXI: https://yaxi.tech/

