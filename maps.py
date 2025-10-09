import geopandas as gpd
import pandas as pd
import elapid as ela
import matplotlib.pyplot as plt
import contextily as ctx

#data
locations = pd.read_csv(r"/Users/ruby/Documents/locations3.csv")


def plot_geodata(df, title="Map", markersize=10):

    geometry = ela.xy_to_geoseries(
        x=df['decimalLongitude'],
        y=df['decimalLatitude']
    )
    gdf = gpd.GeoDataFrame(
        df[['verbatimScientificName', 'year']],
        geometry=geometry,
        crs="EPSG:4326"
    ).to_crs(epsg=3857)

    fig, ax = plt.subplots(figsize=(8, 8))
    gdf.plot(
        column='verbatimScientificName',
        categorical=True,
        legend=True,
        markersize=markersize,
        cmap='tab10',
        alpha=0.8,
        ax=ax
    )
    ctx.add_basemap(ax, source=ctx.providers.Esri.WorldGrayCanvas)
    ax.set_title(title)
    plt.tight_layout()
    return fig


#full dataset
fig1 = plot_geodata(locations, title="Full dataset", markersize=10)

#CA only
california = locations[locations['stateProvince'] == 'California']
fig2 = plot_geodata(california, title="California", markersize=10)

oregon = locations[locations['stateProvince'] == 'Oregon']
fig4 = plot_geodata(oregon, title="Oregon", markersize=10)
#species only
#CA only
columbus = locations[locations['verbatimScientificName'] == "columbianus"]
fig3 = plot_geodata(columbus, title="Columbianus", markersize=10)

plt.show()