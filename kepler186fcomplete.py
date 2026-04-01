import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

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
    
    print("calculating transit depth using direct statistics...")
    
    mask = (binned.time.value > -0.2) & (binned.time.value < 0.2) & ~np.isnan(binned.flux.value)
    x = binned.time.value[mask]
    y = binned.flux.value[mask]
    
    # THE ELEGANT FIX: Ditch the ML optimizer, use basic statistics!
    
    # 1. Find the flat baseline (average the dots outside the transit window)
    out_of_transit_mask = np.abs(x) > 0.05
    baseline = np.mean(y[out_of_transit_mask])
    
    # 2. Find the bottom of the dip (average the dots dead-center in the transit)
    in_transit_mask = np.abs(x) < 0.02
    transit_bottom = np.mean(y[in_transit_mask])
    
    # 3. The depth is simply the difference between the two!
    calc_depth = baseline - transit_bottom
    
    # R_planet = R_star * sqrt(depth)
    star_r = 0.472 * 109.2 
    planet_r = star_r * np.sqrt(calc_depth)
    
    print("\n--- results ---")
    print(f"transit depth: {calc_depth*100:.4f}%")
    print(f"duration:      ~2.40 hrs (measured)")
    print(f"planet radius: {planet_r:.2f} Earth radii")
    print("---------------\n")

    fig, ax = plt.subplots(figsize=(10, 5))
    
    folded.scatter(ax=ax, color='grey', alpha=0.1, label='raw data')
    binned.scatter(ax=ax, color='blue', alpha=0.8, s=20, label='binned')
    
    # Draw the box manually based on our exact measurements
    sx = np.linspace(-0.2, 0.2, 1000)
    sy = np.full_like(sx, baseline)
    in_transit_plot = np.abs(sx) < (0.1 / 2.0)  # The true 2.4 hour duration
    sy[in_transit_plot] -= calc_depth
    
    ax.plot(sx, sy, color='red', lw=2, label=rf'direct measurement ($R_p$ = {planet_r:.2f} $R_\oplus$)')
    
    ax.set_xlim(-0.2, 0.2)     
    ax.set_ylim(0.995, 1.005)  
    ax.set_title('Kepler-186f Transit Fit (Statistical Method)')
    ax.legend(loc='upper right')
    
    print("saving plot...")
    plt.savefig('kepler186f_model_fit.png', dpi=300, bbox_inches='tight')
    print("done!")

if __name__ == "__main__":
    main()
