import pandas as pd
import Process_Files.comm as comm
import os
import helper

def charge_group_by_site_id(df):
    df_grouped = df.groupby(comm.MonthlyBillReviewColumns.SITE_ID_2.display_name)
    
    sum_charge_by_site_id = df_grouped[comm.MonthlyBillReviewColumns.CHARGE_AMOUNT_EX_TAX.display_name].sum()
    df = pd.DataFrame(sum_charge_by_site_id)
    df = df.reset_index()
    
    return df


def get_df_charge_by_site_id(df):
    cols =[comm.MonthlyBillReviewColumns.SITE_ID_2.display_name,comm.MonthlyBillReviewColumns.CHARGE_AMOUNT_EX_TAX.display_name]
   # path = os.path.join(comm.folder,comm.file_bill_charge_detail)
   # df = helper.get_df_from_excel(path,comm.sheet_name,cols)
    df = df[cols]
    df_charged = charge_group_by_site_id(df)
    return df_charged

def get_df_review_expected_template():
    #path = os.path.join(comm.folder,comm.file_reiew_expected_template)
    file_id = helper.get_file_id_by_name(comm.file_reiew_expected_template)
    #df = helper.excel_2_df(path, comm.sheet_name_expected_charge_template)
    df = helper.file_id_2_df(file_id, comm.sheet_name_expected_charge_template)
    df = df.drop(columns=[comm.MonthlyBillReviewColumns.LAST_MONTHS_COST.display_name,
                          comm.MonthlyBillReviewColumns.THIS_MONTHS_COST.display_name])
    return df

def get_merged_df(df):
    df_charge = get_df_charge_by_site_id(df)
    df_review_expected_template = get_df_review_expected_template()
    merged_df = pd.merge(df_charge, df_review_expected_template,
                         right_on = comm.MonthlyBillReviewColumns.SITE_ID.display_name,
                         left_on= comm.MonthlyBillReviewColumns.SITE_ID_2.display_name,
                         how='left')
    merged_df.loc[merged_df[comm.MonthlyBillReviewColumns.SITE_ID_2.display_name].notna(),
                  comm.MonthlyBillReviewColumns.DIFF.display_name] \
    = round(merged_df[comm.MonthlyBillReviewColumns.CHARGE_AMOUNT_EX_TAX.display_name] - merged_df[comm.MonthlyBillReviewColumns.EXPECTED_MONTHLY_COST.display_name],2)

    merged_df[comm.MonthlyBillReviewColumns.COST_CENTER.display_name] \
    = merged_df[comm.MonthlyBillReviewColumns.COST_CENTER.display_name].astype(object)

    return merged_df

def custom_sort_key(row):
    v = row[comm.MonthlyBillReviewColumns.DIFF.display_name]
    if pd.isna(v):
        charge_amount = row[comm.MonthlyBillReviewColumns.CHARGE_AMOUNT_EX_TAX.display_name]
        return (0,(0,-charge_amount) if charge_amount>=0 else (1,charge_amount))
    elif v > 0:
        return (1, -v)
    elif v < 0:
        return (2, v)
    elif v ==0:
        return (3, 0)

def select_reorder_cols(df):
    cols = [comm.MonthlyBillReviewColumns.SITE_ID_2.display_name,
            comm.MonthlyBillReviewColumns.SITE.display_name,
            comm.MonthlyBillReviewColumns.COST_CENTER.display_name,
            comm.MonthlyBillReviewColumns.EXPECTED_MONTHLY_COST.display_name,
            comm.MonthlyBillReviewColumns.CHARGE_AMOUNT_EX_TAX.display_name,
            comm.MonthlyBillReviewColumns.DIFF.display_name,
            comm.MonthlyBillReviewColumns.BILLING_COMMENT.display_name]
    df = df[cols]
    return df



def transform_merged_df(merged_df):
    merged_df['sort_key'] = merged_df.apply(custom_sort_key, axis=1)
    merged_df_sorted = merged_df.sort_values(by = ['sort_key',comm.MonthlyBillReviewColumns.SITE_ID_2.display_name],
                                         ascending=[True, True])
    merged_df_sorted = merged_df_sorted.drop(columns=['sort_key'])

    merged_df_ajusted = select_reorder_cols(merged_df_sorted)
    return merged_df_ajusted

def compare_charge_with_expected(df):
    merged_df = get_merged_df(df)
    merged_df_ajusted = transform_merged_df(merged_df)

    return merged_df_ajusted


