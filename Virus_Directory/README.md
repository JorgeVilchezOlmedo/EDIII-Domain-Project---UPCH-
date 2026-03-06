# Comandos en Gromacs Uso general 

## Usar el cd , asegurarse de crear una carpeta unica para cada cosa antes de comenzar a actuar
### Crear carpetas para cada simulacion de cada mutante. Definir mdp de *ions, nvt npt y minim*  (Reminder, how to nano every parameter), estos se pueden configurar en el nano si es que quieres cambiar parametros, por ahora no es necesario

##Recordar anotar nano y que signfica cada parametro##

#Transformar a caja, centrar el sistema, la opcion de centro puede ser usada para cambiar el centro geometrico. 
#BT para igualar el tipo de caja, con triclinica , cubica, dodecaedrica y octahedrica, el largo es la menor distancia de dos hexagonos opuest

gmx pdb2gmx -f (protname.pdb) -o wt.gro -water tip3pp

#gmx pdb2gmx es para añadir hidrogenos a moleculas y generar coordinadas, hace la topologia, buscara entre forcefields en subdirecciones , es para seleccionar el forcefield que se usar, en la mayoria de casos amber99sb, el programa tiene inteligencia limtada, lee los archivos que permiten hacer enlaces especiales, puede generar que se selecciones que tipo de residuo es requerido, puede ser protonado, desprotonado, esto es automatico pero se puede seleccinonar. 
#-f (nombre_original_archivo) 
#-o nombre a introducir .gro
#-water (modelo a utilizar de agua, comiunmente tip3p) (Recordar leer que es tip3p más tecnicamente)

gmx editconf -f ()


gmx pdb2gmx -f wt.pdb -o wt.gro -water tip3p
gmx editconf -f wt.gro -o box.gro -c -d 2.0 -bt triclinic
gmx solvate -cp box.gro -cs spc216.gro -o solv.gro -p topol.top
gmx grompp -f ions.mdp -c solv.gro -p topol.top -o ions.tpr
gmx genion -s ions.tpr -o ions.gro -p topol.top -pname NA -nname CL -neutral
gmx grompp -f minim.mdp -c ions.gro -p topol.top -o em.tpr
gmx mdrun -v -deffnm em
gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr
gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr
gmx mdrun -deffnm npt -v
gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr
gmx mdrun -deffnm md -v -pin auto -update gpu
