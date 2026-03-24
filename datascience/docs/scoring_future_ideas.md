# Future Work

The following improvements are proposed to expand the scoring library, improve the accuracy of MCDA weighting, and make the system more accessible for both technical and non‑technical users.

### **1. Develop an Analytic Hierarchy Process (AHP) tool for weight calculation**

Create an interactive AHP tool that domain experts can use to perform pairwise comparisons of features.  
This will allow:

*   Transparent, expert‑driven weight generation
*   More defensible MCDA scoring
*   Automated conversion of pairwise comparisons → normalized feature weights

This tool could be command‑line based, notebook-based, or part of a future UI.


### **2. Use TreeO2 Data + Machine Learning to infer MCDA weights**

Explore whether observed species performance in TreeO2 can be used to *learn* suitable feature weights using:

*   Tree-based models (feature importance)
*   SHAP values
*   Logistic/linear models for interpretable weighting

This would provide:

*   Data‑driven complement to expert‑derived weights
*   Ability to compare ML‑derived weights vs. expert weights
*   Potential hybrid weighting schemes


### **3. Add an API endpoint to Add/Modify species parameters**

Implement an API endpoint that allows:

*   Updating parameter sets (weights, scoring methods, tolerances)
*   Uploading CSV/YAML parameter files via the endpoint

Benefits:

*   Enables integration with user-facing tools (web UI, apps)
*   Makes the scoring library usable as a live service

### **4. Refactor code to use SQLAlchemy ORM objects**

The currently implementation takes lists of dictionaries as inputs. In the API, this
requires conversion of SQLAlchemy ORM objects into the required input format. Refactoring
the suitability scoring to accept these objects directly would lead to the following benefits.  

Benefits:

*   Performance improvements
*   Cleaner API code

### **4. Add validation utilities for species parameter inputs**

Before scoring, validate:

*   Missing weights
*   Invalid scoring methods
*   Inconsistent min/max ranges
*   Missing categorical preferences

This avoids silent errors and improves reliability.


### **5. Introduce versioning for rules and parameters**

Add simple version tags to:

*   Species parameters
*   Compatibility matrices
*   Rule sets
*   Scoring configurations

This ensures:

*   Reproducible scoring runs
*   Traceability in research and deployments


### **6. Create a "Compatibility Matrix Editor" tool**

A small module or UI to:

*   Edit categorical compatibility tables
*   Auto-check symmetry
*   Suggest default values
*   Export validated YAML

This makes life easier for domain experts working with categorical scoring.
