import pandas as pd
import numpy as np

main = pd.read_csv('global20_main.csv')
offices = pd.read_csv('global20_offices.csv')
attorneys = pd.read_csv('global20_attorneys.csv')
new_hires = pd.read_csv('global20_newhires.csv')
revenue = pd.read_csv('global20_revenue.csv')
probono = pd.read_csv('global20_probono.csv')
matters = pd.read_csv('global20_matters.csv')

def convert_to_numeric(df, column):
    df[column] = df[column].str.replace(',', '').astype('int')   

convert_to_numeric(main, 'Headcount_GlobalHeadcount')

ids = list(main.Global202023_Id)

p_offices = pd.DataFrame(columns=['Global202023_Id', 'Country_Office_HQ', 'NumberOfOffices'])
for i in ids:
    test = offices.loc[offices['Global202023_Id'] == i]
    most_offices = max(test.NumberOfOffices)
    row_most_offices = test.loc[test['NumberOfOffices'] == most_offices]
    row_most_offices = row_most_offices[['Global202023_Id', 'Country', 'NumberOfOffices']]
    row_most_offices = row_most_offices.rename(columns={"Country": "Country_Office_HQ"})
    p_offices = p_offices.append(row_most_offices)

main = pd.merge(main, p_offices, on='Global202023_Id', how='inner')

main['perc_offices_outside_HQ'] = (main.Offices_GlobalOffices - main.NumberOfOffices) / main.Offices_GlobalOffices

convert_to_numeric(attorneys, 'AttorneyHeadcount')

p_attorneys = pd.DataFrame(columns=['Global202023_Id', 'Country_Attorney_HQ', 'AttorneyHeadcount'])
for i in ids:
    test = attorneys.loc[attorneys['Global202023_Id'] == i]
    most_attorneys = max(test.AttorneyHeadcount)
    row_most_attorneys = test.loc[test['AttorneyHeadcount'] == most_attorneys]
    row_most_attorneys = row_most_attorneys[['Global202023_Id', 'Country', 'AttorneyHeadcount']]
    row_most_attorneys = row_most_attorneys.rename(columns={"Country": "Country_Attorney_HQ"})
    p_attorneys = p_attorneys.append(row_most_attorneys)

main = pd.merge(main, p_attorneys, on='Global202023_Id', how='inner')

main['perc_attorneys_outside_HQ'] = (main.Headcount_GlobalHeadcount - main.AttorneyHeadcount) / main.Headcount_GlobalHeadcount

main['perc_offices_outside_HQ'] = (main.Offices_GlobalOffices - main.NumberOfOffices) / main.Offices_GlobalOffices

main['Offices_Countries'][0]
main.at[0, 'Offices_Countries'] = 'Austria, Belgium, Brunei, China, Czech Republic, Estonia, Finland, France, Germany, Hungary, Iraq, Ireland, Italy, Jordan, Latvia, Lithuania, Luxembourg, Mauritius, Netherlands, Poland, Qatar, Romania, Russia, Saudi Arabia, Singapore, Slovakia, South Africa, Spain, Sweden, Switzerland, Tunisia, United Arab Emirates, United Kingdom, United States'

main['Offices_Countries'][2]
main.at[2, 'Offices_Countries'] = 'United Kingdom, Germany, Netherlands, US, China, France, Belgium, Luxembourg, Spain, Australia, UAE, Italy, Singapore, Poland, South Africa, Indonesia, Thailand, Czech Republic, Morocco, Slovakia, Russia, Japan, Vietnam, Turkey, Hungary, Qatar, Brazil, South Korea, Myanmar, Saudi Arabia'

main['Offices_Countries'] = main['Offices_Countries'].str.split(',')

i = 0
countries_count = []
for x in main['Offices_Countries']:
    count = len(main['Offices_Countries'][i])
    countries_count.append(count)
    i += 1
main['Count_Countries_Offices'] = countries_count

firm_names = ['Eversheds Sutherland', 'Reed Smith', 'Allen & Overy']

main.Firmname = firm_names

firmnames = main[['Global202023_Id', 'Firmname']]

matters = pd.merge(matters, firmnames, on='Global202023_Id', how='inner')

matters.at[54, 'NameOfClient'] = 'Societe Generale'

matters.to_csv('matters_for_article_counts.csv')

matters = pd.read_csv('matters_with_counts.csv')

matters.drop(matters.columns[[0, 1]], axis=1, inplace=True)

breadth = pd.DataFrame(columns=['Global202023_Id', 'article_total'])
for i in ids:
    temp = matters.loc[matters['Global202023_Id'] == i]

    temp['article_total'] = temp['article_counts'].sum()
    
    temp = temp.reset_index(drop=True)
    
    temp = temp.iloc[:1]

    abbr_temp = temp[['Global202023_Id', 'article_total']]

    breadth = breadth.append(abbr_temp)

main = pd.merge(main, breadth, on='Global202023_Id', how='inner')

matters['FinancialValue'] = matters['FinancialValue'].str.replace('$', '').str.replace(',', '').astype(float)

matters['FinancialValue'] = matters['FinancialValue'].fillna(0)

depth1 = pd.DataFrame(columns=['Global202023_Id', 'deal_total'])
for i in ids:
    temp = matters.loc[matters['Global202023_Id'] == i]

    temp['deal_total'] = temp['FinancialValue'].sum()
    
    temp = temp.reset_index(drop=True)
    
    temp = temp.iloc[:1]

    abbr_temp = temp[['Global202023_Id', 'deal_total']]

    depth1 = depth1.append(abbr_temp)

main = pd.merge(main, depth1, on='Global202023_Id', how='inner')

areas_final = []
areas_count_final = []
for i in ids:
    p_areas = []
    temp = matters.loc[matters['Global202023_Id'] == i]
    temp = temp.reset_index(drop=True)
    for x in temp.index:
        p_areas.append(temp['PracticeAreasInvolved'][x])
    areas = list(set(p_areas))
    areas_count = len(areas)
    areas_count_final.append(areas_count)        
    areas_final.append(areas)

main['areas_final'] = areas_final
main['areas_count_final'] = areas_count_final

main['% Attorneys Abroad Rank'] = main['perc_attorneys_outside_HQ'].rank(ascending=False)

main['% Offices Abroad Rank'] = main['perc_offices_outside_HQ'].rank(ascending=False)

main['Count_Countries_Offices_Rank'] = main['Count_Countries_Offices'].rank()

main['article_total_rank'] = main['article_total'].rank()

main['deal_total_rank'] = main['deal_total'].rank()

main['areas_count_final_total'] = main['areas_count_final'].rank(ascending=False)

main['depth_rank'] = (main['deal_total_rank'] + main['areas_count_final_total']) / 2

main['score'] = main['% Attorneys Abroad Rank'] + main['% Offices Abroad Rank'] + main['Count_Countries_Offices_Rank'] + main['article_total_rank'] + main['depth_rank']

main['rank'] = main['score'].rank()

main.to_csv('global20_ranking.csv')
