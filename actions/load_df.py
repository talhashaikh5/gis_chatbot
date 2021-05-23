import pandas as pd

# creating a data frame
df_abroad_general_prg = pd.read_csv("actions/abroad_general_prg.csv").applymap(str)
df_oman_disability_prg = pd.read_csv("actions/oman_disability_prg.csv").applymap(str)
df_public_oman_gen = pd.read_csv("actions/public_oman_gen.csv").applymap(str)
df_private_oman_gen = pd.read_csv("actions/private_oman_gen.csv").applymap(str)


def get_abroad_general_codes(country: str, stream: str) -> list:
    newdf = df_abroad_general_prg[
        (df_abroad_general_prg.country == str(country)) & (df_abroad_general_prg.stream == str(stream))
        ].codes
    return list(newdf)


def get_oman_disability_codes(disbality_type: str, institute: str) -> list:
    newdf = df_oman_disability_prg[
        (df_oman_disability_prg.disbality_type == str(disbality_type)) & (
                    df_oman_disability_prg.institute == str(institute))
        ].codes
    return list(newdf)


def get_public_oman_gen_codes(college: str, stream: str) -> list:
    newdf = df_public_oman_gen[
        (df_public_oman_gen.college == str(college)) & (df_public_oman_gen.stream == str(stream))
        ].codes
    return list(newdf)


def get_private_oman_gen_codes(college: str, stream: str) -> list:
    newdf = df_private_oman_gen[
        (df_private_oman_gen.college == str(college)) & (df_private_oman_gen.stream == str(stream))
        ].codes
    return list(newdf)


if __name__ == '__main__':
    print(get_public_oman_gen_codes("6", "1"))
