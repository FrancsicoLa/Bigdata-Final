# Documento de Seguridad y Control de Acceso

## 1. Principios de Seguridad Aplicados

### 1.1 Principio de Mínimo Privilegio
Cada usuario y servicio recibe **únicamente los permisos necesarios** para realizar su función. No se otorga acceso de administrador completo a ningún usuario del equipo.

### 1.2 No Exposición de Credenciales
- **Prohibido:** Escribir `aws_access_key_id` o `aws_secret_access_key` dentro del código fuente.
- **Prohibido:** Subir archivos `.env`, `credentials` o `terraform.tfstate` al repositorio de GitHub.
- **Implementación:** Se configuró un archivo `.gitignore` que bloquea automáticamente estos archivos.

### 1.3 Credenciales Temporales
Se recomienda el uso de credenciales temporales (STS) siempre que sea posible. Las Access Keys configuradas localmente deben rotarse periódicamente.

---

## 2. Gestión de Identidades (IAM)

### 2.1 Usuarios IAM Creados

| Usuario | Propósito | Políticas Asignadas |
| :--- | :--- | :--- |
| Francisco | Miembro del equipo - acceso a consola y CLI | `PowerUserAccess` |
| [Compañero 2] | Miembro del equipo - acceso a consola y CLI | `PowerUserAccess` |
| [Compañero 3] | Miembro del equipo - acceso a consola y CLI | `PowerUserAccess` |

> **Nota:** Se eligió `PowerUserAccess` en lugar de `AdministratorAccess` porque otorga acceso completo a todos los servicios de AWS **excepto** la gestión de IAM (creación/eliminación de usuarios y roles). Esto evita que un error accidental comprometa la seguridad de la cuenta.

### 2.2 Roles de Servicio

| Rol | Servicio que lo usa | Políticas Adjuntas | Justificación |
| :--- | :--- | :--- | :--- |
| `GlueCrawlerRole` | AWS Glue (Jobs y Crawlers) | `AWSGlueServiceRole`, `AmazonS3FullAccess` | Glue necesita leer los CSV de `raw/` y escribir los Parquet en `processed/`. También necesita acceso al catálogo para crear tablas. |

### 2.3 Trust Policy del Rol de Glue
El rol `GlueCrawlerRole` incluye la siguiente Trust Policy para que AWS Glue pueda asumirlo:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "glue.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

---

## 3. Seguridad del Data Lake (S3)

### 3.1 Configuración del Bucket

| Propiedad | Configuración | Justificación |
| :--- | :--- | :--- |
| Nombre del Bucket | `big-data-project-gang-{account_id}` | El sufijo con el ID de cuenta garantiza unicidad global |
| Acceso Público | **Bloqueado** (Block All Public Access) | Los datos de pesca no deben ser accesibles desde internet |
| Versionado | Deshabilitado | No es necesario para este proyecto académico |
| Cifrado | SSE-S3 (Server-Side Encryption) | Cifrado en reposo por defecto de AWS |

### 3.2 Estructura de Zonas del Data Lake

| Zona | Ruta en S3 | Contenido | Quién escribe | Quién lee |
| :--- | :--- | :--- | :--- | :--- |
| Raw | `s3://bucket/raw/` | CSV originales sin modificar | Terraform (ingesta inicial) | Glue Job |
| Processed | `s3://bucket/processed/` | Parquet particionado por año | Glue Job | Athena, QuickSight |
| Curated | `s3://bucket/curated/` | Vistas materializadas (futuro) | Athena CTAS | QuickSight |

---

## 4. Seguridad en el Repositorio de GitHub

### 4.1 Archivos Protegidos por `.gitignore`

```
# Credenciales AWS
.aws/
credentials

# Estado de Terraform (contiene ARNs y metadata sensible)
*.tfstate
*.tfstate.*
.terraform/

# Datos pesados (penalización de -10 puntos si se suben)
data_full/
*.csv
!data_samples/*.csv
```

### 4.2 Verificación Pre-Push
Antes de cada `git push`, el equipo verifica que:
- [ ] No hay archivos `.csv` de más de 1 MB en el staging area.
- [ ] No hay archivos con extensión `.tfstate` en el staging area.
- [ ] No hay cadenas que contengan `AKIA` (prefijo de Access Keys de AWS) en ningún archivo.

---

## 5. Seguridad en Amazon Athena

| Control | Implementación |
| :--- | :--- |
| Resultados de queries | Se almacenan en `s3://bucket/athena-results/` dentro del mismo bucket protegido |
| Workgroup | Se usa el workgroup `primary` con límite de escaneo de datos |
| Acceso a tablas | Solo los usuarios con `PowerUserAccess` pueden ejecutar queries |

---

## 6. Diagrama de Flujo de Permisos

```
Usuarios IAM (PowerUserAccess)
    │
    ├── Consola AWS ──► S3 (lectura/escritura)
    │                  ► Glue (crear/ejecutar jobs)
    │                  ► Athena (ejecutar queries)
    │                  ► QuickSight (crear dashboards)
    │
    └── NO pueden ──► Crear/borrar usuarios IAM
                     ► Modificar roles
                     ► Cambiar políticas de billing

GlueCrawlerRole (Rol de servicio)
    │
    ├── Puede ──► Leer S3 (raw/)
    │           ► Escribir S3 (processed/)
    │           ► Leer/escribir Glue Data Catalog
    │
    └── NO puede ──► Acceder a otros buckets
                    ► Crear usuarios
                    ► Ejecutar queries en Athena
```
