"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})

    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df1 = regions[['code', 'name']]
    df1.columns = ['code_reg', 'name_reg']

    df2 = departments[['code', 'region_code', 'name']]
    df2.columns = ['code_dep', 'code_reg', 'name_dep']

    return pd.merge(df1, df2, on='code_reg')


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code']\
                                        .apply(lambda x : x.zfill(2))
    df_merged = pd.merge(regions_and_departments,
                        referendum,
                        left_on='code_dep',
                        right_on='Department code')

    return df_merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df_groupby = referendum_and_areas.groupby(['code_reg', 'name_reg'])
    return df_groupby.agg({'Registered': "sum",
                            "Abstentions": "sum",
                            "Null": "sum",
                            "Choice A": "sum",
                            "Choice B": "sum"}).reset_index('name_reg')


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geo_df = gpd.read_file("data/regions.geojson")[['code', 'geometry']]
    geo_df.columns = ['code_reg', 'geometry']
    geo_df.set_index('code_reg')
    df_merged = pd.merge(referendum_result_by_regions, geo_df, on='code_reg')

    df_merged['ratio'] = df_merged['Choice A'] / (df_merged['Registered'] -
                                                    df_merged['Abstentions'] -
                                                    df_merged['Null']
                                                )

    geo_ratio = gpd.GeoDataFrame(df_merged)
    geo_ratio.plot(column="ratio", legend=True)
    return geo_ratio


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
