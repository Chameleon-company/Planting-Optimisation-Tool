# POT Database Schema Definition (SQLAlchemy ORM)

## TABLE: `farm_agroforestry_association`

| Column Name | SQL Type | Nullable | Primary Key | Foreign Key |
| :--- | :--- | :--- | :--- | :--- |
| `farm_id` | `Integer` | No | Yes | id |
| `agroforestry_type_id` | `Integer` | No | Yes | id |
## TABLE: `species_agroforestry_association`

| Column Name | SQL Type | Nullable | Primary Key | Foreign Key |
| :--- | :--- | :--- | :--- | :--- |
| `species_id` | `Integer` | No | Yes | id |
| `agroforestry_type_id` | `Integer` | No | Yes | id |
## TABLE: `species_soil_texture_association`

| Column Name | SQL Type | Nullable | Primary Key | Foreign Key |
| :--- | :--- | :--- | :--- | :--- |
| `species_id` | `Integer` | No | Yes | id |
| `soil_texture_id` | `Integer` | No | Yes | id |
## TABLE: `farms`

| Column Name | SQL Type | Nullable | Primary Key | Foreign Key |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `Integer` | No | Yes |  |
| `rainfall_mm` | `Integer` | No | No |  |
| `temperature_celsius` | `Integer` | No | No |  |
| `elevation_m` | `Integer` | No | No |  |
| `ph` | `Float` | No | No |  |
| `soil_texture_id` | `Integer` | No | No | id |
| `area_ha` | `Float` | No | No |  |
| `latitude` | `Float` | No | No |  |
| `longitude` | `Float` | No | No |  |
| `coastal` | `Boolean` | No | No |  |
| `riparian` | `Boolean` | No | No |  |
| `nitrogen_fixing` | `Boolean` | No | No |  |
| `shade_tolerant` | `Boolean` | No | No |  |
| `bank_stabilising` | `Boolean` | No | No |  |
| `slope` | `Float` | No | No |  |
## TABLE: `species`

| Column Name | SQL Type | Nullable | Primary Key | Foreign Key |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `Integer` | No | Yes |  |
| `name` | `String` | No | No |  |
| `common_name` | `String` | No | No |  |
| `rainfall_mm_min` | `Integer` | No | No |  |
| `rainfall_mm_max` | `Integer` | No | No |  |
| `temperature_celsius_min` | `Integer` | No | No |  |
| `temperature_celsius_max` | `Integer` | No | No |  |
| `elevation_m_min` | `Integer` | No | No |  |
| `elevation_m_max` | `Integer` | No | No |  |
| `ph_min` | `Float` | No | No |  |
| `ph_max` | `Float` | No | No |  |
| `coastal` | `Boolean` | No | No |  |
| `riparian` | `Boolean` | No | No |  |
| `nitrogen_fixing` | `Boolean` | No | No |  |
| `shade_tolerant` | `Boolean` | No | No |  |
| `bank_stabilising` | `Boolean` | No | No |  |
## TABLE: `soil_textures`

| Column Name | SQL Type | Nullable | Primary Key | Foreign Key |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `Integer` | No | Yes |  |
| `texture_name` | `String` | No | No |  |
## TABLE: `agroforestry_types`

| Column Name | SQL Type | Nullable | Primary Key | Foreign Key |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `Integer` | No | Yes |  |
| `type_name` | `String` | No | No |  |
