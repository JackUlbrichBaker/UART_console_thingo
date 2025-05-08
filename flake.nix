{
  description = "Python Console Dev Venv";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python3;
        python-with-rich = python.withPackages (ps: with ps; [ rich ]);
      in {
        devShells.default = pkgs.mkShell {
          name = "python-rich-shell";
          buildInputs = [ python-with-rich pkgs.python3Packages.venv ];

          shellHook = ''
            echo "Creating virtual environment in .venv..."
            if [ ! -d .venv ]; then
              ${python}/bin/python -m venv .venv
              echo "Virtual environment created."
            else
              echo ".venv already exists."
            fi
            echo "Activating virtual environment."
            source .venv/bin/activate
          '';
        };
      });
}

