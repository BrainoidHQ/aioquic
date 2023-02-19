{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    python310
    pipenv
    openssl
    go-task
  ];

  PIPENV_VENV_IN_PROJECT = 1;
}
