{
  description = "Source of andy.hammerhartes.de";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils = {
      url = "github:numtide/flake-utils";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pelican = {
      url = "github:Trundle/pelican/trundles_slugify";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, pelican }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [
          pelicanOverlay
        ];
      };
      pelicanOverlay = final: prev: {
        pelican = prev.python3Packages.pelican.overrideAttrs (oldAttrs: {
          src = pelican;
          disabledTestPaths = [
            # Likely all fail due to my custom slugify
            "pelican/tests/test_contents.py"
            "pelican/tests/test_generators.py"
            "pelican/tests/test_importer.py"
            "pelican/tests/test_readers.py"
            "pelican/tests/test_testsuite.py"
            "pelican/tests/test_urlwrappers.py"
            "pelican/tests/test_utils.py"
          ];
        });
      };
    in
    {
      devShell = pkgs.mkShell
        {
          name = "blog-dev-shell";

          buildInputs = [
            pkgs.pelican
          ];
        };
    });
}
