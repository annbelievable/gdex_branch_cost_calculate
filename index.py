import pandas as pd
import numpy as np

## this is to set the rows displayed when printing out 
pd.set_option('display.max_row', 100)

## variables that can be edited
doc_filename='./data.xlsx'
sheet_names=['VehicleRouteMovement','VehicleCost']
unknown_route_placeholder='EMPTY'

## open the excel sheet with sheet names
df = pd.read_excel(io=doc_filename, sheet_name=sheet_names)

## setting up each excel sheets
vehicle_routes_df=df['VehicleRouteMovement']
vehicle_cost_df=df['VehicleCost']





## PART 1, this is more like data engineering, making the dataframe so that its easier to handle

## drop unused columns
vehicle_routes_df.drop(['id'], axis=1, inplace=True)
vehicle_routes_df.drop(['date'], axis=1, inplace=True)

## fill the NaN with other value for ease of handling the dataframe
vehicle_routes_df['route_no']=vehicle_routes_df['route_no'].fillna(unknown_route_placeholder)
vehicle_routes_df['branch_code']=vehicle_routes_df['branch_code'].fillna(unknown_route_placeholder)

## drop empty columns
vehicle_routes_df.dropna( axis=1, inplace=True)

## merged the 2 sheets together based on the value in the column vehicle number
merged_df = pd.merge(vehicle_routes_df, vehicle_cost_df, on='vehicle_no')





## PART 2, this is where the actual logic calculation occurs

## find the cost for each row by dividing the mileage of the current row by the total mileage and multiply it with the total maintenance cost of that vehicle 
merged_df['cost'] = merged_df.apply(lambda row: round((row.mileage/row.total_mileage*row.maintenace_cost), 4), axis = 1)

non_empty_df = merged_df[merged_df.branch_code != unknown_route_placeholder]
empty_df = merged_df[merged_df.branch_code == unknown_route_placeholder]

## sum the cost for empty routes based on vehicle_no
empty_df['empty_cost'] = empty_df.groupby(['vehicle_no'])['cost'].transform(sum)

## dropping the other duplicated rows
empty_df = empty_df[['vehicle_no','empty_cost']].copy()

## remove columns that are not used
non_empty_df.drop(['route_no','mileage','total_mileage','maintenace_cost'], axis=1, inplace=True)

## sum the cost based on the group
grouped_df = non_empty_df.groupby(['vehicle_no','branch_code']).sum()

## resetting the index column which is the branch code
grouped_df.reset_index( inplace=True)

## merged the grouped df with the empty one
merged_df = pd.merge(grouped_df, empty_df, on='vehicle_no', how='left')

## fill NaN with 0 value
merged_df['empty_cost']=merged_df['empty_cost'].fillna(0)

## this get the number of branches that uses a vehicle
vehicle_branch_count=merged_df.groupby('vehicle_no').branch_code.nunique()

#print(vehicle_branch_count)
#print(vehicle_branch_count['BPB 4008'])
#print(vehicle_branch_count['BQP 3000'])

merged_df['divided_empty_cost'] = merged_df.apply(lambda row: round((row.empty_cost/vehicle_branch_count[row.vehicle_no]), 4), axis = 1)
merged_df['vehicle_branch_cost'] = merged_df.apply(lambda row: row.divided_empty_cost+row.cost, axis = 1)

merged_df['cost_incurred'] = merged_df.groupby(['branch_code'])['vehicle_branch_cost'].transform(sum)

## create a new dataframe with just the 2 columns needed
answer_df = merged_df[['branch_code','cost_incurred']].copy()

## remove the duplicated rows based on the branch_code
answer_df.drop_duplicates(subset='branch_code', keep='first', inplace=True)

## order the dataframe by the branch_code, this can be updated to be sorted by the cost_incurred
answer_df = answer_df.sort_values(by=['branch_code'], ascending=[True])

## reset the index
answer_df.reset_index(drop=True, inplace=True)

print(answer_df)