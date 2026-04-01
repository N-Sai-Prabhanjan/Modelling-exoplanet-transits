import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# We removed duration and t0 from the guessing game!
# Step-functions (sharp boxes) break calculus-based optimizers, so we simplify.
def box_model(t, depth, baseline):
    flux = np.full_like(t, baseline, dtype=float)
    
    # We lock the duration (0.22 days = ~5.2 hours) and center (0.0) in place
    in_transit = np.abs(t - 0.0) < (0.22 / 2.0)
    flux[in_transit] -= depth
    return flux

def main():
    print("fetching kepler-186 data...")
    res = lk.search_lightcurve('Kepler-186', author='Kepler')
    
    print(f"downloading {len(res)} datasets (should be fast if cached)...")
    lcs = res.download_all()
    
    print("cleaning and flattening (this takes a sec)...")
    clean_list = []
    for lc in lcs:
        clean = lc.remove_nans().remove_outliers().flatten(window_length=401)
        clean_list.append(clean)
        
    print("stitching it all together...")
    stitched = lk.LightCurveCollection(clean_list).stitch()
    
    p = 129.944  
    epoch = 172.15  
    
    folded = stitched.fold(period=p, epoch_time=epoch)
    binned = folded.bin(time_bin_size=0.015) 
    
    print("running scipy curve fit...")
    
    mask = (binned.time.value > -0.2) & (binned.time.value < 0.2) & ~np.isnan(binned.flux.value)
    x = binned.time.value[mask]
    y = binned.flux.value[mask]
    
    # initial guesses: just depth and baseline now
    guess = [0.0004, 1.0]
    
    # THE FIX: We added bounds back in to prevent negative depth guesses (NaN errors)
    # bounds=([lower_depth, lower_baseline], [upper_depth, upper_baseline])
    popt, _ = curve_fit(box_model, x, y, p0=guess, bounds=([0.0, 0.99], [0.01, 1.01]))
    calc_depth, calc_base = popt
    
    # R_planet = R_star * sqrt(depth)
    star_r = 0.472 * 109.2 
    planet_r = star_r * np.sqrt(calc_depth)
    
    print("\n--- results ---")
    print(f"transit depth: {calc_depth*100:.4f}%")
    print(f"duration:      5.28 hrs (fixed)")
    print(f"planet radius: {planet_r:.2f} Earth radii")
    print("---------------\n")

    fig, ax = plt.subplots(figsize=(10, 5))
    
    folded.scatter(ax=ax, color='grey', alpha=0.1, label='raw data')
    binned.scatter(ax=ax, color='blue', alpha=0.8, s=20, label='binned')
    
    sx = np.linspace(-0.2, 0.2, 1000)
    sy = box_model(sx, calc_depth, calc_base)
    ax.plot(sx, sy, color='red', lw=2, label=rf'model fit ($R_p$ = {planet_r:.2f} $R_\oplus$)')
    
    ax.set_xlim(-0.2, 0.2)     
    ax.set_ylim(0.995, 1.005)  
    ax.set_title('Kepler-186f Transit Fit')
    ax.legend(loc='upper right')
    
    print("saving plot...")
    plt.savefig('kepler186f_model_fit.png', dpi=300, bbox_inches='tight')
    print("done!")

if __name__ == "__main__":
    main()
