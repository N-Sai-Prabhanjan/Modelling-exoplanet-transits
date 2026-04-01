import lightkurve as lk
import matplotlib.pyplot as plt

def main():
    print("Searching for Kepler-186 data...")
    search_result = lk.search_lightcurve('Kepler-186', author='Kepler')
    
    # We removed the [0:8] limit! We are downloading ALL available data.
    print(f"Downloading {len(search_result)} datasets... (This should be fast using cached files)")
    lc_collection = search_result.download_all()
    
    print("Cleaning and flattening data (Optimized)...")
    clean_lcs = []
    for lc in lc_collection:
        # Flattening each quarter individually keeps the computer from freezing
        clean_lc = lc.remove_nans().remove_outliers().flatten(window_length=401)
        clean_lcs.append(clean_lc)
        
    print("Stitching the clean datasets together...")
    flat_lc = lk.LightCurveCollection(clean_lcs).stitch()
    
    # CORRECTED Kepler-186f Parameters
    planet_period = 129.944  
    transit_epoch = 170.4  # Updated to center the transit perfectly at 0
    
    print("Folding light curve...")
    folded_lc = flat_lc.fold(period=planet_period, epoch_time=transit_epoch)
    
    print("Binning data to highlight the tiny transit dip...")
    # Smaller bin size for higher resolution, now that we have more data!
    binned_lc = folded_lc.bin(time_bin_size=0.03) 
    
    # Plot the result
    fig, ax = plt.subplots(figsize=(10, 5))
    folded_lc.scatter(ax=ax, color='grey', alpha=0.1, label='Unbinned Data')
    binned_lc.scatter(ax=ax, color='blue', alpha=0.8, s=20, label='Binned Data (Kepler-186f)')
    
    # Zooming in
    ax.set_xlim(-2, 2)         
    ax.set_ylim(0.995, 1.005)  
    
    ax.set_title('Exoplanet Transit Signal: Kepler-186f (Earth-Sized)')
    ax.legend()
    
    print("Success! Saving plot to your folder...")
    plt.savefig('kepler186f_transit.png', dpi=300, bbox_inches='tight')
    print("Done! Look for 'kepler186f_transit.png' in your project folder.")

if __name__ == "__main__":
    main()
