# Data Dictionary for Product Owner Datasets

This document provides an overview of the datasets supplied by the Product Owners. It describes the purpose of each file and outlines the associated data schema, including column names, data types, units, and requirements. All datasets referenced in this document are stored in Microsoft Teams > Planting Optimisation Tool > Shared > Datasets. The information herein was verified by the Product Owner as accurate at the time of publication (23 January 2026) and represents the current state of the product.

**Note:** Some filenames include a date and a unique identifier.

## Tree O2 Datasets

These datasets contain tree monitoring data collected from farmers across multiple municipalities in Timor-Leste.

### Gold Standard (GS) Projects

#### Data Schema

| Column Name            | Type    | Unit        | Description                  | Requirement |
|------------------------|---------|-------------|------------------------------|-------------|
| fob_id                 | String  | –           | Unique tree record ID        | Required    |
| scan_date              | Date    | dd/mm/yyyy  | Date the tree was scanned    | Optional    |
| planted_year           | Integer | year        | Year the tree was planted    | Optional    |
| planted_month          | Integer | month       | Month the tree was planted   | Optional    |
| trunk_circumference    | Float   | cm          | Tree trunk circumference     | Optional    |
| tree_species           | String  | –           | Tree species name            | Optional    |

#### Project Files

| File Name                                    | Description                                                                     |
|----------------------------------------------|---------------------------------------------------------------------------------|
| GS4210_Tree_Data.csv                         | Tree monitoring data from Baguia Administrative Post, Baucau Municipality       |
| GS4210_Tree_Data_2.csv                       | Tree monitoring data from Baguia Administrative Post, Baucau Municipality       |
| GS11743_Tree_data.csv                        | Tree monitoring data from Cova Lima Municipality                                |
| GS11800_Tree_Data.csv                        | Tree monitoring data from Baucau Municipality                                   |
| GS11801_Tree_Data.csv                        | Tree monitoring data from Liquiçá Municipality                                  |
| GSXXXX_RM_Quelicai_Laga_Tree_Data.csv        | Tree monitoring data from Quelicai and Laga, Baucau Municipality                |
| GSxxxxx_RM_Lautem_Lospalos_Tree_Data.csv     | Tree monitoring data from Lospalos, Lautém Municipality                         |
| GSxxxxx_RM_Viqueque_Uatucarbau_Tree_Data.csv | Tree monitoring data from Uatucarbau Administrative Post, Viqueque Municipality |

**Note:** These files use the GS prefix followed by a project number (e.g. GS4210). This indicates that the project is certified 
under the Gold Standard program, allowing farmers to earn income from carbon credits.

#### Other Projects

#### Data Schema

| Column Name                  | Type     | Unit               | Description                               | Requirement |
|------------------------------|----------|--------------------|-------------------------------------------|-------------|
| FobID                        | String   | –                  | Unique tree record ID                     | Required    |
| EarliestScanTimestamp        | DateTime | dd/mm/yyyy hh:mm   | First scan timestamp for the tree         | Required    |
| LatestScanTimestamp          | DateTime | dd/mm/yyyy hh:mm   | Latest scan timestamp for the tree        | Required    |
| ScanCount                    | Integer  | –                  | Number of times the tree was scanned      | Required    |
| TreeTypeName                 | String   | –                  | Tree species name                         | Required    |
| EstimatedPlantedMonth        | Integer  | month              | Estimated month the tree was planted      | Optional    |
| EstimatedPlantedYear         | Integer  | year               | Estimated year the tree was planted       | Optional    |
| EstimatedPlatedDate          | String   | –                  | Estimated planted date                    | Optional    |
| Latitude                     | Float    | deg                | Tree location latitude                    | Required    |
| Longitude                    | Float    | deg                | Tree location longitude                   | Required    |
| TrunkDiameter                | Float    | cm                 | Tree trunk diameter                       | Optional    |
| TrunkCircumference           | Float    | cm                 | Tree trunk circumference                  | Optional    |
| Height                       | Float    | m                  | Tree height                               | Optional    |
| CarbonDioxide                | Float    | kg                 | Estimated carbon dioxide stored           | Optional    |
| PhotoURL                     | String   | –                  | Link to tree photo                        | Optional    |
| FarmerCardID                 | String   | –                  | Unique farmer ID card number              | Optional    |
| FarmerName                   | String   | –                  | Farmer full name                          | Optional    |
| FarmerStreetAddress          | String   | –                  | Farmer street address                     | Optional    |
| FarmerSuburbLocality         | String   | –                  | Farmer suburb or locality                 | Optional    |
| FarmerRegion                 | String   | –                  | Farmer region                             | Optional    |
| FarmerStateProvince          | String   | –                  | Farmer municipality                       | Optional    |
| FarmerCountryCode            | String   | –                  | Country code                              | Optional    |

#### Project Files

| File Name                                                | Description                                                                         |
|----------------------------------------------------------|-------------------------------------------------------------------------------------|
| Baguia_Trees_2025-11-25_038a64.csv                       | Tree monitoring data from Baguia, Baucau Municipality                               |
| CCC_Trees_2025-11-25_2da6c9.csv                          | Tree monitoring data managed with local partner CCC (Covalima Community Centre)     |
| Lautem-Lospalos_Trees_2025-11-25_564e36.csv              | Tree monitoring data from Lospalos, Lautém Municipality                             |
| NETIL_Trees_2025-11-25_859919.csv                        | Tree monitoring data managed with local partner NETIL                               |
| Quelicai-Laga_Trees_2025-11-25_36be59.csv                | Tree monitoring data from Quelicai and Laga, Baucau Municipality                    |
| TV_Trees_2025-11-25_56c5f6.csv                           | Tree monitoring data managed with local partner TV                                  |
| Viqueque_Uatucarbau_Uatulari_Trees_2025-11-25_4930fd.csv | Tree monitoring data from Viqueque, Uatucarbau, and Uatulari, Viqueque Municipality |

## TreeO2 (Dec 5) Datasets

These are the most recent TreeO2 datasets, provided by the Product Owners as of 5 December 2025. They include additional columns, namely farmer identification (scanned_to_farmer_id) and tree location (latitude and longitude).

### Gold Standard (GS) Projects

#### Data Schema

| Column Name             | Type    | Unit        | Description                                      | Requirement |
|-------------------------|---------|-------------|--------------------------------------------------|-------------|
| fob_id                  | String  | –           | Unique tree record ID                            | Required    |
| scan_date               | Date    | dd/mm/yyyy  | Date the tree was scanned                        | Optional    |
| scanned_to_farmer_id    | Integer | –           | Farmer ID linked to the scan                     | Optional    |
| farmer_card_id          | String  | –           | Farmer card ID                                   | Optional    |
| planted_year            | Integer | year        | Year the tree was planted                        | Optional    |
| planted_month           | Integer | month       | Month the tree was planted                       | Optional    |
| trunk_circumference     | Float   | cm          | Tree trunk circumference                         | Optional    |
| tree_species            | String  | –           | Tree species name                                | Optional    |
| latitude                | Float   | deg         | GPS latitude coordinate of the tree location     | Optional    |
| longitude               | Float   | deg         | GPS longitude coordinate of the tree location    | Optional    |

#### Project Files

| File Name                                    | Description                                                                                                                    |
|----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| GS4210_Baguia_Tree_Data (Files 1–6)          | Tree monitoring data from Baguia Administrative Post, Baucau Municipality. The data is divided into six files                  |
| GS11743_CCC_Covalima_Tree_Data (1).csv       | Tree monitoring data from Covalima Municipality. Data collection is managed with local partner Covalima Community Centre (CCC) |
| GS11800_TV_Baucau_Tree_Data (1).csv          | Tree monitoring data from Baucau Municipality. Data collection is managed with local partner TV                                |
| GS11801_NETIL_Liquica_Tree_Data (1).csv      | Tree monitoring data from Liquiçá Municipality. Data collection is managed with local partner NETIL                            |

### Regional Management (RM) Projects

#### Project Files

| File Name                                    | Description                                                              |
|----------------------------------------------|--------------------------------------------------------------------------|
| RM_Lautem-Lospalos_Tree_Data.csv             | Tree monitoring data from Lospalos, Lautém Municipality                  |
| RM_Quelicai-Laga_Tree_Data.csv               | Tree monitoring data from Quelicai and Laga, Baucau Municipality         |
| RM_Viqueque-Uatucarbau-Uatulari_Tree_Data.csv| Tree monitoring data from Uatucarbau and Uatulari, Viqueque Municipality |

**Note:** These files use the RM prefix and relate to locally managed projects.

## Species Data Datasets

### List of Riparian and Coastal Species.xlsx  

Tree species suitable for riparian and coastal planting.

#### Riparian species

| Column Name      | Type    | Unit | Description                        | Requirement |
|------------------|---------|------|------------------------------------|-------------|
| Sr. No.          | Integer | –    | Serial number                      | Required    |
| Scientific Name  | String  | –    | Scientific name of the tree        | Required    |
| Common Name      | String  | –    | Common name of the tree            | Optional    |
| Remark           | String  | –    | Notes on where the tree grows      | Optional    |
| Reference        | String  | –    | Source of the information          | Optional    |

#### Coastal species

| Column Name      | Type    | Unit | Description                        | Requirement |
|------------------|---------|------|------------------------------------|-------------|
| Sr. No.          | Integer | –    | Serial number                      | Required    |
| Scientific Name  | String  | –    | Scientific name of the tree        | Required    |
| Common Name      | String  | –    | Common name of the tree            | Optional    |
| Remark           | String  | –    | Notes on where the tree grows      | Optional    |
| Reference        | String  | –    | Source of the information          | Optional    |

---

### Proposed Species for Future Inclusion.xlsx  

Tree species proposed for inclusion in future planting programs.

#### Sheet1

| Column Name              | Type    | Unit | Description                               | Requirement |
|--------------------------|---------|------|-------------------------------------------|-------------|
| Sr. No.                  | Integer | –    | Serial number                             | Required    |
| Common Name              | String  | –    | Common name of the tree                   | Required    |
| Remark                   | String  | –    | Notes on the species                      | Optional    |
| Provisional Id           | String  | –    | Provisional scientific identification     | Optional    |
| Location                 | String  | –    | Location where the species was observed   | Optional    |
| Suggested by             | String  | –    | Person or group who suggested the species | Optional    |
| Identification Characters| String  | –    | Key identification features               | Optional    |
| Use                      | String  | –    | Reported uses of the species              | Optional    |
| Photographs Link         | String  | –    | Link to photographs                       | Optional    |
| Flowering                | String  | –    | Flowering information                     | Optional    |

---

### Species occurrence and Identity.xlsx  

Tree species occurrence and identification data by location within Timor-Leste.

#### Species Occurrence

| Column Name      | Type    | Unit | Description                                   | Requirement |
|------------------|---------|------|-----------------------------------------------|-------------|
| Sr. No.          | Integer | –    | Serial number                                 | Required    |
| Scientific Name  | String  | –    | Scientific name of the tree                   | Required    |
| Common Name      | String  | –    | Common name of the tree                       | Optional    |
| Photographs link | String  | –    | Link to species photographs                   | Optional    |
| Distribution     | String  | –    | Native or non-native to Timor-Leste           | Optional    |
| Remarks          | String  | –    | Notes on species occurrence and observations  | Optional    |
| Baucau           | String  | –    | Species occurrence in Baucau                  | Optional    |
| Liquica          | String  | –    | Species occurrence in Liquiçá                 | Optional    |
| Covalima         | String  | –    | Species occurrence in Covalima                | Optional    |
| Baguia           | String  | –    | Species occurrence in Baguia                  | Optional    |
| Los Paolos       | String  | –    | Species occurrence in Lospalos                | Optional    |
| Viqueque         | String  | –    | Species occurrence in Viqueque                | Optional    |

#### Legend  

| Column Name     | Type    | Unit | Description             |
|-----------------|---------|------|-------------------------|
| Sr. no.         | Integer | –    | Serial number           |
| Topic           | String  | –    | Topic being interpreted |
| Colour Code     | String  | –    | Colour code used        |
| Interpretation  | String  | –    | Meaning of the colour   |

---

### Species Phenology Pending Verification.xlsx  

Tree species with flowering and fruiting periods pending verification.

#### Species list to Verify

| Column Name               | Type    | Unit | Description                     | Requirement |
|---------------------------|---------|------|---------------------------------|-------------|
| Sr. No.                   | Integer | –    | Serial number                   | Required    |
| Scientific Name           | String  | –    | Scientific name of the tree     | Required    |
| Common Name               | String  | –    | Common name of the tree         | Optional    |
| Location                  | String  | –    | Observation location            | Optional    |
| Remarks                   | String  | –    | Notes on verification           | Optional    |
| Flowering/Fruiting Period | String  | –    | Flowering and fruiting period   | Optional    |
| Reference                 | String  | –    | Information source              | Optional    |

#### Timor-Leste Climate

| Column Name | Type    | Unit | Description          |
|-------------|---------|------|----------------------|
| Sr. No.     | Integer | –    | Serial number        |
| Season      | String  | –    | Season type          |
| Month       | String  | –    | Months of the season |

---

## Agroforestry Data Datasets

### Agroforestry Crop.xlsx

Growth habit and shade tolerance for various crop types.

#### Legend

| Column Name      | Type    | Unit | Description             |
|------------------|---------|------|-------------------------|
| Sr. No.          | Integer | –    | Serial number           |
| Color Code       | String  | –    | Colour code used        |
| Interpretation   | String  | –    | Shade tolerance meaning |

#### Fruit Crops

| Column Name        | Type    | Unit | Description                        | Requirement |
|--------------------|---------|------|------------------------------------|-------------|
| Sr. No.            | Integer | –    | Serial number                      | Required    |
| Botanical Name     | String  | –    | Scientific name of the crop        | Required    |
| Common Name        | String  | –    | Common name of the crop            | Optional    |
| Habit              | String  | –    | Growth habit                       | Optional    |
| Agroforestry Layer | String  | –    | Agroforestry layer position        | Optional    |
| Shade Tolerance    | String  | –    | Shade requirement                  | Optional    |
| Reference          | String  | –    | Source of information              | Optional    |

#### Cash Crops

| Column Name     | Type    | Unit | Description                           | Requirement |
|-----------------|---------|------|---------------------------------------|-------------|
| Sr. No.         | Integer | –    | Serial number                         | Required    |
| Botanical Name  | String  | –    | Scientific name of the crop           | Required    |
| Common Name     | String  | –    | Common name of the crop               | Optional    |
| Habit           | String  | –    | Growth habit                          | Optional    |
| Shade Tolerance | String  | –    | Shade requirement                     | Optional    |
| Reference       | String  | –    | Source of information                 | Optional    |

#### Annual Crops

| Column Name     | Type    | Unit | Description                           | Requirement |
|-----------------|---------|------|---------------------------------------|-------------|
| Sr. No.         | Integer | –    | Serial number                         | Required    |
| Botanical Name  | String  | –    | Scientific name of the crop           | Required    |
| Common Name     | String  | –    | Common name of the crop               | Optional    |
| Habit           | String  | –    | Growth habit                          | Optional    |
| Shade Tolerance | String  | –    | Shade requirement                     | Optional    |
| Reference       | String  | –    | Source of information                 | Optional    |

---

### Agroforestry Database.xlsx

Tree species and crops that grow well together and a guide for intercropping them.

#### Agrofoestry suitablity

| Column Name                     | Type    | Unit  | Description                                           | Requirement |
|---------------------------------|---------|-------|-------------------------------------------------------|-------------|
| Sr. No.                         | Integer | –     | Serial number                                         | Required    |
| Species Name                    | String  | –     | Scientific name of the tree                           | Required    |
| Local Name                      | String  | –     | Local name used in Timor-Leste                        | Optional    |
| English Name                    | String  | –     | English common name                                   | Optional    |
| Intercropping with Annual Crops | String  | –     | Guidance on growing trees with annual food crops      | Optional    |
| Agroforestry Type               | String  | –     | Recommended planting system (e.g. block or boundary)  | Optional    |
| Allelopathic Effect             | String  | –     | Whether the tree suppresses nearby plant growth       | Optional    |
| Canopy Shade                    | String  | –     | Degree of light reduction caused by the canopy        | Optional    |
| Soil Dynamics                   | String  | –     | Effects on soil nutrients and fertility               | Optional    |
| Suitable Age for Intercropping  | String  | yr    | Tree age range suitable for intercropping             | Optional    |
| Annual Crops                    | String  | –     | Compatible annual food crops                          | Optional    |
| Fruit Trees                     | String  | –     | Compatible fruit tree species                         | Optional    |
| Cash Crops                      | String  | –     | Compatible cash crops (e.g. coffee or cocoa)          | Optional    |
| Reference                       | String  | –     | Source of the information                             | Optional    |

#### Reference

| Column Name    | Type    | Unit | Description               | Requirement |
|----------------|---------|------|---------------------------|-------------|
| Sr. No.        | Integer | –    | Serial number             | Required    |
| Citation       | String  | –    | Short citation            | Required    |
| Full Reference | String  | –    | Full reference details    | Optional    |

---

### Yield Reduction of Crop.xlsx

Crop yield losses caused by tree shade along with research evidence and long term estimates.

#### Sheet1

| Column Name                              | Type    | Unit | Description                                             | Requirement |
|------------------------------------------|---------|------|---------------------------------------------------------|-------------|
| Sr. No.                                  | Integer | –    | Serial number                                           | Required    |
| Botanical Name                           | String  | –    | Scientific name of the crop                             | Required    |
| Common Name                              | String  | –    | Common name of the crop                                 | Optional    |
| Habit                                    | String  | –    | Growth habit                                            | Optional    |
| Shade Tolerance                          | String  | –    | Crop response to shade                                  | Optional    |
| Evidence of Shade Effect                 | String  | –    | Research evidence describing yield response to shade    | Optional    |
| Approximate Yield Reduction by Year 40   | String  | –    | Estimated yield reduction under mature canopy           | Optional    |
| Reference                                | String  | –    | Source of the information                               | Optional    |

#### Sheet2

| Column Name                            | Type   | Unit | Description                                                | Requirement |
|----------------------------------------|--------|------|------------------------------------------------------------|-------------|
| Evidence of Shade Effect               | String | –    | Summary of observed yield response to shade                | Optional    |
| Approximate Yield Reduction by Year 40 | String | –    | Estimated long-term yield reduction under tree shade       | Optional    |

## GIS Datasets (Overview)

The following folders contain spatial soil datasets used for GIS-based environmental analysis in Timor-Leste. These datasets are provided as supporting spatial layers and are intended for use within GIS software (e.g. QGIS). They are not designed for direct tabular analysis outside a GIS environment.

Each folder groups together related shapefiles and their required supporting files ('.shp', '.dbf', '.prj', '.shx', etc), together with optional QGIS style files used only for map visualisation.

---

### TL_Soils_FNF_2010

This folder contains national-scale soil classification layers for Timor-Leste derived from the FAO/UNESCO Harmonized World Soil Database (HWSD).  

The datasets are commonly used to distinguish forest and non-forest soil classifications at a national scale.

---

### Soil type map – Seeds of Life

This folder contains detailed soil type maps produced under the *Seeds of Life* program.  

The datasets represent mapped soil units and soil types across Timor-Leste.

Both original layers and geometry-corrected versions are included to support spatial accuracy.

---

### Soil texture

This folder contains a spatial layer classifying soil texture across Timor-Leste, such as sandy, loamy, and clay-based soils.

---

### Soil pH

This folder contains a spatial layer showing soil pH ranges across Timor-Leste.

---

### Soil complexes

This folder contains spatial layers representing grouped or combined soil units, commonly referred to as soil complexes.

---

**Note:**  
All files within these folders are standard GIS components:

- '.shp' files store spatial geometry  
- '.dbf' files store attribute data  
- '.prj' / '.qpj' files define coordinate systems  
- '.shx', '.sbn', '.sbx' files support spatial indexing  

QGIS style files are optional and only affect how layers appear on a map.

## Other Datasets

### all_farm_sample.xlsx & all_farm_sample.csv

Environmental and soil data for each farm

#### all_farm_sample

| Column Name | Type    | Unit      | Description                                           | Requirement |
|-------------|---------|-----------|-------------------------------------------------------|-------------|
| farm_ID     | Integer | –         | Unique identifier for each farm record                | Required    |
| Name        | String  | –         | Farmer full name                                      | Required    |
| elevation   | Integer | m         | Elevation above sea level                             | Required    |
| temperature | Integer | °C        | Average annual temperature                            | Required    |
| rainfall    | Integer | mm        | Average annual rainfall                               | Required    |
| pH          | Float   | –         | Soil pH value                                         | Optional    |
| texture     | String  | –         | Soil texture classification                           | Optional    |
| area_ha     | Float   | ha        | Farm area                                             | Required    |

---

### Copy of List of Riparian and Coastal Species.xlsx 

Tree species suitable for riparian and coastal planting.

#### Riparian species

| Column Name      | Type    | Unit | Description                        | Requirement |
|------------------|---------|------|------------------------------------|-------------|
| Sr. No.          | Integer | –    | Serial number                      | Required    |
| Scientific Name  | String  | –    | Scientific name of the tree        | Required    |
| Common Name      | String  | –    | Common name of the tree            | Optional    |
| Remark           | String  | –    | Notes on where the tree grows      | Optional    |
| Reference        | String  | –    | Source of the information          | Optional    |

#### Coastal species

| Column Name      | Type    | Unit | Description                        | Requirement |
|------------------|---------|------|------------------------------------|-------------|
| Sr. No.          | Integer | –    | Serial number                      | Required    |
| Scientific Name  | String  | –    | Scientific name of the tree        | Required    |
| Common Name      | String  | –    | Common name of the tree            | Optional    |
| Remark           | String  | –    | Notes on where the tree grows      | Optional    |
| Reference        | String  | –    | Source of the information          | Optional    |

---

### Exclusion_criteria.xlsx

Tree species exclusion criteria and optimal environmental ranges.

#### Sheet1

| Column Name        | Type    | Unit | Description                                                         | Requirement |
|--------------------|---------|------|---------------------------------------------------------------------|-------------|
| Sr. No.            | Integer | –    | Serial number                                                       | Required    |
| Species            | String  | –    | Scientific name of the tree                                         | Required    |
| Exclusion Criteria | String  | –    | Environmental conditions under which the species should be excluded | Required    |
| Grow well in       | String  | –    | Environmental conditions suitable for the species                   | Optional    |

---

### Optimum Environmental Variables for species.xlsx

Tree species optimal environmental and soil ranges including factors that limit growth.

#### Sheet1

| Column Name                     | Type    | Unit            | Description                                      | Requirement |
|---------------------------------|---------|-----------------|--------------------------------------------------|-------------|
| Sr. No.                         | Integer | –               | Serial number                                    | Required    |
| Species Name                    | String  | –               | Scientific name of the tree                      | Required    |
| Common Name                     | String  | –               | Common name of the tree                          | Optional    |
| Remark                          | String  | –               | Growth related notes                             | Optional    |
| Limiting Factor                 | String  | –               | Environmental conditions limiting species growth | Optional    |
| Soil Type                       | String  | –               | Optimal soil types                               | Optional    |
| Rainfall                        | String  | mm              | Annual rainfall range optimal for growth         | Optional    |
| Temperature                     | String  | °C              | Optimal temperature range                        | Optional    |
| Soil pH                         | String  | pH              | Optimal soil pH range                            | Optional    |
| Altitude                        | String  | m               | Optimal elevation range                          | Optional    |

---

### Species dependencies.xlsx

Tree species that grow well together along with specific recommendations on which combinations to avoid.

#### Sheet1

| Column Name               | Type    | Unit | Description                               | Requirement |
|---------------------------|---------|------|-------------------------------------------|-------------|
| Sr. No.                   | Integer | –    | Serial number                             | Required    |
| Focal Species             | String  | –    | Scientific name of the tree               | Required    |
| Role                      | String  | –    | Role in the agroforestry system           | Required    |
| Good Tree Partners        | String  | –    | Species that grow well together           | Optional    |
| Avoid or Use with Caution | String  | –    | Species combinations to avoid or limit    | Optional    |
| Group Notes               | String  | –    | Planting recommendations                  | Optional    |

---

### Species Limiting Factor_.xlsx

Tree species growth limitations and site suitability.

#### Sheet1

| Column Name     | Type    | Unit | Description                                      | Requirement |
|-----------------|---------|------|--------------------------------------------------|-------------|
| Sr. No.         | Integer | –    | Serial number                                    | Required    |
| Species Name    | String  | –    | Scientific name of the tree                      | Required    |
| Common Name     | String  | –    | Common name of the tree                          | Optional    |
| Limiting Factor | String  | –    | Conditions where the species does not grow well  | Optional    |
| Remarks         | String  | –    | Notes on suitability and use                     | Optional    |
