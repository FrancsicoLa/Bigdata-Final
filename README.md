# 🐟 AWS Data Engineering Capstone - Sea Around Us

## 📊 Visión General
Este repositorio contiene el código fuente y la documentación de nuestro Proyecto Final (Ruta A) para el curso de AWS Academy Data Engineering. 
El objetivo del proyecto es procesar datos globales de pesca marítima (Sea Around Us) diseñando, implementando y operando una tubería de datos (Data Pipeline) automatizada de extremo a extremo en AWS utilizando **Amazon S3, AWS Glue, Amazon Athena y Amazon QuickSight**.

---

## 🏗️ Arquitectura del Proyecto
![Arquitectura del Proyecto](orchestration/architecture.png)

Nuestro Data Lake está dividido en 3 zonas (Raw, Processed, Curated). Toda la infraestructura está definida como código (IaC) mediante **Terraform**. El procesamiento de los datos crudos a formato **Parquet particionado** se realiza mediante un cluster de **PySpark** en AWS Glue, lo cual optimizó nuestros costos de escaneo en Athena en más de un 99%.

---

## 👥 Miembros del Equipo y Roles

| Nombre | Rol | Aportación y Responsabilidad Principal |
| :--- | :--- | :--- |
| **Diego** | **Rol 1: Data Engineer** | Ingesta a S3 automatizada, Transformación PySpark (CSV a Parquet), Particionamiento por año, Configuración del Glue Crawler. |
| **Ángela** | **Rol 2: Data Quality Engineer** | Implementación de 10 reglas estrictas de validación de negocio usando Pandas, descubrimiento de registros duplicados de origen, y generación de reporte HTML automatizado. |
| **Daniela** | **Rol 3: Analytics Engineer** | Justificación del particionamiento, Benchmark de rendimiento comparativo (CSV vs Parquet), Vistas SQL avanzadas en Athena y construcción del Dashboard interactivo en QuickSight. |
| **Francisco** | **Rol 4: Orchestration & Ops** | **Líder de Integración:** Diseño de máquina de estados (Step Functions), desarrollo de Script Bot en Python para ejecución *End-to-End* desatendida, diseño del diagrama arquitectónico, protección del repositorio (.gitignore) y gobierno de seguridad IAM. |

---

## 📂 Estructura del Repositorio

```text
data-eng-project-team01/
├── README.md                           # Documentación principal
├── .gitignore                          # Protección de credenciales AWS y datos pesados
├── pipeline/                           # Rol 1: Data Engineer
│   ├── scripts/glue_job.py             # Código PySpark: limpieza y conversión a Parquet
│   └── terraform/                      # Infraestructura como Código (S3, Glue Job, Crawler)
│       ├── main.tf 
│       └── variables.tf
├── data_quality/                       # Rol 2: Data Quality Engineer
│   ├── validate_quality.py             # Script con 10 reglas de calidad
│   └── report.html                     # Reporte de resultados PASS/FAIL
├── analytics/                          # Rol 3: Analytics Engineer
│   ├── benchmark.md                    # Análisis de costos/tiempos y resultados de queries
│   └── dashboard.md                    # Documentación del Dashboard en QuickSight
├── orchestration/                      # Rol 4: Orchestration & Ops
│   ├── auto_execute.py                 # Bot maestro: Orquestador Python de extremo a extremo
│   ├── step_functions_definition.json  # Máquina de estados oficial (AWS Step Functions)
│   ├── security.md                     # Políticas IAM y control de accesos
│   └── architecture.png                # Diagrama visual
└── presentation/
    ├── slides.html                     # Presentación del equipo
    └── guion_diapositivas.md           # Guion exacto de la defensa oral
```

---

## 🚀 Cómo Ejecutar el Proyecto (End-to-End)

El objetivo principal de nuestro pipeline es que corra **sin intervención manual**. Hemos logrado automatizar el despliegue de infraestructura y el procesamiento lógico.

### Paso 1: Desplegar la Infraestructura (Rol 1 & 4)
Para crear el Data Lake, configurar los roles IAM y preparar los servicios de AWS Glue:
```bash
cd pipeline/terraform
terraform init
terraform apply -auto-approve
```

### Paso 2: Ejecutar el Orquestador Automatizado (Rol 4)
Para correr el pipeline completo de procesamiento sin tocar la consola de AWS:
```bash
cd ../..
python orchestration/auto_execute.py
```
**¿Qué hace este Bot de Python?**
1. **Activa el Glue Job:** Inicia la transformación de casi 2 millones de filas (CSV a Parquet particionado).
2. **Monitoreo:** Entra en un ciclo de espera (Wait State) manejando posibles errores (`FAILED`).
3. **Catálogo:** Una vez finalizado el Job, activa el Glue Crawler para inferir el esquema (Schema-on-Read).
4. **Validación y Benchmark:** Lanza automáticamente 6 consultas SQL hacia Amazon Athena comparando la velocidad de los CSV vs Parquet, imprimiendo el ahorro del 99% directamente en la terminal.

---

## 🔒 Seguridad y Gobernanza
- **Protección de Secretos:** Implementamos un archivo `.gitignore` robusto que impide la exposición de la carpeta `.aws/credentials` y los archivos locales de Terraform (`.tfstate`).
- **Mínimo Privilegio:** Todos los miembros del equipo operan con la política `PowerUserAccess` y los servicios interactúan exclusivamente mediante el rol dedicado `GlueCrawlerRole`.
- Detalles completos en `orchestration/security.md`.
