# Modelling-exoplanet-transits
Simulating and modelling exoplanet transits using kepler data
# Exoplanet Transit Modelling using Kepler Data 
(We are using data for kepler 186f as this was the first interesting exoplanet i learned about and in 4th grade me and my friends thought to design a spaceship to go there.. huh, kids, I will come to regret choosing this planet as we shall see further) We are using kepler 1b for code validation.

## Overview
This project analyzes real photometric data from NASA's Kepler mission to model exoplanet transit signals and estimate planetary parameters. (First we detect the star, then we use SciPy to make a box model and find transit depth, radius and duration of transit(generally taken as given to fix other parameters in our code))
Best to start from kepler1b.py and kepler186fdetection modules as I have given the logical flow.

## Objective
To detect and model the dip in stellar brightness caused by an exoplanet passing in front of its host star, and extract key parameters such as transit depth, planetary radius and duration of transit.

## Methodology
* **Data Acquisition:** Downloaded Kepler light curve data using 'Lightkurve'.
* **Preprocessing:** Removed noise and long-term trends (flattening the light curve).
* **Modeling:** Implemented a transit model.
* **Parameter Estimation:** Used nonlinear curve fitting ('SciPy') to estimate parameters.

## Results
* Successfully detected the transit signal.
* Estimated key parameters:
  * Transit depth - Radius of Planet
  * The mid transit distance, epoch. (forced to do this or the code failed)
  * Transit duration
  * Images 1 and 2 show the graph and calculated values for kepler 1b, this is the proper validation for our process,Image 6 shows a graph of the same system when we used the same code as that for kepler 186f and the planet itself was taken as outlying values and the ML program tries to find data not there. Can be run by using kepler1b.py.
  * Images 3, 4 and 5 show our initial kepler 186f we can barely see a proper dip and the estimated values are way off as our math and anlysis techniques are not good enough to detect such a faint planet, with large ~160 days, ie only 11 data points in the 4 years kepler probe collected data, not enough to cancel noise. Can be run by using kepler186f.py's
  <img width="2621" height="1407" alt="kepler1b_model_fit" src="https://github.com/user-attachments/assets/e2dab4a7-f78d-49b7-8e6b-2db8bbc1ab24" />
  <img width="489" height="319" alt="image" src="https://github.com/user-attachments/assets/fa52364c-515f-48ed-b1ef-c1bfdf4ffc9e" />
  <img width="2625" height="1407" alt="kepler186f_transit" src="https://github.com/user-attachments/assets/2e00d424-59ea-4c0c-b6e2-309d061bbb90" />
  <img width="2638" height="1407" alt="kepler186f_transit_zoomed" src="https://github.com/user-attachments/assets/58ad019c-600a-460f-9e2c-bc48b7fc447d" />
  <img width="491" height="163" alt="image" src="https://github.com/user-attachments/assets/7cc197ae-5d68-4a8d-92ca-3876756957b8" />
  <img width="2368" height="1262" alt="image" src="https://github.com/user-attachments/assets/6cf597d7-c707-4c08-9481-8dc9c4fc243e" />

## Tools Used
* **Language:** Python
* **Libraries:** NumPy, SciPy, Matplotlib, Lightkurve.

## Future Improvements
* Include limb darkening models for higher accuracy.
* Use Markov Chain Monte Carlo (MCMC) for robust parameter estimation.
* Analyze multi-planet systems.

## The Journey (and The Roadblocks)

Building this project taught me one major lesson: real astronomical data is incredibly messy. What I thought would be a straightforward modelling problem turned into long debugging monolouge even with the help of ai tools. Here is a look at the roadblocks I hit and how I eventually solved them:

1. The "Data has no feelings" Reality Check (Signal-to-Noise)
I originally wanted to detect Kepler-186f, an Earth-sized planet and based on my personal childhood bias. The problem? An Earth-sized transit only blocks about 0.04% of its star's light.
When I fed this data into SciPy’s optimizer, the algorithm went crazy. The tiny dip was so buried in natural telescope static that the math optimizer kept finding "zero-slopes," crashing into negative numbers, and throwing NaN errors.
The Pivot: I realized I was trying to run a marathon before learning to walk. I pivoted my target to Kepler-1b —a massive "Hot Jupiter" that blocks 1.5% of its star's light. This allowed me to actually validate that my core architecture worked before trying to find microscopic signals.

2. I Accidentally made my Planet disappear.
Once I switched to the giant Hot Jupiter, I ran my code and... the graph was a perfectly flat line. The planet was completely gone.
After a long tug of war changing and tweaking the code, I realized the culprit was my cleaning algorithm. I was using standard Lightkurve filters like .remove_outliers() and .flatten(). Because Kepler-1b is so huge, the algorithm looked at the massive 1.5% drop in light and thought, "Wow, that’s a massive glitch! Let me delete that so I don't ruin the graph."
The Fix: My code literally detected the planet and yeeted it out of existence. I had to bypass the automated outlier filters and trust NASA's raw telemetry (hope there were no truly crazy outliers) so the planet could actually survive the pipeline.

4. Looking in the Wrong Place (Coordinate Drift)
Even with the planet saved, my SciPy algorithm was hallucinating. It was drawing shallow, random boxes on the far edges of my graph.
It turned out my math was flawless, but my "Epoch" (the starting timestamp) was wrong due to how different NASA catalogs calculate time (BJD vs. BKJD etc... out of my field). I was zoomed in on exactly Phase 0.0, but the planet was actually transiting off-screen at Phase +0.90.
The Fix: Instead of blindly guessing NASA's exact timestamps, I rewrote the code to be dynamic. I used NumPy to scan the entire folded timeline, hunt down the absolute deepest point of the curve, and automatically snap the camera and the math directly onto the planet. 

 The Big Takeaway
This project completely changed how I view data science. You cannot just plug .remove_outliers() or scipy.optimize into a script and expect magic. If you don't understand the physical reality of the data you are looking at, your cleaning tools will literally delete the discoveries you are trying to make, and your machine learning models will confidently give you answers based on empty static.
I was humbled as I believed doing a modelling course had already given me all the required skills and despite the help of the internet and AI tools it took a long time to completely be finished.

Thank you, hoping to do much better simulations in the future, cheers!

## How to Run
On bash, we used git gui 
1. Clone the repository: git clone https://github.com/N-Sai-Prabhanjan/Modelling-exoplanet-transits.git
2. Install the required dependencies: pip install -r requirements.txt
3. Run the main script you want, ex: python kepler1b.py
