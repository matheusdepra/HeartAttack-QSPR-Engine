# Future Improvements & Refinements

This document outlines potential technical and methodological improvements for the heart attack drug QSPR pipeline, based on the comparative analysis against the Rasheed et al. (2023) paper.

## 1. Statistical Normalization
### Log-Transformation for Vapor Pressure (VP)
- **Problem**: Vapor Pressure values for these drugs span over 20 orders of magnitude (from $10^{-2}$ to $10^{-22}$ mmHg). Linear regression on raw values is statistically dominated by the highest values (outliers), making the correlation coefficient ($r$) misleadingly low.
- **Improvement**: Implement $log_{10}(VP)$ normalization before running the QSPR regression. This is the scientific standard for properties with high dynamic ranges and will likely yield $r > 0.90$ consistent with literature.

## 2. Data Quality & Unit Consistency
### Temperature Unit Validation (Flash Point)
- **Problem**: Significant discrepancies were found (e.g., Aspirin FP at 482°C in PubChem vs 131.2°C in the article). Investigation suggests some PubChem values might specify °F instead of °C, or refer to decomposition points.
- **Improvement**: Implement a unit-check heuristic in the scraper to detect and convert °F to °C and flag values that exceed the Boiling Point (BP), as Flash Point must mathematically be lower than Boiling Point.

### Outlier Detection (Cook's Distance)
- **Problem**: Single drugs with problematic experimental data (like Aspirin's FP) can destroy otherwise strong correlations.
- **Improvement**: Integrate Cook's Distance or RANSAC (Random Sample Consensus) in the `src/calculators/qspr.py` module to automatically detect and flag influential outliers for manual review.

## 3. Methodological Alignment
### Handling "0.0" vs "Tiny" Values
- **Problem**: Literature often treats very low Vapor Pressures as literal 0.0, while our pipeline uses precise scientific notation. This "precision mismatch" affects the $r$ calculation.
- **Improvement**: Add an optional "Literature Emulation Mode" that applies a floor (e.g., values $< 1.0e-10$ are treated as $0.0$) to compare results more fairly with legacy publications.

## 4. Feature Engineering
### Hydrogen-Bonding Descriptors
- **Problem**: Degree-based indices (Randic, Zagreb) focus solely on molecular "skeleton" connectivity.
- **Improvement**: Incorporate H-Bond Donor/Acceptor counts and Polar Surface Area (PSA) as additional features in a multi-variate regression model, as these are critical for properties like Surface Tension and Vapor Pressure.

## 5. Automated Pipeline Enhancements
### Cross-Source Verification
- **Improvement**: Cross-reference PubChem data with other databases like **DrugBank** or **ChemSpider** to create a weighted "consensus" value for physicochemical properties when experimental data is conflicting.
