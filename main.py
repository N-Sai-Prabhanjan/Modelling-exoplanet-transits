import lightkurve as lk
import matplotlib.pyplot as plt

def main():
    print("Searching for Kepler-186 data...")
    search_result = lk.search_lightcurve('Kepler-186', author='Kepler')
    
    print(f"Downloading {len(search_result)} datasets... (Using cached files)")
    lc_collection = search_result.download_all()
    
    print("Cleaning and flattening data (Optimized)...")
    clean_lcs = []
    for lc in lc_collection:
        # Removing outliers deletes cosmic ray glitches
        # Flattening each quarter individually keeps the computer from freezing
        clean_lc = lc.remove_nans().remove_outliers().flatten(window_length=401)
        clean_lcs.append(clean_lc)
        
    print("Stitching the clean datasets together...")
    flat_lc = lk.LightCurveCollection(clean_lcs).stitch()
    
    # Kepler-186f Parameters
    planet_period = 129.944  
    transit_epoch = 172.15  # Perfectly centers the transit dip at X=0
    
    print("Folding light curve...")
    folded_lc = flat_lc.fold(period=planet_period, epoch_time=transit_epoch)
    
    print("Binning data to highlight the tiny transit dip...")
    # 0.015 day bin size (~21 minutes) provides great resolution for a 2.4-hour transit
    binned_lc = folded_lc.bin(time_bin_size=0.015) 
    
    # Plot the result
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plot raw data faintly in the background
    folded_lc.scatter(ax=ax, color='grey', alpha=0.1, label='Unbinned Data')
    
    # Plot clean, binned data over the top
    binned_lc.scatter(ax=ax, color='blue', alpha=0.8, s=20, label='Binned Data (Kepler-186f)')
    
    # The "Zoom Lens": Focusing tightly on the transit event
    ax.set_xlim(-0.2, 0.2)     # Zoom in to roughly 5 hours before and after the transit
    ax.set_ylim(0.995, 1.005)  # Zoom in vertically to see the 0.04% depth
    
    ax.set_title('Exoplanet Transit Signal: Kepler-186f (Earth-Sized)')
    ax.legend()
    
    print("Success! Saving plot to your folder...")
    plt.savefig('kepler186f_transit_zoomed.png', dpi=300, bbox_inches='tight')
    print("Done! Look for 'kepler186f_transit_zoomed.png' in your project folder.")

if __name__ == "__main__":
    main()
    
