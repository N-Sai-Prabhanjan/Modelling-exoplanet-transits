import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

def box_model(t, depth, duration, t0):
    # basic u-shape array to simulate the transit dip
    flux = np.ones_like(t)
    in_transit = np.abs(t - t0) < (duration / 2.0)
    flux[in_transit] = 1.0 - depth
    return flux

def main():
    print("fetching kepler-186 data...")
    res = lk.search_lightcurve('Kepler-186', author='Kepler')
    lcs = res.download_all()
    
    print("cleaning and flattening (this takes a sec)...")
    clean_list = []
    for lc in lcs:
        # scrub nans, outliers, and flatten the wiggles
        clean = lc.remove_nans().remove_outliers().flatten(window_length=401)
        clean_list.append(clean)
        
    print("stitching it all together...")
    stitched = lk.LightCurveCollection(clean_list).stitch()
    
    # kepler 186f parameters
    p = 129.944  
    epoch = 172.15  # tweaked this offset to center the dip perfectly at 0
    
    folded = stitched.fold(period=p, epoch_time=epoch)
    
    # bin down the noise. 0.015 days is about 21 minutes
    binned = folded.bin(time_bin_size=0.015) 
    
    print("running scipy curve fit...")
    
    # zooming the math in on the actual transit window so scipy doesn't freak out
    mask = (binned.time.value > -0.2) & (binned.time.value < 0.2) & ~np.isnan(binned.flux.value)
    
    x = binned.time.value[mask]
    y = binned.flux.value[mask]
    
    # initial guesses: depth, duration, center time
    guess = [0.0004, 0.1, 0.0]
    
    # put bounds on it so the algorithm doesn't give us physically impossible answers
    popt, _ = curve_fit(box_model, x, y, p0=guess, bounds=([0, 0.01, -0.1], [0.01, 0.5, 0.1]))
    calc_depth, calc_dur, calc_t0 = popt
    
    # R_planet = R_star * sqrt(depth)
    # kepler 186 radius is 0.472 solar radii. (1 solar radius = 109.2 earth radii)
    star_r = 0.472 * 109.2 
    planet_r = star_r * np.sqrt(calc_depth)
    
    print("\n--- results ---")
    print(f"transit depth: {calc_depth*100:.4f}%")
    print(f"duration:      {calc_dur * 24:.2f} hrs")
    print(f"planet radius: {planet_r:.2f} Earth radii")
    print("---------------\n")

    # set up the plot
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # plot the raw and binned data
    folded.scatter(ax=ax, color='grey', alpha=0.1, label='raw data')
    binned.scatter(ax=ax, color='blue', alpha=0.8, s=20, label='binned')
    
    # draw the red model line
    sx = np.linspace(-0.2, 0.2, 1000)
    sy = box_model(sx, calc_depth, calc_dur, calc_t0)
    ax.plot(sx, sy, color='red', lw=2, label=rf'model fit ($R_p$ = {planet_r:.2f} $R_\oplus$)')
    
    # zoom camera
    ax.set_xlim(-0.2, 0.2)     
    ax.set_ylim(0.995, 1.005)  
    
    ax.set_title('Kepler-186f Transit Fit')
    ax.legend(loc='upper right') 
    
    # plt.show() # usually freezes up my machine, saving it instead
    
    print("saving plot...")
    plt.savefig('kepler186f_model_fit.png', dpi=300, bbox_inches='tight')
    print("done!")

if __name__ == "__main__":
    main()
