
import investpy
import pandas as pd
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

"""This Python project retrieves and formats information related to currency crosses and economic events from the InvestPy API.
 The program obtains a list of main currency crosses, 
 formats them with their exchange rates against the USD,
  retrieves US economic events data for the past month and creates an HTML file that displays this information in a table format.
"""

def get_main_currency_crosses():
    df = investpy.get_currency_crosses_overview("USD", n_results = 1000)
    main_crosses = ['EUR/USD', 'USD/JPY', 'USD/RUB']
    main_crosses_result = df[df['symbol'] .isin(main_crosses)]
    unique_main_crosses_result = main_crosses_result.drop_duplicates(subset=['symbol', 'name'], keep='first')
    return unique_main_crosses_result

currency_sumbols = {
    "EUR/USD" :" EUR",
    "USD/JPY" :" JPY",
    "USD/RUB" :" RUB"
}
def format_main_currency_crosses ( unique_main_crosses_result ):
    for index, row in unique_main_crosses_result.iterrows():
        symbol_pair = row['symbol']
        currency_symbol_pair = currency_sumbols[symbol_pair]
        if symbol_pair.endswith('/USD') == True:
            unique_main_crosses_result.loc[index, '1$='] = f"1$ = {round( 1/ row['bid'] ,2)}{currency_symbol_pair}"
        else:
            unique_main_crosses_result.loc[index, '1$='] = f"1$ = {round(row['bid'] ,2)}{currency_symbol_pair}"
    unique_main_crosses_result = unique_main_crosses_result[['1$=']]
    print(unique_main_crosses_result)
    return unique_main_crosses_result

def get_economic_calendar( from_date , to_date , list_of_event_names):
    calendar = investpy.news.economic_calendar(countries=['US'], from_date=from_date, to_date=to_date)
    calendar = calendar[calendar['zone'] == 'united states']
    calendar = calendar[['date', 'event', 'actual', 'forecast', 'previous']]
    event_df_list = []
    for event_name in list_of_event_names:
        event_df = calendar[calendar['event'].str.startswith(event_name)]
        event_df_list.append(event_df)

    return pd.concat(event_df_list)

data = {'event' :['JOLTs Job Openings  (Jun)', 'Unemployment Rate  (Jul)', 'CPI (YoY)  (Jul)', 'GDP (QoQ)  (Q2)'],
        'event_description' :
            ['JOLTS defines Job Openings as all positions that are open (not filled) on the last business day of the month. A job is open only if it meets all of the following conditions: A specific position exists and there is work available for that position.',
                             'The U-3 unemployment rate represents the number of unemployed people who are actively seeking a job',
                             'The Consumer Price Index (CPI) is a measure of the average change overtime in the prices paid by urban consumers for a market basket of consumer goods and services',
                             'Gross domestic product (GDP), total market value of the goods and services produced by a countrys economy during a specified period of time']}

df_events = pd.DataFrame(data)

def add_event_description(needed_events, data):
    df_info = pd.DataFrame(data)
    return pd.merge(
        left=needed_events,
        right=df_info,
        how="left",
        on='event',
    )

def writing_html (total_event_df, currency_crosses_df):
    file_html = open("demo.html", "w")
    file_html.write(currency_crosses_df.to_html().replace('class="dataframe"', 'class="dataframe" align="center"'))
    for index, row in total_event_df.iterrows():
        file_html.write(f"<h3> {row['event_description']} </h3>")
        html_dataframe = pd.DataFrame (row[['date' ,'actual' ,'forecast', 'previous']])
        html_dataframe.columns = [row['event']]
        file_html.write(html_dataframe.to_html().replace('class="dataframe"', 'class="dataframe" align="center"'))
    file_html.close()

def main_function():
    currency_crosses = get_main_currency_crosses()
    formatted_currency_crosses = format_main_currency_crosses(currency_crosses)
    d = datetime.today() - timedelta(days=30)
    from_date = d.strftime("%d/%m/%Y")
    d2 = datetime.today()
    to_date = d2.strftime("%d/%m/%Y")
    economic_calendar = get_economic_calendar(from_date=from_date,
                                              to_date=to_date,
                                              list_of_event_names=
                                              ('JOLTs', 'Unemployment Rate', 'CPI (YoY)', 'GDP (QoQ'))
    adding_description = add_event_description(needed_events=economic_calendar, data=data)
    writing_html(adding_description, formatted_currency_crosses)

main_function()
