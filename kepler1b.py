import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# We brought the 't0' (center offset) variable back! SciPy can easily find it now.
def box_model(t, depth, t0, baseline):
    flux = np.full_like(t, baseline, dtype=float)
    
    # Kepler-1b's transit is about 1.8 hours wide (0.075 days)
    in_transit = np.abs(t - t0) < (0.075 / 2.0)
    flux[in_transit] -= depth
    return flux

def main():
    print("fetching kepler-1 data (TrES-2b Hot Jupiter)...")
    res = lk.search_lightcurve('Kepler-1', author='Kepler')
    
    print(f"downloading {len(res)} datasets...")
    lcs = res.download_all()
    
    print("cleaning and flattening...")
    clean_list = []
    for lc in lcs:
        clean = lc.remove_nans().remove_outliers().flatten(window_length=401)
        clean_list.append(clean)
        
    print("stitching it all together...")
    stitched = lk.LightCurveCollection(clean_list).stitch()
    
    # Kepler-1b parameters
    p = 2.4706  
    epoch = 120.53  # Approximate first transit
    
    folded = stitched.fold(period=p, epoch_time=epoch)
    
    # Shorter period means we need smaller, higher-resolution bins!
    binned = folded.bin(time_bin_size=0.005) 
    
    print("running scipy curve fit...")
    
    # Zooming the math window to +/- 0.1 days
    mask = (binned.time.value > -0.1) & (binned.time.value < 0.1) & ~np.isnan(binned.flux.value)
    x = binned.time.value[mask]
    y = binned.flux.value[mask]
    
    # Initial guesses: depth (1.5%), center (0.0), baseline (1.0)
    guess = [0.015, 0.0, 1.0]
    
    # Bounds: Let SciPy shift the center left or right to find the perfect fit
    popt, _ = curve_fit(box_model, x, y, p0=guess, bounds=([0.005, -0.05, 0.99], [0.05, 0.05, 1.01]))
    calc_depth, calc_t0, calc_base = popt
    
    # R_planet = R_star * sqrt(depth)
    # The host star (Kepler-1) is almost exactly the same size as our Sun!
    star_r = 1.0 * 109.2 
    planet_r = star_r * np.sqrt(calc_depth)
    
    print("\n--- results ---")
    print(f"transit depth: {calc_depth*100:.2f}%")
    print(f"center offset: {calc_t0:+.4f} days")
    print(f"duration:      1.80 hrs (fixed)")
    print(f"planet radius: {planet_r:.2f} Earth radii")
    print(f"planet radius: {planet_r / 11.2:.2f} Jupiter radii") # 1 Jupiter = 11.2 Earths
    print("---------------\n")

    fig, ax = plt.subplots(figsize=(10, 5))
    
    folded.scatter(ax=ax, color='grey', alpha=0.1, label='raw data')
    binned.scatter(ax=ax, color='blue', alpha=0.8, s=20, label='binned')
    
    sx = np.linspace(-0.1, 0.1, 1000)
    sy = box_model(sx, calc_depth, calc_t0, calc_base)
    ax.plot(sx, sy, color='red', lw=2, label=rf'scipy fit ($R_p$ = {planet_r:.2f} $R_\oplus$)')
    
    ax.set_xlim(-1.2, 1.2)     
    # We HAVE to change the Y-axis bounds, or the 1.5% dip will go off the screen!
    ax.set_ylim(0.97, 1.01)  
    ax.set_title('Kepler-1b (TrES-2b) Hot Jupiter Transit')
    
    # Moved the legend to the lower right so it doesn't cover the massive dip
    ax.legend(loc='lower right') 
    
    print("saving plot...")
    plt.savefig('kepler1b_model_fit.png', dpi=300, bbox_inches='tight')
    print("done!")

if __name__ == "__main__":
    main()
