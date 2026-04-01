import lightkurve as lk
import matplotlib.pyplot as plt

def main():
    print("Searching for Kepler-186 data...")
    search_result = lk.search_lightcurve('Kepler-186', author='Kepler')
    
    # Grab the first 8 datasets
    search_result = search_result[0:8]
    
    print(f"Downloading {len(search_result)} datasets...")
    lc_collection = search_result.download_all()
    
    print("Cleaning and flattening data (Optimized)...")
    clean_lcs = []
    for lc in lc_collection:
        # ADDED: .remove_outliers() to delete the cosmic ray glitches
        clean_lc = lc.remove_nans().remove_outliers().flatten(window_length=401)
        clean_lcs.append(clean_lc)
        
    print("Stitching the clean datasets together...")
    flat_lc = lk.LightCurveCollection(clean_lcs).stitch()
    
    # Kepler-186f Parameters
    planet_period = 129.944  
    transit_epoch = 168.8    
    
    print("Folding light curve...")
    folded_lc = flat_lc.fold(period=planet_period, epoch_time=transit_epoch)
    
    print("Binning data to highlight the tiny transit dip...")
    # Increased bin size slightly to make the line smoother
    binned_lc = folded_lc.bin(time_bin_size=0.05) 
    
    # Plot the result
    fig, ax = plt.subplots(figsize=(10, 5))
    folded_lc.scatter(ax=ax, color='grey', alpha=0.1, label='Unbinned Data')
    binned_lc.scatter(ax=ax, color='blue', alpha=0.8, s=20, label='Binned Data (Kepler-186f)')
    
    # ADDED: Zooming in the axes to actually see the planet!
    ax.set_xlim(-2, 2)         # Zoom in to just 2 days before and after the transit
    ax.set_ylim(0.995, 1.005)  # Zoom in tightly on the Y-axis to see the 0.04% dip
    
    ax.set_title('Exoplanet Transit Signal: Kepler-186f (Earth-Sized)')
    ax.legend()
    
    print("Success! Saving plot to your folder...")
    plt.savefig('kepler186f_transit.png', dpi=300, bbox_inches='tight')
    print("Done! Look for 'kepler186f_transit.png' in your project folder.")

if __name__ == "__main__":
    main()
    
