import lightkurve as lk
import matplotlib.pyplot as plt

def main():
    print("fetching kepler-186 data...")
    res = lk.search_lightcurve('Kepler-186', author='Kepler')
    
    print(f"downloading {len(res)} datasets (should be fast if cached)...")
    lcs = res.download_all()
    
    print("cleaning and flattening (this takes a sec)...")
    clean_list = []
    for lc in lcs:
        # Removing nans, outliers, and flatten the wiggles (Otherwise too much data and the code crashes)
        clean = lc.remove_nans().remove_outliers().flatten(window_length=401)
        clean_list.append(clean)
        
    print("stitching it all together...")
    stitched = lk.LightCurveCollection(clean_list).stitch()
    
    # kepler 186f parameters
    p = 129.944  
    epoch = 172.15  # modified offset to center the dip perfectly at 0, we first ran without any such parameter observed where the dip was seen and have modified it.
    folded = stitched.fold(period=p, epoch_time=epoch)
    
    # bin down the noise. 0.015 days is about 21 mins, we took 0.1 before but now as we are taking a shorter interval of just 9 hours we have reduced the size of the bin so we can get enough bin points to see a clear pattern.
    binned = folded.bin(time_bin_size=0.015) 
    
    # setting up the plot
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # plot raw data faintly in the background using 90% transperency
    folded.scatter(ax=ax, color='grey', alpha=0.1, label='raw data')
    
    # plot clean, binned data over the top much darker, 20% transparency
    binned.scatter(ax=ax, color='blue', alpha=0.8, s=20, label='binned')
    
    # zoom camera right into the transit window, we had taken the standard ranges of -1 to 1 before however the x axis was too big in this and we were unable to see any clear pattern.
    ax.set_xlim(-0.2, 0.2)     
    ax.set_ylim(0.995, 1.005)  
    
    ax.set_title('Kepler-186f Transit Fit')
    ax.legend(loc='upper right')
    
    # plt.show() # my cpu crashes or takes too long, saving it instead, will be displayed in the file location and i have uploaded all results to READ ME
    
    print("saving plot...")
    plt.savefig('kepler186f_transit_zoomed.png', dpi=300, bbox_inches='tight')
    print("done!")
    #thank you, we can see a very small dip, or tending to it between 0 and -0.01, despite all this we do not have a perfect graph and values as our estimation technique 'savitzky-golay smoothneing' is not exact, actual scientits used much more complicated gaussian and other smoothneing and estimation techniques.

if __name__ == "__main__":
    main()
    
