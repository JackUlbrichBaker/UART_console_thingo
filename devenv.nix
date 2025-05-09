{ pkgs, ... }: 

{ 
  env.GREET = "hello"; 

  packages = [ 
    pkgs.python312Packages.textual
    pkgs.python312Packages.pyserial
  ];

  enterShell = ''
    echo $GREET
  ''; 
}

