{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    python311Packages.fastapi
    python311Packages.uvicorn
    python311Packages.pip
  ];

  shellHook = ''
    echo "vasp-laksvrddhi-chatbot Environment Ready!"
    export PYTHONPATH=$PWD:$PYTHONPATH
  '';
}