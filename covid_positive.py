import os
import time
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates

start = time.process_time()

# Choose which dataset to parse (full, 10k, 100)
# 100 rows
# csv_file = '/home/nobalai/Downloads/state_linelist_20210215-sample.csv'
# 10k rows
# csv_file = '/home/nobalai/Downloads/state_linelist_20210215-sample-10k.csv'
# 1.8 million rows
csv_file = '/home/nobalai/Downloads/state_linelist_20210215.csv'

COUNTY = 'County'
CHART_DATE = 'ChartDate'
CHART_DATE_BINS = 'ChartDate_bins'
CHART_DATE_BINS_COUNT = 'ChartDate_bins_count'
PER_MILLION_POPULATION = 'PerMillionPopulation'

ten_thousand = 10_000
one_million = 1_000_000
SCALE_FACTORS = {
	ten_thousand: '10k',
	one_million: '1M'
}

# Configurable variables
MIN_POPULATION = 750000
SCALE_FACTOR = one_million


def florida_county_population_map():
	florida_counties_dataset_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Florida_Demographic_Information.csv')
	florida_counties_df = pd.read_csv(florida_counties_dataset_file, usecols=['NAMELSAD', 'TotalPopul'])
	
	map = {}
	for index, row in florida_counties_df.iterrows():
		name = row['NAMELSAD'].replace(' County', '')
		map[name] = row['TotalPopul']

	return map


def setup_plot():
	fig, ax = plt.subplots()
	ax.set_title('COVID Positive Florida County (' + str(MIN_POPULATION) + ' or higher pop.)')
	ax.set_ylabel('Per ' + SCALE_FACTORS[SCALE_FACTOR] +  ' Population')
	ax.set_xlabel('By Binned Date Ranges')

	return fig, ax

def plot_by_county(by_county, ax):
	# Limit total counties printed out
	max_count = 70  # This dataset has 68
	
	# Aggregate by county, sum into the time bins above.
	
	for county, group in by_county:
		county_population = county_population_map.get(county)
		
		if max_count > 1 and county_population and county_population > MIN_POPULATION:
			value = group[CHART_DATE_BINS].value_counts(sort=False)
			
			# Scale the count based on county population
			per_million_population = value.transform(lambda v: SCALE_FACTOR * v / county_population)
			
			per_million_population.plot.line(
				x=CHART_DATE_BINS,
				# y=CHART_DATE_BINS_COUNT,
				ax=ax,
				label=county,
			)
		max_count -= 1


county_population_map = florida_county_population_map()

df = pd.read_csv(csv_file, usecols=[COUNTY, CHART_DATE], parse_dates=[CHART_DATE])

# The range of the dataset, manually defined rather than programatically found
date_range = pd.date_range('2020-03-10', '2021-02-10', freq='1D')

# Add to the time (RangeIndex) bin
df[CHART_DATE_BINS] = pd.cut(df[CHART_DATE], bins=date_range)

# by_county_1 = df.value_counts(subset=[COUNTY, CHART_DATE_BINS])
# df.set_index(CHART_DATE_BINS)

by_county = df.groupby(COUNTY)

# group = by_county.get_group('Palm Beach')
fig, ax = setup_plot()

plot_by_county(by_county, ax)

counties = df[COUNTY].unique()

plt.ylim(0)
plt.legend()
plt.show()

print("In " + str(time.process_time() - start))