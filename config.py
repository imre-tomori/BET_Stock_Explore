from datetime import datetime, timedelta

### Download section

# Security sections:
    # Indexek: ['Indices']
    # Azonnali piac: ['Részvények Prémium', 'Részvények Standard', 'ETF', 'Investment Certifikát','Turbo Certifikát és Warrant']
    # Származékos piac: -
    # Árupiac: -
    # Béta piac: -
    
security_categories = (
    {'Indexek': ['Indices'],
     'Azonnali Piac': ['Részvények Prémium', 'Részvények Standard', 'ETF', 'Investment Certifikát','Turbo Certifikát és Warrant']}
)
# 'Turbo Certifikát és Warrant' - this one breaks the download when lookin for more than 14 months of data, need to request separetly

# Site parameters to use on BET.hu per security category
BET_parameters = ( {
    'Indexek': ["index","select2-indexCategoryInput-container","select2-indexCategoryInput-results","indexButton"],
    'Azonnali Piac': ["prompt","select2-promptCategoryInput-container","select2-promptCategoryInput-results","promptButton"]
} )

# Download range
end_date_orig = datetime.today() - timedelta(days=1)
start_date_orig = end_date_orig - timedelta(days=2*365) # 2 years
end_date, start_date = end_date_orig.strftime("%Y.%m.%d."), start_date_orig.strftime("%Y.%m.%d.")

### Calculation parameters
lookback_range = 90
MA_lengths = {'EMA_144': 144, 'EMA_169': 169}
LR_lengths = {'LR_89':89,'LR_144':144,'LR_169':169}