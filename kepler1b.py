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
    
    print("stitching data (Skipping the flatten step to save the planet!)...")
    clean_list = []
    for lc in lcs:
        # THE FIX: We removed .flatten(). We are just removing NaNs and trusting NASA's raw data.
        clean = lc.remove_nans()
        clean_list.append(clean)
        
    stitched = lk.LightCurveCollection(clean_list).stitch()
    
    # Kepler-1b exact NASA parameters
    p = 2.470613  
    epoch = 120.9933  
    
    folded = stitched.fold(period=p, epoch_time=epoch)
    binned = folded.bin(time_bin_size=0.005) 
    
    print("running scipy curve fit...")
    
    mask = (binned.time.value > -0.1) & (binned.time.value < 0.1) & ~np.isnan(binned.flux.value)
    x = binned.time.value[mask]
    y = binned.flux.value[mask]
    
    guess = [0.015, 0.0, 1.0]
    popt, _ = curve_fit(box_model, x, y, p0=guess, bounds=([0.005, -0.05, 0.99], [0.05, 0.05, 1.01]))
    calc_depth, calc_t0, calc_base = popt
    
    star_r = 1.0 * 109.2 
    planet_r = star_r * np.sqrt(calc_depth)
    
    print("\n" + "="*30)
    print("🪐 PLANET DETECTION RESULTS")
    print("="*30)
    print(f"transit depth: {calc_depth*100:.2f}%")
    print(f"center offset: {calc_t0:+.4f} days")
    print(f"duration:      1.80 hrs (fixed)")
    print(f"planet radius: {planet_r:.2f} Earth radii")
    print(f"planet radius: {planet_r / 11.2:.2f} Jupiter radii")
    print("="*30 + "\n")

    fig, ax = plt.subplots(figsize=(10, 5))
    
    folded.scatter(ax=ax, color='grey', alpha=0.1, label='raw data')
    binned.scatter(ax=ax, color='blue', alpha=0.8, s=20, label='binned')
    
    sx = np.linspace(-0.1, 0.1, 1000)
    sy = box_model(sx, calc_depth, calc_t0, calc_base)
    ax.plot(sx, sy, color='red', lw=2, label=rf'scipy fit ($R_p$ = {planet_r:.2f} $R_\oplus$)')
    
    ax.set_xlim(-0.1, 0.1)     
    ax.set_ylim(0.97, 1.01)  
    
    ax.set_title('Kepler-1b (TrES-2b) Hot Jupiter Transit')
    ax.legend(loc='lower right') 
    
    print("saving plot...")
    plt.savefig('kepler1b_model_fit.png', dpi=300, bbox_inches='tight')
    print("done! Look for 'kepler1b_model_fit.png'.")

if __name__ == "__main__":
    main()
