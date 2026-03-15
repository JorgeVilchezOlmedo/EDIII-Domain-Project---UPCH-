un# Comandos en Gromacs Uso general 

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


### gmx pdb2gmx -f wt.pdb -o wt.gro -water tip3p
### gmx editconf -f wt.gro -o box.gro -c -d 2.0 -bt triclinic
### gmx solvate -cp box.gro -cs spc216.gro -o solv.gro -p topol.top
### gmx grompp -f ions.mdp -c solv.gro -p topol.top -o ions.tpr
### gmx genion -s ions.tpr -o ions.gro -p topol.top -pname NA -nname CL -neutral
13 sOL
### gmx grompp -f minim.mdp -c ions.gro -p topol.top -o em.tpr
### gmx mdrun -v -deffnm em
## y
### gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr
### gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr
### gmx mdrun -deffnm nvt -v
### gmx mdrun -deffnm npt -v
yy
### gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr
### gmx mdrun -deffnm md -v -pin auto -update gpu

gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr
gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr
gmx mdrun -deffnm npt -v
gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr
gmx mdrun -deffnm md -v -pin auto -update gpu

Posterior
gmx trjconv -f md.xtc -s md.tpr -pbc whole -o whole.xtc

L312R 

V. Análisis de trayectoria y propiedades estructurales
En algun punto para corregir el PBC Y el INDEX no hay mucho problema aparte
Solo haz eso. 

1. Corregir PBC:
echo 1 | gmx trjconv -f md.xtc -s md.tpr -pbc whole -o whole.xtc
2. Crear index:
gmx make_ndx -f md.tpr -o index.ndx
Para modificarlo se utiliza:
gmx make_ndx -f md.tpr -o index.ndx -n index.ndx
● La versión previa del index.ndx se va a guardar con un #.
● Se pueden especificar grupos de estudio como cadenas de proteínas para análisis
posteriores.
● Los grupos (previa verificación en el archivo pdb) se agregan colocando a
#átomo-#átomo.
Para renombrar se utiliza name #grupo {nombre}. Asimismo, para modificar el index.ndx se
agrega -n index.ndx al comando y para revisarlo se usa gmx check -n index.ndx.

Nota: Parece ser que transcribir topologia le falta algun punto aun .
3. Transcribir topología:
gmx convert-tpr -s md.tpr -n index.ndx -o final.tpr
● Para tener el archivo de topología con el número correcto de átomos.
4. Extraer trayectoria corregida:
echo 1 1 | gmx trjconv -f whole.xtc -s md.tpr -pbc nojump -center -o final.xtc -n index.ndx
● Para eliminar saltos y centrar la molécula.
● También se puede colocar la opción -o .pdb para obtener un archivo conjunto
trayectoria + coordenadas.

Se puede intentar usar el Whole y el md tpr en vez de la transcrrpionc parece que hay un error que tengo que consultar a Mauricio.

5. Generar estructura .gro:
gmx editconf -f {.gro inicial} -o final.gro -n index.ndx
● Para obtener un .gro para visualizar el archivo .xtc obtenidos con la misma opción
del index.ndx.
6. Cálculos estadísticos:
Todos se hacen con la opción C-alpha del index. El echo puede variar según el index.ndx.
- Para el RMSD y RMSF:
echo 3 | gmx rms -f final.xtc -s final.tpr -n index.ndx -o rmsd.xvg
echo 3 | gmx rmsf -f final.xtc -s final.tpr -n index.ndx -o rmsf.xvg -res
- Para el área accesible al solvente o sasa:
echo 3 | gmx sasa -f final.xtc -s final.tpr -n index.ndx -o sasa.xvg
- Para el radio de giro:
echo 3 | gmx gyrate -f final.xtc -s final.tpr -n index.ndx -o gyrate.xvg
- Cálculo numérico de puentes de hidrógeno con el index.
echo 1 1  | gmx hbond -f final.xtc -s final.tpr -n index.ndx -num hbond.xvg
SELECCIONAR DOSVECES PROTEINA  



VI. Análisis de componentes principales (PCA)
1. Calcular matriz de covarianza:
gmx covar -s final.tpr -f final.xtc -o eigenval.xvg -v eigenvec.trr
2. Proyectar modos principales:

gmx anaeig -v eigenvec.trr -f final.xtc -proj proj.xvg -first 1 -last 2 -2d 2d_proj.xvg
gmx anaeig -v eigenvec.trr -s md.tpr -f whole.xtc -proj proj.xvg -first 1 -last 2 -2d 2d_proj.xvg

PCA calculado para 3 porque fue de 98 atomos
Carbono alfa entre los 3 , pára los 3.

Parece ser que en este faltaba el -s md tpr luego el xtc va ahi, asi que normal, pero esta anotado aca ahora para ocrregirlo, giual la transcripcion de topologia no importa mucho en este especificamente

● Con -2d 2d_proj.xvg se puede visualizar el gráfico de dispersión de PC2 vs PC1.
- first y -last indican los componentes principales que se quieren proyectar.
  
3. Obtener contribuciones atómicas:
gmx anaeig -v eigenvec.trr -s final.tpr -comp comp.xvg
● Analiza por defecto el PC1, a menos que se especifique con -first y -last.
● Las contribuciones pueden ser analizadas con xmgrace, aunque se recomienda
mejorar la salida utilizando matplotlib.

4. Visualizar desplazamientos estructurales:
gmx anaeig -v eigenvec.trr -s final.tpr -extr extr.pdb -first 1 -last 1

Aqui parece que faltaba el WHole como trayectorai, soea faltaba poner la trayectoria con el -f
gmx anaeig -v eigenvec.trr -s md.tpr -f whole.xtc -extr extr.pdb -first 1 -last 1

Notas:
- Se puede utilizar gmx anaeig -v eigenvec.trr -f final.xtc -s final.tpr -eig 1 2 -extr
traj_pca.xtc para extraer la trayectoria de PC1 y PC2.
- Las estructuras desplazadas permiten visualizar el movimiento asociado al modo
principal.
- La opción -comp permite visualizar la contribución de cada residuo al PCA en las
tres dimensiones x, y, z y el total. La curva indica qué eigenvectors son los que se
deben analizar. Los valores positivos significan que la estructura se mueve para una
dirección y negativos para la dirección opuesta. Representan los dos extremos del
mismo movimiento. Si están más lejos de cero, contribuyen más al PCA.
- Se recomienda visualizar los movimientos esenciales en PyMOL o VMD.
Resultado: trayectoria de los modos de movimiento extr.pdb, proyección de los
componentes principales proj.xvg y 2d_proj.xvg, y la contribución de cada átomo a los
componentes principales comp.xvg

