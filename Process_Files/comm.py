from enum import Enum
class BillChargeDetailColumns(Enum):
    # for loading from excel
    COST_CENTER = ('Cost Centre','keep')
    SALES_ORDER = ('Sales Order #','keep')
    CHARGE_DESCRIPTION = ('Charge Description','keep')
    CHARGE_AMOUNT_EX_TAX = ('Charge Amount (ex Tax)','keep')
    FROM = ('From','keep')

    # for adding to cols
    LLDGCODE= ('LLDGCODE', 'add') # to generate
    LNARR1 = ('LNARR1','add') # to generate

    def __init__(self,display_name, group):
        self.display_name = display_name
        self.group = group
    
    @property
    def is_keep(self):
        return self.group == 'keep'
    
class MonthlyBillReviewColumns(Enum):
    SITE = ('Site', 'keep')
    SITE_ID = ('Site ID','keep')
    COST_CENTER = ('Cost Centre','keep')
    EXPECTED_MONTHLY_COST = ('Expected Monthly Cost','keep')
    LAST_MONTHS_COST= ('Last Months Cost','keep')
    THIS_MONTHS_COST = ('This months cost','keep')
    BILLING_COMMENT = ('Billing Comment','keep')

    DIFF = ('charged - expected','add')
    CHARGE_AMOUNT_EX_TAX = ('Charge Amount (ex Tax)','add')
    SITE_ID_2 = ('Site Id','add')

    def __init__(self,display_name, group):
        self.display_name = display_name
        self.group = group
    
    @property
    def is_keep(self):
        return self.group == 'keep'

folder = 'Orro_Bills'
file_bill_charge_detail = '1071219.xlsx'
sheet_name = 'Bill Charge Detail'

file_reiew_expected_template = 'Orro Monthly Billing Review Aug 2024.xlsx'
sheet_name_expected_charge_template = 'Carriage Reconcilliation'


format_1 = '%d/%m/%Y'
format_2 = "%B %Y"