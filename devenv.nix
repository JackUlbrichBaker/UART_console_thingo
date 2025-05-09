{ pkgs, ... }: 

{ 
  env.GREET = "hello"; 

  packages = [ 
    pkgs.python312Packages.textual
  ];

  enterShell = ''
    echo $GREET
  ''; 
}

