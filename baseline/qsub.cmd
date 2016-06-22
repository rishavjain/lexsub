@ECHO OFF

::ECHO %*

FOR /L %%i IN (1,1,8) DO (
  SHIFT
)

SET cmd=

:args
IF "%1"=="" ( GOTO end )
SET cmd=%cmd% %1
SHIFT
GOTO args

:end
SET cmd=%cmd:~+1%
%cmd%