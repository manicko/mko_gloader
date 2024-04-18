import pathlib

base_file_name = 'data_file'
file_ext = '.txt'
file_number = 200
folder = 'test_data/ber/rt'
sample_text = f'hfbdfbksbfksdnfksdjnfksnf'
try:
    folder = pathlib.Path(folder)
except Exception as err:
    raise err
for i in range(1, file_number + 1):

    file_path = pathlib.Path.joinpath(folder, f'{base_file_name}_{i}{file_ext}')
    with open(file=file_path, mode='w') as f:
        f.write(sample_text)
