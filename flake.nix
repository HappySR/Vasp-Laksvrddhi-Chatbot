{
  description = "vasp-laksvrddhi-chatbot";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python311Packages;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python311
            pythonPackages.fastapi
            pythonPackages.uvicorn
            pythonPackages.pip
            pythonPackages.setuptools
            pythonPackages.wheel
          ];

          shellHook = ''
            echo "🚀 vasp-laksvrddhi-chatbot"
            echo "Python version: $(python --version)"
            echo "FastAPI available: $(python -c 'import fastapi; print(fastapi.__version__)')"
            echo ""
            echo "To run the app:"
            echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
            echo ""
          '';
        };

        packages.default = pkgs.python311Packages.buildPythonApplication {
          pname = "chatbot-fastapi";
          version = "1.0.0";
          
          src = ./.;
          
          propagatedBuildInputs = with pythonPackages; [
            fastapi
            uvicorn
          ];
          
          doCheck = false;
        };
      });
}