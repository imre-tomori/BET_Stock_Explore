from datetime import datetime, timedelta

### Download section

# Security sections:
    # Indexek: ['Indices']
    # Azonnali piac: ['Részvények Prémium', 'Részvények Standard', 'ETF', 'Investment Certifikát','Turbo Certifikát és Warrant']
    # Származékos piac: -
    # Árupiac: -
    # Béta piac: -

# Securities to inclde in the download
security_categories = (
    {'Indexek': ['Indices'],
     'Azonnali Piac': ['Részvények Prémium', 'Részvények Standard', 'ETF', 'Investment Certifikát', 'Turbo Certifikát és Warrant']}
)

# Site parameters to use on BET.hu per security category
BET_parameters = ( {
    'Indexek': ["index","select2-indexCategoryInput-container","select2-indexCategoryInput-results","indexButton"],
    'Azonnali Piac': ["prompt","select2-promptCategoryInput-container","select2-promptCategoryInput-results","promptButton"]
} )

# Download range
end_date_orig = datetime.today() - timedelta(days=1)
start_date_orig = end_date_orig - timedelta(days=4*365) # 4 years
end_date, start_date = end_date_orig.strftime("%Y.%m.%d."), start_date_orig.strftime("%Y.%m.%d.")

### Calculation parameters

# Highlights stock if there is a signal in the last x days
lookback_range = 180

# Set up indicator lengths
#MA_lengths = {'EMA_0': 89, 'EMA_1': 100}
#LR_lengths = {'LR_0':55,'LR_1':89,'LR_2':100}
MA_lengths = {'EMA_0': 144, 'EMA_1': 169}
LR_lengths = {'LR_0':89,'LR_1':144,'LR_2':169}


