# Modelling-exoplanet-transits
Simulating and modelling exoplanet transits using kepler data
# Exoplanet Transit Modelling using Kepler Data 
(We are using data for kepler 186f as this was the first interesting exoplanet i learned about and in 4th grade me and my friends thought to design a spaceship to go there.. huh, kids, I will come to regret choosing this planet as we shall see further) We are using kepler 1b for code validation.

## Overview
This project analyzes real photometric data from NASA's Kepler mission to model exoplanet transit signals and estimate planetary parameters. (First we detect the star, then we use SciPy to make a box model and find transit depth, radius and duration of transit)

## Objective
To detect and model the dip in stellar brightness caused by an exoplanet passing in front of its host star, and extract key parameters such as transit depth and duration.

## Methodology
* **Data Acquisition:** Downloaded Kepler light curve data using `Lightkurve`.
* **Preprocessing:** Removed noise and long-term trends (flattening the light curve).
* **Modeling:** Implemented a transit model.
* **Parameter Estimation:** Used nonlinear curve fitting (`SciPy`) to estimate parameters.

## Results
* Successfully detected the transit signal.
* Estimated key parameters:
  * Transit depth - Radius of Planet
  * Transit duration
  * Mid-transit time


## Tools Used
* **Language:** Python
* **Libraries:** `NumPy`, `SciPy`, `Matplotlib`, `Lightkurve`

## Future Improvements
* Include limb darkening models for higher accuracy.
* Use Markov Chain Monte Carlo (MCMC) for robust parameter estimation.
* Analyze multi-planet systems.

---
## How to Run
1. Clone the repository: `git clone https://github.com/N-Sai-Prabhanjan/Modelling-exoplanet-transits.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the main script: `python main.py`
