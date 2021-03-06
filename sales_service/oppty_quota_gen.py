import dateutil.parser

from data_generator import DataGenerator
from datetime import date

today = date.today()

def run(batch_id, source_file_name, output_file_name, reference_date=today):
    data_gen = DataGenerator()

    # load source file
    source_columns = ['External_Id__c','Name', 'UserRole.Name']
    data_gen.load_source_file(source_file_name, source_columns)

    data_gen.filter(lambda cv: 'RVP' not in cv['UserRole.Name'])
    data_gen.filter(lambda cv: 'CSM' not in cv['UserRole.Name']) # comes from Service


    data_gen.rename_column('External_Id__c', 'QuotaOwner_Id__c')
    data_gen.rename_column('Name', 'OwnerName__c')

    # generate id
    data_gen.add_formula_column('External_Id__c', formula=lambda: 'W_Quota.' + str(data_gen.current_row + 1))

    data_gen.duplicate_rows(24)

    def quota_formula():
        # first month of quarter = 300k
        # second month of quarter = 500k
        # third month of quarter = 500k
        quarter = data_gen.current_row % 3
        if quarter == 0:
            return 300000
        elif quarter == 1:
            return 750000
        else:
            return 500000
    data_gen.add_formula_column('QuotaAmount__c', quota_formula)


    current_year = reference_date.year
    last_year = current_year - 1
    def start_date_formula():
        user_row = data_gen.current_row % 24
        month = str((user_row % 12) + 1).zfill(2)
        day = '01'
        if user_row < 12:
            year = str(last_year)
        else:
            year = str(current_year)
        return dateutil.parser.parse(year + '-' + month + '-' + day).date()
    data_gen.add_formula_column('StartDate__c', start_date_formula)

    # add a UUID for each row that is created in this batch
    data_gen.add_constant_column('analyticsdemo_batch_id__c', batch_id)

    # apply transformations and write file
    data_gen.apply_transformations()
    data_gen.write(output_file_name, ['External_Id__c','QuotaOwner_Id__c', 'OwnerName__c', 'StartDate__c', 'QuotaAmount__c'])


if __name__ == "__main__":
    # execute only if running as a script
    run('1', 'data/output/User.csv', 'data/output/Quota.csv')
