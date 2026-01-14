{
  description = "Environnement de développement pour SAE Splat IUTO";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = function:
        nixpkgs.lib.genAttrs supportedSystems (system: function nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = [
            (pkgs.python3.withPackages (python-pkgs: [
              python-pkgs.pygame   # Pour l'affichage graphique
              python-pkgs.pytest   # Car j'ai vu ton dossier 'tests' !
            ]))
          ];

          # Cette partie est CRUCIALE pour ton projet :
          # Elle dit à Python : "Regarde dans le dossier actuel pour trouver les modules"
          # Sans ça, tes imports entre dossiers (ex: importer const dans serveur) risquent de planter.
          shellHook = ''
            export PYTHONPATH=$PWD/$PYTHONPATH
            echo " Environnement python !"
            echo "Tu peux lancer le serveur avec : python serveur/serveur.py"
          '';
        };
      });
    };
}