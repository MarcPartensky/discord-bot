{
  description = "discord-bot";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python312;
      src = ./.;

      libs = with pkgs; [
        stdenv.cc.cc.lib
        zlib
        openssl
        libffi
        libopus
        libxcrypt-legacy
        postgresql.lib
      ];
    in {
      packages.default = pkgs.writeShellApplication {
        name = "discord-bot";
        runtimeInputs = [python pkgs.uv pkgs.ffmpeg pkgs.chromedriver pkgs.chromium];
        text = ''
          export UV_PYTHON=${python.interpreter}
          export UV_PYTHON_DOWNLOADS=never
          export UV_PYTHON_PREFERENCE=only-system
          export UV_PROJECT_ENVIRONMENT="''${STATE_DIRECTORY:-$PWD}/venv"
          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath libs}

          uv sync --frozen --no-dev --project ${src}
          exec "$UV_PROJECT_ENVIRONMENT/bin/python" -m discord_bot
        '';
      };

      devShells.default = pkgs.mkShell {
        packages = [python pkgs.uv pkgs.just pkgs.ffmpeg pkgs.chromedriver pkgs.chromium];
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
    })
    // {
      nixosModules.default = {
        config,
        lib,
        pkgs,
        ...
      }: let
        cfg = config.services.discord-bot;
      in {
        options.services.discord-bot = {
          enable = lib.mkEnableOption "discord-bot";
          package = lib.mkOption {
            type = lib.types.package;
            default = self.packages.${pkgs.stdenv.hostPlatform.system}.default;
          };
          environmentFile = lib.mkOption {type = lib.types.path;};
          host = lib.mkOption {
            type = lib.types.str;
            default = "127.0.0.1";
          };
          port = lib.mkOption {
            type = lib.types.port;
            default = 8050;
          };
        };

        config = lib.mkIf cfg.enable {
          systemd.services.discord-bot = {
            wantedBy = ["multi-user.target"];
            wants = ["network-online.target"];
            after = ["network-online.target"];
            environment = {
              DISCORD_BOT_HOST = cfg.host;
              DISCORD_BOT_PORT = toString cfg.port;
            };
            serviceConfig = {
              ExecStart = lib.getExe cfg.package;
              EnvironmentFile = cfg.environmentFile;
              DynamicUser = true;
              StateDirectory = "discord-bot";
              WorkingDirectory = "/var/lib/discord-bot";
              Restart = "always";
              RestartSec = 10;
              ProtectSystem = "strict";
              ProtectHome = true;
              PrivateTmp = true;
              NoNewPrivileges = true;
              CacheDirectory = "discord-bot";
              Environment = [
                "UV_CACHE_DIR=/var/cache/discord-bot"
                "HOME=/var/lib/discord-bot"
              ];
            };
          };
        };
      };
    };
}
