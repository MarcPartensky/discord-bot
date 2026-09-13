{
  description = "discord-bot dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python312;

      # libs cherchees au runtime par les wheels manylinux
      libs = with pkgs; [
        stdenv.cc.cc.lib # libstdc++, requis par a peu pres tout
        zlib
        openssl
        libffi
        libopus # py-cord[voice]
        libxcrypt-legacy # libcrypt.so.1, pour le python 3.8 si besoin
        postgresql.lib # psycopg2
      ];
    in {
      devShells.default = pkgs.mkShell {
        packages = [
          python
          pkgs.uv
          pkgs.just
          pkgs.ffmpeg # py-cord[voice], nightcore
          pkgs.chromedriver # selenium
          pkgs.chromium
        ];

        env = {
          UV_PYTHON = python.interpreter;
          UV_PYTHON_DOWNLOADS = "never";
          UV_PYTHON_PREFERENCE = "only-system";
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath libs;
        };

        shellHook = ''
          echo "python $(python --version), uv $(uv --version)"
          [ -d .venv ] || uv venv
          source .venv/bin/activate
        '';
      };
    });
}
