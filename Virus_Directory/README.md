
## Comandos en Gromacs posterior a uso generla
cd home/Jorge/WNV_WT
#Crear carpetas para cada simulacion de cada mutante, pero primero definir los mdp ions nvt npt y minim , estos se pueden configurar en el nano si es que quieres cambiar parametros, por ahora no es necesario

##Recordar anotar nano y que signfica cada parametro##

#Transformar a caja, centrar el sistema, la opcion de centro puede ser usada para cambiar el centro geometrico. 
#BT para igualar el tipo de caja, con triclinica , cubica, dodecaedrica y octahedrica, el largo es la menor distancia de dos hexagonos opuest

gmx pdb2gmx -f (protname.pdb) -o wt.gro -water tip3pp

#gmx pdb2gmx es para añadir hidrogenos a moleculas y generar coordinadas, hace la topologia, buscara entre forcefields en subdirecciones , es para seleccionar el forcefield que se usar, en la mayoria de casos amber99sb, el programa tiene inteligencia limtada, lee los archivos que permiten hacer enlaces especiales, puede generar que se selecciones que tipo de residuo es requerido, puede ser protonado, desprotonado, esto es automatico pero se puede seleccinonar. 
#-f (nombre_original_archivo) 
#-o nombre a introducir .gro
#-water (modelo a utilizar de agua, comiunmente tip3p) (Recordar leer que es tip3p más tecnicamente)

gmx editconf -f ()
