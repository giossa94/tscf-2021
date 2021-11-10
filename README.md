## Ambiente

En la raíz del repositorio se adjunta un archivo `environment.yml`
para las dependencias de todo el proyecto.

1.  Instalar conda (anaconda o miniconda)
2.  En una nueva terminal --> `conda env create -f environment.yml`
3.  Para activar el ambiente--> `conda activate tscf-2021`
4.  Si queremos eliminarlo --> `conda remove --name tscf-2021 --all`
5.  Si queremos actualizarlo --> `conda env update --file environment.yml`

## Experimentos

- Experimento 0 (main_exp0.py) toma como criterio de parada la igualdad de las tablas. Enfoque centralizado.
- Experimento 2 (main_exp2.py) toma como criterio de parada ventana deslizante. Enfoque centralizado.

