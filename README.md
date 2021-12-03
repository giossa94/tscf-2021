## Dependencias

### Ambiente de Python
En la raíz del repositorio se adjunta un archivo `environment.yml`
para las dependencias de todo el proyecto.

1.  Instalar conda (anaconda o miniconda)
2.  En una nueva terminal --> `conda env create -f environment.yml`
3.  Para activar el ambiente--> `conda activate tscf-2021`
4.  Si queremos eliminarlo --> `conda remove --name tscf-2021 --all`
5.  Si queremos actualizarlo --> `conda env update --file environment.yml`

### Imagen de Docker

1. Pararse junto al Dockerfile --> `cd fat_tree_generator/Dockerfiles/kathara-frr-tscf2021` 
2. Correr `docker build -t kathara/frr-tscf2021 .`

### Tshark

Para poder correr los experimentos de ventana deslizante se necesita tener instalado TShark en el sistema operativo.

## Experimentos

- **Experimento 0**: (main_exp0.py) toma como criterio de parada la igualdad de las tablas. Enfoque centralizado.
- **Experimento 1**: (main_exp1.py) toma como criterio de parada la igualdad de las tablas. Enfoque distribuido.
- **Experimento 2**: (main_exp2.py) toma como criterio de parada ventana deslizante. Enfoque centralizado.
- **Experimento 3**: (main_exp3.py) toma como criterio de parada ventana deslizante. Enfoque distribuido.

## Parámetros

Los parámetros se usan al ejecutar cada experimento. Por ejemplo: ``python main_exp3.py -k=4 -w=10``

- ``-k`` es el número k natural que define el Fat Tree a emular. Por defecto es ``k=4``.
- ``-p`` es la cantidad de planos deseada. Por defecto es ``p=k/2``.
- ``-c`` corre ``kathara lclean`` en el laboratorio previo a iniciar la emulación. Por defecto es ``c=True``.
- ``-w`` es el tamaño de ventana a usar. Es útil solo en experimentos de ventana deslizante. Por defecto es ``w=10``.
- ``-t`` es el umbral a usar. Es útil solo en experimentos de ventana deslizante. Por defecto es ``t=0.5``.
