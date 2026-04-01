import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# --- 1. DEFINE THE MATHEMATICAL MODEL ---
def box_transit_model(time, depth, duration, mid_transit_time):
    """A simple U-shaped box model for an exoplanet transit."""
    flux = np.ones_like(time)
    # Create a condition where the planet is in front of the star
    in_transit = np.abs(time - mid_transit_time) < (duration / 2.0)
    # Lower the brightness by the depth of the planet during that time
    flux[in_transit] = 1.0 - depth
    return flux

def main():
    print("Searching for Kepler-186 data...")
    search_result = lk.search_lightcurve('Kepler-186', author='Kepler')
    
    print(f"Downloading {len(search_result)} datasets... (Using cached files)")
    lc_collection = search_result.download_all()
    
    print("Cleaning and flattening data (Optimized)...")
    clean_lcs = []
    for lc in lc_collection:
        clean_lc = lc.remove_nans().remove_outliers().flatten(window_length=401)
        clean_lcs.append(clean_lc)
        
    print("Stitching the clean datasets together...")
    flat_lc = lk.LightCurveCollection(clean_lcs).stitch()
    
    # Kepler-186f Parameters
    planet_period = 129.944  
    transit_epoch = 172.15  
    
    print("Folding light curve...")
    folded_lc = flat_lc.fold(period=planet_period, epoch_time=transit_epoch)
    
    print("Binning data to highlight the tiny transit dip...")
    binned_lc = folded_lc.bin(time_bin_size=0.015) 
    
    # --- 2. CURVE FITTING WITH SCIPY ---
    print("Fitting mathematical Box Model to the data...")
    # Extract raw arrays from Lightkurve and remove any remaining blank spots
    valid_indices = ~np.isnan(binned_lc.flux.value)
    x_data = binned_lc.time.value[valid_indices]
    y_data = binned_lc.flux.value[valid_indices]
    
    # Initial guesses: [depth, duration, mid_transit_time]
    # We guess a duration of 0.1 days (~2.4 hours) and a mid-transit at 0.0
    initial_guesses = [0.0004, 0.1, 0.0]
    
    # Run the SciPy optimizer to find the perfect fit
    # Bounds keep the computer from guessing impossible physics
    popt, pcov = curve_fit(box_transit_model, x_data, y_data, 
                           p0=initial_guesses, 
                           bounds=([0, 0.01, -0.1], [0.01, 0.5, 0.1]))
                           
    # Extract the exact metrics found by the computer
    fitted_depth, fitted_duration, fitted_t0 = popt
    
    # --- 3. CALCULATE THE PLANETARY RADIUS ---
    # Kepler-186 star radius is ~0.472 times our Sun
    # 1 Solar Radius = 109.2 Earth Radii
    radius_star_earths = 0.472 * 109.2 
    
    # Physics Formula: Planet Radius = Star Radius * sqrt(Depth)
    radius_planet_earths = radius_star_earths * np.sqrt(fitted_depth)
    
    # Print the final detected parameters to the terminal
    print("\n" + "="*30)
    print(" PLANET DETECTION RESULTS")
    print("="*30)
    print(f"Mid-Transit Time:  {fitted_t0:+.5f} days from fold center")
    print(f"Transit Duration:  {fitted_duration * 24:.2f} hours")
    print(f"Transit Depth:     {fitted_depth * 100:.4f}% light blocked")
    print(f"Calculated Radius: {radius_planet_earths:.2f} Earth Radii")
    print("="*30 + "\n")

    # --- 4. PLOT THE RESULTS ---
    fig, ax = plt.subplots(figsize=(10, 5))
    
    folded_lc.scatter(ax=ax, color='grey', alpha=0.1, label='Unbinned Data')
    binned_lc.scatter(ax=ax, color='blue', alpha=0.8, s=20, label='Binned Data')
    
    # Plot the mathematical Box Model as a solid red line over the data
    smooth_x = np.linspace(-0.2, 0.2, 1000)
    smooth_y = box_transit_model(smooth_x, fitted_depth, fitted_duration, fitted_t0)
    ax.plot(smooth_x, smooth_y, color='red', linewidth=2, 
            label=f'Model Fit ($R_p$ = {radius_planet_earths:.2f} $R_\oplus$)')
    
    # Zoom in tightly on the transit
    ax.set_xlim(-0.2, 0.2)     
    ax.set_ylim(0.995, 1.005)  
    
    ax.set_title('Exoplanet Transit Model: Kepler-186f')
    ax.legend()
    
    print("Saving final plot with mathematical model...")
    plt.savefig('kepler186f_model_fit.png', dpi=300, bbox_inches='tight')
    print("Done! Look for 'kepler186f_model_fit.png' in your project folder.")

if __name__ == "__main__":
    main()
