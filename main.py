import lightkurve as lk
import matplotlib.pyplot as plt

def main():
    print("Searching for Kepler-186 data...")
    # 1. Search for all available Kepler data for Kepler-186
    search_result = lk.search_lightcurve('Kepler-186', author='Kepler')
    
    print(f"Found {len(search_result)} datasets. Downloading and stitching...")
    # 2. Download all quarters and stitch them into one continuous light curve
    # This is necessary because the planet's period (~130 days) is longer than a single Kepler Quarter
    lc_collection = search_result.download_all()
    lc = lc_collection.stitch()
    
    # 3. Preprocess: Remove NaNs and flatten to remove long-term stellar variations
    print("Flattening the light curve...")
    clean_lc = lc.remove_nans()
    flat_lc = clean_lc.flatten(window_length=401)
    
    # 4. Fold the light curve
    # Kepler-186f Parameters
    planet_period = 129.944  # Orbital period in days
    transit_epoch = 168.8    # Approximate reference epoch for folding
    
    print("Folding light curve...")
    folded_lc = flat_lc.fold(period=planet_period, epoch_time=transit_epoch)
    
    # 5. Bin the folded data
    # Because Kepler-186f is Earth-sized, its transit dip is extremely small.
    # Binning averages nearby points together to reduce noise and reveal the signal.
    print("Binning data to highlight the tiny transit dip...")
    binned_lc = folded_lc.bin(time_bin_size=0.01)
    
    # 6. Plot the result
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plot the raw folded data faintly in the background
    folded_lc.scatter(ax=ax, color='grey', alpha=0.1, label='Unbinned Data')
    
    # Plot the clean, binned data over the top
    binned_lc.scatter(ax=ax, color='blue', alpha=0.8, s=20, label='Binned Data (Kepler-186f)')
    
    ax.set_title('Exoplanet Transit Signal: Kepler-186f (Earth-Sized)')
    ax.legend()
    
    print("Displaying plot. Close the plot window to end the script.")
    plt.show()

# This is the section that was missing the indentation!
if __name__ == "__main__":
    main()
