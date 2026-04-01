import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

def box_model(t, depth, t0, baseline):
    """A simple U-shaped box model for an exoplanet transit."""
    flux = np.full_like(t, baseline, dtype=float)
    in_transit = np.abs(t - t0) < (0.075 / 2.0)
    flux[in_transit] -= depth
    return flux

def main():
    print("fetching kepler-1 data (TrES-2b Hot Jupiter)...")
    res = lk.search_lightcurve('Kepler-1', author='Kepler')
    
    print(f"downloading {len(res)} datasets...")
    lcs = res.download_all()
    
    print("cleaning and flattening (outlier filter disabled!)...")
    clean_list = []
    for lc in lcs:
        # We flatten so the baseline stays at 1.0, but do not remove_outliers as we had done for kepler 186f as the dip ~1.5% will be counted as an outlier where it is our planet itself and we will elminate our planet as an outlier ( I did this and was struck for an hour)
        clean = lc.remove_nans().flatten(window_length=401)
        clean_list.append(clean)
        
    stitched = lk.LightCurveCollection(clean_list).stitch()
    
    p = 2.470613  
    # We are not able to set epoch well and get the desired results so we let the code handle this for us.
    folded = stitched.fold(period=p)
    binned = folded.bin(time_bin_size=0.005) 
    
    print("Locating the planet in the folded timeline...")
    
    valid_indices = ~np.isnan(binned.flux.value)
    binned_times = binned.time.value[valid_indices]
    binned_fluxes = binned.flux.value[valid_indices]
    
    # Find the absolute deepest dip in the entire orbit and make this the centre point forour graph.
    deepest_index = np.argmin(binned_fluxes)
    detected_t0 = binned_times[deepest_index]
    
    print(f"-> Planet found hiding at phase offset: {detected_t0:+.4f} days!")
    
    print("running scipy curve fit around the detected planet...")
    
    #zoom the math mask to wherever the planet actually is so we get clear data.
    mask = (binned_times > detected_t0 - 0.1) & (binned_times < detected_t0 + 0.1)
    x = binned_times[mask]
    y = binned_fluxes[mask]
    
    # Initial guesses using the dynamically detected center
    guess = [0.015, detected_t0, 1.0]
    
    # Now we finally let SciPy lock in on the exact bottom
    popt, _ = curve_fit(box_model, x, y, p0=guess, bounds=([0.005, detected_t0 - 0.05, 0.99], [0.05, detected_t0 + 0.05, 1.01]))
    calc_depth, calc_t0, calc_base = popt
    
    star_r = 1.0 * 109.2 
    planet_r = star_r * np.sqrt(calc_depth)
    
    print("\n" + "="*30)
    print("PLANET DETECTION RESULTS")
    print("="*30)
    print(f"transit depth: {calc_depth*100:.2f}%")
    print(f"center offset: {calc_t0:+.4f} days")
    print(f"duration:      1.80 hrs (fixed)")
    print(f"planet radius: {planet_r:.2f} Earth radii")
    print(f"planet radius: {planet_r / 11.2:.2f} Jupiter radii")
    print("="*30 + "\n")

    # PLOTTING THE RESULTS
    fig, ax = plt.subplots(figsize=(10, 5))
    
    folded.scatter(ax=ax, color='grey', alpha=0.1, label='raw data')
    binned.scatter(ax=ax, color='blue', alpha=0.8, s=20, label='binned')
    
    # Draw the red model line across our dynamic window
    sx = np.linspace(calc_t0 - 0.15, calc_t0 + 0.15, 1000)
    sy = box_model(sx, calc_depth, calc_t0, calc_base)
    ax.plot(sx, sy, color='red', lw=2, label=rf'scipy fit ($R_p$ = {planet_r:.2f} $R_\oplus$)')
    
    # Dynamically center the camera on the planet using our determined deepest dip as the centre.
    ax.set_xlim(calc_t0 - 0.15, calc_t0 + 0.15)     
    ax.set_ylim(0.97, 1.01)  
    
    ax.set_title('Kepler-1b (TrES-2b) Hot Jupiter Transit')
    ax.legend(loc='lower right') 
    
    print("saving plot...")
    plt.savefig('kepler1b_model_fit.png', dpi=300, bbox_inches='tight')
    print("done!")

if __name__ == "__main__":
    main()
#thank you, after a lot of errors and struggles we finally get a perfect planetary detection result, they can be found in READ ME or can be run on your own.
