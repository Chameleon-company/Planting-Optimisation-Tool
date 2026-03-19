# Suitability Scoring Requirements
The suitability scoring module needs takes an input farm profile and a list of candidate trees. It then calculates a suitability score for each candidate tree along with an explanation for the score. This information is returned from the function. The features in the inputs for both the farm and tree are likely to change in future versions, therefore the code needs to be designed to be flexible to different input features. 

# Inputs
The farm and species profiles share common features that have been classified as bioclimate, soil, topographic, ecological functions, agroforestry use. 

## Current inputs

**Tree profile**:
*  bioclimate
    *  rainfall minimum - numerical
    *  rainfall maximum - numerical
    *  temperature minimum - numerical
    *  temperature maximum - numerical

*  soil
    *  pH minimum - numerical
    *  pH maximum - numerical
    *  texture classes - categorical, possibly multiple values from (sand, loamy sand, sandy loam, loam, silt loam, silt, sandy clay loam, clay loam, silty clay loam, sandy clay, silty clay, clay) [USDA](https://www.nrcs.usda.gov/sites/default/files/2022-11/Texture%20and%20Structure%20-%20Soil%20Health%20Guide_0.pdf)

* topographic
    *  elevation minimum - numerical
    *  elevation maximum - numerical

* ecological functions - **None**

* agroforestry use - **None**

**Farm profile**:
*  bioclimate
    *  rainfall - numerical
    *  temperature - numerical
*  soil
    *  pH - numerical
    *  texture - categorical, single value
*  topographic
    *  elevation - numerical

* ecological functions - **None**

* agroforestry use - **None**

## Planned inputs
These are the inputs in addition to the current inputs.

*  topographic
    *  costal - categorical (yes/no)
    *  riparian - categorical (yes/no)

*  ecological functions
    *  soil improving
        *  Nitrogen-fixing - categorical (yes/no)
    *  stress tolerance
        *  Shade tolerant - categorical (yes/no)
    *  erosion control
        * bank stabilising - categorical (yes/no)

*  agroforestry type - categorical (block, boundary, intercropping, mosaic), list of multiple categories

## Future inputs
These are beyond the scope of the project due to insufficient data.

*  bioclimate
    * Minimum and maximum temperature for farm rather than the average
* soil
    *  drainage class - categorical (well drained, moderately well drained, poorly drained)
    *  depth class - categorical (shallow, moderate, deep).
    *  Fertility - categorical (low, medium, high)
    *  tolerances - flags: salinity tolerant, sodicity tolerant, rockiness/stoniness tolerant.
    *  parent material - e.g., limestone, volcanic, red soil/loam, black soil.

*  agroforestry type
    * intercropping duration

# Outputs
For each of the candidate tree species:
* Suitability score - number
* Explanation for score - text

# Approach
The first implementation will use a Multiple-Criteria-Decision-Analysis approach as per the PO current prototype.